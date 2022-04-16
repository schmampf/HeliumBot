from threading import Thread, Event
from datetime import timedelta, datetime
from time import sleep
from logging import getLogger

logger = getLogger("HeliumBot")


class LevelMeterWorker(Thread):
    def __init__(self, driver, refresh_rate):
        super().__init__()
        self.exit_request = Event()
        self.name = f"LevelMeterWorker"

        self.driver = driver
        self.refresh_rate = refresh_rate
        self.status = self.driver.status
        logger.info(f"({self.name}) ... initialized!")

    def run(self):
        logger.info(f"({self.name}) ... started running!")
        temp_notification_timer = datetime.utcnow()
        while not self.exit_request.is_set():
            timer = datetime.utcnow()
            if (timer - temp_notification_timer) >= timedelta(seconds=self.refresh_rate):
                temp_notification_timer = timer
                self.status = self.driver.status
                logger.debug(f"({self.name}) {self.status['printer']}")
            sleep(0.1)
        logger.info(f"({self.name}) ... stopped running!")


"""
# Test
levelmeterworker = LevelMeterWorker(driver=ami135)
levelmeterworker.start()
sleep(5)
levelmeterworker.exit_request.set()
"""


class LevelMeter:
    def __init__(self, driver, refresh_rate):
        self.name = f"LevelMeter"
        self.driver = driver
        self.refresh_rate = refresh_rate
        logger.info(f"({self.name}) ... initialized!")

    def init(self):
        self.levelmeterworker = LevelMeterWorker(driver=self.driver, refresh_rate=self.refresh_rate)
        self.levelmeterworker.start()
        logger.info(f"({self.name}) Worker is started.")

    def close(self):
        self.levelmeterworker.exit_request.set()
        logger.info(f"({self.name}) Worker is stopped.")

    @property
    def status(self):
        status = self.levelmeterworker.status
        logger.debug(f"({self.name}) {status}")
        return status


"""
# Test
level_meter = LevelMeter(driver=ami135)
level_meter.start()
sleep(5)
level_meter.status
sleep(5)
level_meter.close()
"""
