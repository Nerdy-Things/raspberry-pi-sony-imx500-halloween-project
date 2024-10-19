from datetime import datetime

class DateUtils:
    @staticmethod
    def get_date() -> str:
        current_datetime = datetime.now()
        return current_datetime.strftime("%Y-%m-%d")

    @staticmethod
    def get_time() -> str:
        current_datetime = datetime.now()
        return current_datetime.strftime("%H:%M:%S.%f")