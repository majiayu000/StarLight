import logging
import os
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler
import time

class Log:
    log_name: str = ''
    dir_name: str = 'log'
    log_names: list[str] = []
    dir_names: list[str] = []
    file_names: list[str] = []

    @classmethod
    def log(cls, file_name: str = None, dir_name: str = None) -> logging.Logger:
        if not cls.log_name:
            cls.log_name = 'root'
            log_name = cls.log_name
            if dir_name:
                cls.dir_name = f'{cls.dir_name}/{dir_name}'
            dir_name = cls.dir_name
            if not file_name:
                file_name = cls.log_name
        else:
            dir_name = f'{cls.dir_name}/{dir_name}' if dir_name else cls.dir_name
            if file_name:
                log_name = file_name
            else:
                log_name = cls.log_name
                file_name = log_name

        if log_name in cls.log_names and dir_name in cls.dir_names and file_name in cls.file_names:
            logger = logging.getLogger(log_name)
        else:
            if log_name not in cls.log_names:
                cls.log_names.append(log_name)
            if dir_name not in cls.dir_names:
                cls.dir_names.append(dir_name)
            if file_name not in cls.file_names:
                cls.file_names.append(file_name)

            def localtime(*args) -> time.struct_time:
                converted = datetime.utcnow() + timedelta(hours=8)
                return converted.timetuple()

            current_path = os.path.abspath(os.path.dirname(__file__))
            root_path = os.path.split(current_path)[0]

            dir_name = f'{root_path}/{dir_name}'
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

            fmt = '%(asctime)s %(levelname)s  %(name)s %(filename)s [line: %(lineno)d] %(funcName)s：\n%(message)s'
            logging.Formatter.converter = localtime
            logging.basicConfig(level=logging.INFO, format=fmt)
            formatter = logging.Formatter(fmt)
            filehandler = TimedRotatingFileHandler(f'{dir_name}/{file_name}', 'D', 1, 30, encoding="utf-8")
            filehandler.setFormatter(formatter)
            logger = logging.getLogger(None if log_name == 'root' else log_name)
            logger.propagate = False
            logger.addHandler(filehandler)

        return logger
