import os

from itkacher.camera_capture import CameraCapture
from itkacher.image_recognition import ImageRecognotion
from itkacher.image_cropper import ImageCropper
from itkacher.date_utils import DateUtils

def build_image_path():
    origin_folder_path = f"data/{DateUtils.get_date()}/images/origin"
    if not os.path.exists(origin_folder_path):
        os.makedirs(origin_folder_path)

    cropped_folder_path = f"data/{DateUtils.get_date()}/images/cropped"
    if not os.path.exists(cropped_folder_path):
        os.makedirs(cropped_folder_path)

    recognized_folder_path = f"data/{DateUtils.get_date()}/images/recognized"
    if not os.path.exists(recognized_folder_path):
        os.makedirs(recognized_folder_path)

    return origin_folder_path, cropped_folder_path, recognized_folder_path

if __name__ == '__main__':
    camera = CameraCapture()
    model = "itkacher/model/yolov8n.onnx"
    recognition = ImageRecognotion(model)
    cropper = ImageCropper()

    while True:
        origin_folder_path, cropped_folder_path, recognized_folder_path = build_image_path()

        image_name = f"{DateUtils.get_time()}.jpg"
        
        captured_image_path = os.path.join(origin_folder_path, image_name)
        captured_image_path = camera.capture_image(captured_image_path)

        cropped_image_path = os.path.join(cropped_folder_path, image_name)
        cropper.crop(captured_image_path, cropped_image_path)

        recognized_image_path = os.path.join(recognized_folder_path, image_name)
        recognized = recognition.recognise(cropped_image_path, recognized_image_path)

        print(f"recognized {recognized}")
