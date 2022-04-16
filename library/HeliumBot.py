# Import everything
from logging import getLogger, basicConfig, INFO, WARNING
from json import load
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from time import sleep
from library.AMI135 import AMI135
from library.TestDriver import TestDriver
from library.LevelMeter import LevelMeter
from library.HeliumLogger import HeliumLogger
from library.arg_handler import plot_arg_handler_scheer_2
from library.plotter import generate_plot_scheer_2
from library.arg_handler import notifications_arg_handler
from library.Notifications import Notifications

# Configurate Logger
logger = getLogger("HeliumBot")
basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=INFO,
)
getLogger("apscheduler.scheduler").setLevel(WARNING)


class HeliumBot:
    def __init__(
        self,
        dewar="Scheer 2",
    ):
        # All possible configs
        with open("library/HeliumBot_config.json") as f:
            self.all_config = load(f)

        # Get Config for Dewar
        self.config = self.all_config[dewar]

        self.name = "HeliumBot"
        # Initialize Driver, LevelMeter(Driver), HeliumLogger(LevelMeter)
        self.driver = eval(self.config["driver"]["name"])()
        self.levelmeter = LevelMeter(
            driver=self.driver, refresh_rate=self.config["driver"]["refresh_rate"]
        )
        self.heliumlogger = HeliumLogger(levelmeter=self.levelmeter, config=self.config["logger"])

        # Initialize Telegram Bot
        self.telegram_bot = f"TelegramBot@{self.config['telegram']['bot_name']}"
        self.updater = Updater(token=self.config["telegram"]["token"], use_context=True)
        self.dispatcher = self.updater.dispatcher
        self.all_commands = {"help": ["help", "hlep"]}
        logger.info(f"({self.telegram_bot}) ... initialized!)")

        # Initialize Notifications(LevelMeter, Updater)
        self.notifications = Notifications(levelmeter=self.levelmeter, updater=self.updater)
        # Initialize Handlers
        self.add_handlers()

        sleep(3)
        logger.info(f"({self.name}) ... initialized!")

    def init(self):
        self.levelmeter.init()
        self.heliumlogger.init()
        self.updater.start_polling()
        logger.info(f"(TelegramBotWorker@{self.config['telegram']['bot_name']}) ... initialized!)")
        logger.info(
            f"(TelegramBotWorker@{self.config['telegram']['bot_name']}) ... started running!)"
        )
        logger.info(f"({self.telegram_bot}) Worker is started.)")
        logger.info(f"({self.name}) ... started running!")

    def close(self):
        self.levelmeter.close()
        self.heliumlogger.close()
        self.notifications.close_all()
        self.updater.stop()
        logger.info(
            f"(TelegramBotWorker@{self.config['telegram']['bot_name']}) ... stopped running!)"
        )
        logger.info(f"({self.telegram_bot}) Worker is stopped.)")
        logger.info(f"({self.name}) ... stopped running!")

    def add_handlers(self):
        # Status Handler
        def get_status(update: Update, context: CallbackContext):
            chat_id = update.effective_chat.id
            printer = self.levelmeter.status["printer"]
            context.bot.send_message(chat_id=chat_id, text=f"{printer}")
            logger.info(f"({self.telegram_bot}@{chat_id}) sent: {printer}")

        items = ["helium", "status"]
        for item in items:
            self.dispatcher.add_handler(CommandHandler(item, get_status))
        self.all_commands["status"] = items

        # Notification Handler
        def get_notifications(update: Update, context: CallbackContext):
            chat_id = update.effective_chat.id
            text = " ".join(context.args)
            args, description = notifications_arg_handler(text)
            if text == "":
                context.bot.send_message(chat_id=update.effective_chat.id, text=description)
            if args["notifications"] is not None:
                self.notifications.set_notifications(chat_id=chat_id, value=args["notifications"])
            if args["alarm"] is not None:
                self.notifications.set_alarm(chat_id=chat_id, value=args["alarm"])
            if args["refresh_rate"] is not None:
                self.notifications.set_refresh_rate(chat_id=chat_id, value=args["refresh_rate"])
            if args["level"] is not None:
                self.notifications.set_alarm_level(chat_id=chat_id, value=args["level"])
            string = str(self.notifications.get_status(chat_id=chat_id))
            context.bot.send_message(chat_id=update.effective_chat.id, text=string)
            logger.info(f"({self.telegram_bot}@{chat_id}) {string}")

        items = ["notify", "notifications", "notification"]
        for item in items:
            self.dispatcher.add_handler(CommandHandler(item, get_notifications))
        self.all_commands["notifications"] = items

        def get_plot(update: Update, context: CallbackContext):
            chat_id = update.message.chat_id
            text = " ".join(context.args)
            args, description = eval(self.config["plotter"]["arg_handler"])(text)
            if text == "":
                context.bot.send_message(chat_id=update.effective_chat.id, text=description)
            file_name, caption = eval(self.config["plotter"]["function"])(args, self.config)
            context.bot.sendPhoto(
                chat_id=chat_id,
                photo=open(file_name, "rb"),
                disable_notification=True,
                caption=caption,
            )
            logger.info(f"({self.telegram_bot}@{chat_id}) {caption}")

        items = ["plot", "plt", "graph", "curve"]
        for item in items:
            self.dispatcher.add_handler(CommandHandler(item, get_plot))
        self.all_commands["plot"] = items

        # Help Handler
        def helper(update: Update, context: CallbackContext):
            chat_id = update.effective_chat.id
            description = ""
            for k in self.all_commands.keys():
                string = ""
                for s in self.all_commands[k]:
                    string = string + f", /{s}"
                description = description + f"{k}: {string[2:]}\n"
            text = f"Use one of the following commands, for\n" + description
            context.bot.send_message(chat_id=chat_id, text=text)
            logger.info(f"({self.telegram_bot}@{chat_id}) ... sent help.")

        for item in self.all_commands["help"]:
            self.dispatcher.add_handler(CommandHandler(item, helper))

        # Unknown Handler (must be the last Handler added)
        def unknown(update: Update, context: CallbackContext):
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, I didn't understand that command. Use /help for help.",
            )

        unknown_handler = MessageHandler(Filters.text | Filters.command, unknown)
        self.dispatcher.add_handler(unknown_handler)


'''
heliumbot = HeliumBot()
heliumbot.init()
'''
