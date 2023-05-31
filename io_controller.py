from common_types import ExceptionAbstract
from currency_comparer import CurrencyComparer
from datetime import datetime
import telebot


class IOController:
    def show_message(self, msg: str, param=None) -> None:
        ExceptionAbstract("IOController._show_message")

    def show_values(self, currency_comparer: CurrencyComparer, param=None) -> None:
        currency_names = currency_comparer.get_currency_names()
        if len(currency_names) == 0:
            self.show_message("Нет доступных валют!")
        else:
            msg = "Доступны следующие валюты:"
            for curr_name in currency_names:
                msg += "\n" + curr_name

            self.show_message(msg, param)

    def show_currency(self, qty1: float, caption1: str, qty2: float, caption2: str, param=None) -> None:
        msg = f"{qty1} {caption1} = {qty2} {caption2}"
        self.show_message(msg, param)

    def show_currency_ex(self, qty1: float, caption1: str, qty2: float, caption2: str, time: datetime, param=None) -> None:
        time_str = time.strftime("%H:%M:%S")
        msg = f"{qty1} {caption1} = {qty2} {caption2}\n({time_str})"
        self.show_message(msg, param)

    def show_info(self, param=None):
        msg = """Приветствую!\n
        Данный бот служит для работы с валютами\n
        Доступны следующие команды:\n
        /start, /help - показ данного сообщения\n
        /values - показ списка доступных валют\n
        /value <количество переводимой валюты> <валюта, цену которой нужно узнать> <валюта, цену в которой нужно узнать>\n 
        -- показ количества валюты 2, равного по цене количеству валюты 1,\n
        -- валюта 1 и валюта 2 могут быть указаны как кодом, так и названием"""
        self.show_message(msg, param)

    def read_command(self) -> str:
        ExceptionAbstract("IOController.read_command")

    def read_message(self) -> str:
        ExceptionAbstract("IOController.read_command")

    def run(self) -> None:
        ExceptionAbstract("IOController.run")


class IOControllerConsole(IOController):
    def show_message(self, msg: str, param=None) -> None:
        print(msg)

    def read_command(self) -> str:
        return input()

    def read_message(self) -> str:
        return input()

    def run(self) -> None:
        while True:
            command = read_command()
            if command[0] == '/':
                self._proceed_input(command[1:])
            else:
                self._proceed_message(command)


class IOControllerTelegramBot(IOController):
    def __init__(self, bot: telebot.TeleBot) -> None:
        self.__bot = bot

    def show_message(self, msg: str, param=None) -> None:
        message = param
        self.__bot.send_message(message.chat.id, msg)
        print(msg)
