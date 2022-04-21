from time import sleep
from library.HeliumBot import HeliumBot
from logging import getLogger, basicConfig, INFO, WARNING

logger = getLogger("HeliumBot")
basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=INFO,
)
getLogger("apscheduler.scheduler").setLevel(WARNING)
if __name__ == "__main__":
    helium_bot = HeliumBot(dewar="Scheer 2")
    helium_bot.init()
    try:
        while True:
            sleep(3)
    except KeyboardInterrupt:
        helium_bot.close()
