from itkacher.date_utils import DateUtils
import os

class FileUtils:

    def create_folders(path: str):
        if not os.path.exists(path):
            os.makedirs(path)
