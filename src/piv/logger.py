import datetime
import logging
import os

class CustomAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        # Garantiza que siempre estén presentes los campos personalizados
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        if "class_name" not in kwargs["extra"]:
            kwargs["extra"]["class_name"] = self.extra.get("class_name", "N/A")
        if "function_name" not in kwargs["extra"]:
            kwargs["extra"]["function_name"] = self.extra.get("function_name", "N/A")
        return msg, kwargs

class Logger:
    def __init__(self):
        if not os.path.exists("logs"):
            os.makedirs("logs")

        self.log_file = f"logs/meta_analysis_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        # Configura el formateador y el handler manualmente
        formatter = logging.Formatter(
            "[%(asctime)s | %(name)s | %(class_name)s | %(function_name)s | %(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        file_handler = logging.FileHandler(self.log_file)
        file_handler.setFormatter(formatter)

        base_logger = logging.getLogger("DolarAnalysis")
        base_logger.setLevel(logging.INFO)
        base_logger.addHandler(file_handler)

        self.logger = CustomAdapter(base_logger, extra={})

    def info(self, class_name, function_name, description):
        self.logger.info(description, extra={"class_name": class_name, "function_name": function_name})

    def warning(self, class_name, function_name, description):
        self.logger.warning(description, extra={"class_name": class_name, "function_name": function_name})

    def error(self, class_name, function_name, description):
        self.logger.error(description, extra={"class_name": class_name, "function_name": function_name})
