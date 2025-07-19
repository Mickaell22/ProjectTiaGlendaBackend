import os
import datetime


class HandleLogs:
    @staticmethod
    def write_log(message):
        """Escribir log de operación normal"""
        try:
            log_dir = "src/utils/general/LOGS"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            date_str = datetime.datetime.now().strftime("%d_%m_%Y")
            log_file = f"{log_dir}/LOG_{date_str}.log"
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} - INFO - {message}\n")
        except Exception as e:
            print(f"Error escribiendo log: {e}")

    @staticmethod
    def write_error(message):
        """Escribir log de error"""
        try:
            log_dir = "src/utils/general/LOGS"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            date_str = datetime.datetime.now().strftime("%d_%m_%Y")
            error_file = f"{log_dir}/ERR_{date_str}.log"
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with open(error_file, "a", encoding="utf-8") as f:
                f.write(f"{timestamp} - ERROR - {message}\n")
        except Exception as e:
            print(f"Error escribiendo error log: {e}")