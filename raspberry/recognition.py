import sys
from functools import lru_cache
import cv2
import numpy as np
import time

from itkacher.date_utils import DateUtils
from itkacher.file_utils import FileUtils

from picamera2 import MappedArray, Picamera2
from picamera2.devices import IMX500
from picamera2.devices.imx500 import (NetworkIntrinsics,
                                      postprocess_nanodet_detection)

import socket

last_detections = []

MESSAGE = b"BOO!"  # Message to send
PORT = 9341
MESSAGE_COOLDOWN = 10  # Cooldown time in seconds
last_message_time = 0  # To track the last time a message was sent

threshold = 0.55
iou = 0.65
max_detections = 10

def send_udp_message(message: bytes, port: int):
    global last_message_time
    current_time = time.time()  # Get the current time in seconds

    # Check if the cooldown period has passed
    if current_time - last_message_time < MESSAGE_COOLDOWN:
        print("Ignoring send request, still in cooldown period.")
        return  # Skip sending the message

    last_message_time = current_time

    interfaces = socket.getaddrinfo(host=socket.gethostname(), port=None, family=socket.AF_INET)
    allips = [ip[-1][0] for ip in interfaces]
    
    # Create the socket once
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    for ip in allips:
        try:
            print(f'sending on {ip}')
            # No need to bind the socket unless necessary
            sock.sendto(message, ("255.255.255.255", port))
        except Exception as e:
            print(f"Error sending message on {ip}: {e}")
    sock.close()

class Detection:
    def __init__(self, coords, category, conf, metadata):
        """Create a Detection object, recording the bounding box, category and confidence."""
        self.category = category
        self.conf = conf
        self.box = imx500.convert_inference_coords(coords, metadata, picam2)


def parse_detections(metadata: dict):
    """Parse the output tensor into a number of detected objects, scaled to the ISP out."""
    global last_detections
    bbox_normalization = intrinsics.bbox_normalization

    np_outputs = imx500.get_outputs(metadata, add_batch=True)
    input_w, input_h = imx500.get_input_size()
    if np_outputs is None:
        return last_detections
    if intrinsics.postprocess == "nanodet":
        boxes, scores, classes = \
            postprocess_nanodet_detection(outputs=np_outputs[0], conf=threshold, iou_thres=iou,
                                          max_out_dets=max_detections)[0]
        from picamera2.devices.imx500.postprocess import scale_boxes
        boxes = scale_boxes(boxes, 1, 1, input_h, input_w, False, False)
    else:
        boxes, scores, classes = np_outputs[0][0], np_outputs[1][0], np_outputs[2][0]
        if bbox_normalization:
            boxes = boxes / input_h

        boxes = np.array_split(boxes, 4, axis=1)
        boxes = zip(*boxes)

    last_detections = [
        Detection(box, category, score, metadata)
        for box, score, category in zip(boxes, scores, classes)
        if score > threshold
    ]
    return last_detections


@lru_cache
def get_labels():
    labels = intrinsics.labels

    if intrinsics.ignore_dash_labels:
        labels = [label for label in labels if label and label != "-"]
    return labels


def draw_detections(request, stream="main"):
    """Draw the detections for this request onto the ISP output."""
    detections = last_results
    if detections is None:
        return
    labels = get_labels()
    with MappedArray(request, stream) as m:
        for detection in detections:
            x, y, w, h = detection.box
            label = f"{labels[int(detection.category)]} ({detection.conf:.2f})"

            # Calculate text size and position
            (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            text_x = x + 5
            text_y = y + 15

            # Create a copy of the array to draw the background with opacity
            overlay = m.array.copy()

            # Draw the background rectangle on the overlay
            cv2.rectangle(overlay,
                          (text_x, text_y - text_height),
                          (text_x + text_width, text_y + baseline),
                          (255, 255, 255),  # Background color (white)
                          cv2.FILLED)

            alpha = 0.30
            cv2.addWeighted(overlay, alpha, m.array, 1 - alpha, 0, m.array)

            # Draw text on top of the background
            cv2.putText(m.array, label, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            # Draw detection box
            cv2.rectangle(m.array, (x, y), (x + w, y + h), (0, 255, 0, 0), thickness=2)

        if intrinsics.preserve_aspect_ratio:
            b_x, b_y, b_w, b_h = imx500.get_roi_scaled(request)
            color = (255, 0, 0)  # red
            cv2.putText(m.array, "ROI", (b_x + 5, b_y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            cv2.rectangle(m.array, (b_x, b_y), (b_x + b_w, b_y + b_h), (255, 0, 0, 0))


if __name__ == "__main__":

    model = "./imx500-models/imx500_network_ssd_mobilenetv2_fpnlite_320x320_pp.rpk"
    # model = "./imx500-models/imx500_network_efficientdet_lite0_pp.rpk"
    # model = "./imx500-models/imx500_network_nanodet_plus_416x416.rpk"
    # model = "./imx500-models/imx500_network_nanodet_plus_416x416_pp.rpk"

    # This must be called before instantiation of Picamera2
    imx500 = IMX500(model)
    intrinsics = imx500.network_intrinsics
    if not intrinsics:
        intrinsics = NetworkIntrinsics()
        intrinsics.task = "object detection"
    elif intrinsics.task != "object detection":
        print("Network is not an object detection task", file=sys.stderr)
        exit()

    # Defaults
    if intrinsics.labels is None:
        with open("assets/coco_labels.txt", "r") as f:
            intrinsics.labels = f.read().splitlines()
    intrinsics.update_with_defaults()

    picam2 = Picamera2(imx500.camera_num)

    # Night settings
    controls = {
        "Brightness": 0.25,  # Range is typically from -1.0 to 1.0
        "Contrast": 1.0,    # Increase for sharper contrast in low light
        "ExposureTime": 150000,
        "AnalogueGain": 32.0,
    }

    # Day settings
    controls = {}

    config = picam2.create_preview_configuration(
        controls = controls, 
        buffer_count=12
    )

    imx500.show_network_fw_progress_bar()
    picam2.start(config, show_preview=False)

    if intrinsics.preserve_aspect_ratio:
        imx500.set_auto_aspect_ratio()

    last_results = None
    picam2.pre_callback = draw_detections
    print("Started!")
    while True:
        last_results = parse_detections(picam2.capture_metadata())
        # Record file to SD card
        data_folder = f"../data/images/{DateUtils.get_date()}/"
        try:
            picam2.capture_file(f"{data_folder}/{DateUtils.get_time()}.jpg")
        except:
            FileUtils.create_folders(data_folder)

        if (len(last_results) > 0):
            for result in last_results:
                if result.category == 0: 
                    print("Person detected, sending BOO!")
                    send_udp_message(MESSAGE, PORT)
