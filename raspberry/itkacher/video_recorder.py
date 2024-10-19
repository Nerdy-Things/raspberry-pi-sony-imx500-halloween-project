import cv2
import os

class VideoRecorder:
    
    def record_video(self, input_folder: str, output_video_file: str):
        images = [img for img in os.listdir(input_folder) if img.endswith(".jpg") or img.endswith(".png")]
        images.sort()  

        first_image_path = os.path.join(input_folder, images[0])
        frame = cv2.imread(first_image_path)
        height, width, layers = frame.shape

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4 format
        video = cv2.VideoWriter(output_video_file, fourcc, 30.0, (width, height))  # 30.0 is the FPS

        for image in images:
            image_path = os.path.join(input_folder, image)
            frame = cv2.imread(image_path)
            video.write(frame)

        video.release()
