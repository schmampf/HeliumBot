from threading import Thread, Event
from datetime import timedelta, datetime
from logging import getLogger
from time import sleep

logger = getLogger("HeliumBot")


class NotificationsWorker(Thread):
    def __init__(self, level_meter, updater, chat_id):
        super().__init__()
        self.notifications = Event()
        self.alarm = Event()
        self.name = f"NotificationsWorker[{chat_id}]"

        self.level_meter = level_meter
        self.updater = updater
        self.chat_id = chat_id

        self.refresh_rate = 3600.0  # s
        self.alarm_level = 20.0  # L
        self.program_refresh = 5  # s

        logger.info(f"({self.name}) ... initialized!")

    def run(self):
        logger.info(f"({self.name}) ... started running!")
        temp_notification_timer = datetime.utcnow() - timedelta(seconds=self.refresh_rate + 1)
        while self.notifications.is_set():
            timer = datetime.utcnow()
            if (timer - temp_notification_timer) >= timedelta(seconds=self.refresh_rate):
                temp_notification_timer = timer
                status = self.level_meter.status
                if self.alarm.is_set() and status["volume"] <= self.alarm_level:
                    disable_notification = False
                else:
                    disable_notification = True

                self.updater.bot.send_message(
                    chat_id=self.chat_id,
                    text=f"{status['printer']}",
                    disable_notification=disable_notification,
                )
                logger.info(f"({self.name}) {status['printer']}")

            sleep(self.program_refresh)
        logger.info(f"({self.name}) ... stopped running!")


"""
# Test
notificationworker = NotificationsWorker(levelmeter=levelmeter,
                                        updater=updater,
                                        chat_id=62579439)

notificationworker.notifications.set()
notificationworker.start()
notificationworker.refresh_rate = 3
"""


class Notifications:
    def __init__(self, levelmeter, updater):
        self.name = "Notifications"
        self.levelmeter = levelmeter
        self.updater = updater
        self.chat_ids = []
        self.notificationworker = {}
        logger.info(f"({self.name}) ... initialized!")

    def close_all(self):
        while not self.chat_ids == []:
            for chat_id in self.chat_ids:
                self.set_notifications(chat_id, value=False)

    @property
    def threads(self):
        return self.chat_ids, self.notificationworker

    @property
    def status(self):
        status = []
        for chat_id in self.chat_ids:
            status.append(self.get_status(chat_id))
        return status

    def get_status(self, chat_id):
        status = "Start with: /notify notify:True"
        if chat_id in self.chat_ids:
            status = {
                "chat_id": chat_id,
                "notifications": self.get_notifications(chat_id),
                "alarm": self.get_alarm(chat_id),
                "refresh_rate": self.get_refresh_rate(chat_id),
                "level": self.get_alarm_level(chat_id),
                "program_refresh": self.get_program_refresh(chat_id),
            }
        return status

    def get_notifications(self, chat_id) -> bool:
        return self.notificationworker[f"{chat_id}"].notifications.is_set()

    def set_notifications(self, chat_id, value: bool):
        if value:
            if not chat_id in self.chat_ids:
                self.chat_ids.append(chat_id)
                self.notificationworker[f"{chat_id}"] = NotificationsWorker(
                    self.levelmeter, self.updater, chat_id
                )
                self.notificationworker[f"{chat_id}"].notifications.set()
                self.notificationworker[f"{chat_id}"].alarm.set()
                self.notificationworker[f"{chat_id}"].start()
                logger.info(f"({self.name}@{chat_id}) Worker is started.")
                self.updater.bot.send_message(
                    chat_id=chat_id, text=f"Worker started for chat_id: {chat_id}."
                )
            else:
                self.notificationworker[f"{chat_id}"].notifications.set()
        elif not value:
            while self.notificationworker[f"{chat_id}"].notifications.is_set():
                self.notificationworker[f"{chat_id}"].notifications.clear()
                sleep(0.1)
            self.chat_ids.remove(chat_id)
            logger.info(f"({self.name}@{chat_id}) Worker is closed.")
            self.updater.bot.send_message(
                chat_id=chat_id, text=f"Worker stopped for chat_id:{chat_id}."
            )
        else:
            pass
        sleep(1)

    def get_alarm(self, chat_id) -> bool:
        return self.notificationworker[f"{chat_id}"].alarm.is_set()

    def set_alarm(self, chat_id, value: bool):
        if value:
            self.notificationworker[f"{chat_id}"].alarm.set()
        else:
            self.notificationworker[f"{chat_id}"].alarm.clear()

    def get_refresh_rate(self, chat_id) -> float:
        return self.notificationworker[f"{chat_id}"].refresh_rate

    def set_refresh_rate(self, chat_id, value: float):
        self.notificationworker[f"{chat_id}"].refresh_rate = value

    def get_alarm_level(self, chat_id) -> float:
        return self.notificationworker[f"{chat_id}"].alarm_level

    def set_alarm_level(self, chat_id, value: float):
        self.notificationworker[f"{chat_id}"].alarm_level = value

    def get_program_refresh(self, chat_id) -> float:
        return self.notificationworker[f"{chat_id}"].program_refresh

    def set_program_refresh(self, chat_id, value: float):
        self.notificationworker[f"{chat_id}"].program_refresh = value


"""
# Test
notifications = Notifications(levelmeter=levelmeter, updater=updater)
notifications.set_notifications(chat_id=62579439, value=True)
notifications.set_notifications(chat_id=-771946321, value=True)
notifications.set_refresh_rate(chat_id=62579439, value=10)
notifications.set_refresh_rate(chat_id=-771946321, value=10)
print(notifications.status, notifications.threads)
notifications.close_all()
"""
