from logging import getLogger
from datetime import datetime
from time import sleep
from os import makedirs
from os.path import isfile
from threading import Thread, Event

logger = getLogger("HeliumBot")


class HeliumLoggerWorker(Thread):
    def __init__(
        self,
        level_meter,
        config,
    ):
        super().__init__()
        self.exit_request = Event()

        self.name = "HeliumLoggerWorker"
        self.level_meter = level_meter
        self.config = config
        logger.info(f"({self.name}) ... initialized!")

    def run(self):
        logger.info(f"({self.name}) ... started running!")
        old_status = 0

        makedirs(self.config["path"], exist_ok=True)
        while not self.exit_request.is_set():
            utc_timer = datetime.utcnow()
            file = f"{self.config['path']}{self.config['file_name']}_{utc_timer.strftime('%Y-%m-%d')}.csv"

            initialized = False
            if isfile(file):
                with open(file, "r") as fd:
                    initialized = fd.readline()[0] == "#"

            if not initialized:
                with open(file, "a") as fd:
                    for headline in self.config["header"]:
                        fd.write(f"# {headline}\n")

            status = self.level_meter.status

            if not status == old_status:
                with open(file, "a") as fd:
                    fd.write(f"{status['file_string']}\n")
                logger.debug(f"({self.name}) {status['printer']}")
                old_status = status
            else:
                logger.error(f"({self.name}) status: still same")

            sleep(self.config["refresh_rate"])
        logger.info(f"({self.name}) ... stopped running!")


class HeliumLogger:
    def __init__(
        self,
        levelmeter,
        config,
    ):
        self.name = "HeliumLogger"
        self.levelmeter = levelmeter
        self.config = config
        logger.info(f"({self.name}) ... initialized!")

    def init(self):
        self.HeliumLoggerWorker = HeliumLoggerWorker(level_meter=self.levelmeter, config=self.config)
        self.HeliumLoggerWorker.start()
        logger.info(f"({self.name}) Worker is started.")

    def close(self):
        while not self.HeliumLoggerWorker.exit_request.is_set():
            self.HeliumLoggerWorker.exit_request.set()
            sleep(0.1)
        logger.info(f"({self.name}) Worker is closed.")
