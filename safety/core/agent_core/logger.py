"""日志管理"""
from dataclasses import dataclass
from datetime import datetime

@dataclass
class LogItem:
    time: str
    level: str
    msg: str

class PipelineLogger:
    def __init__(self, debug = True):
        self.logs: list [LogItem] = []
        self.debug = debug

    def info(self, msg: str):
        record = LogItem(
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            level = "INFO",
            msg = msg
        )
        self.logs.append(record)
        if self.debug:
            print(f'INFO: [{record.time}][{record.level}]{record.msg}')

    def warning(self, msg: str):
        record = LogItem(
        time = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        level = "WARNING",
        msg = msg
        )
        self.logs.append(record)
        print(f'WARNING: [{record.time}][{record.level}]{record.msg}')

    def error(self, msg: str):
        record = LogItem(
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            level = "ERROR",
            msg = msg
        )
        self.logs.append(record)
        print(f'ERROR: [{record.time}][{record.level}]{record.msg}')

    def get_plain_test(self):
        """转换成纯文本，传给前端"""
        lines = []
        for record in self.logs:
            lines.append(f'[{record.level}]:[ {record.msg}]{record.time}')
        return lines

