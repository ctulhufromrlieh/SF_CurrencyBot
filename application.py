# from common_types import *
# from settings import Settings
from io_controller import *
# from cacher import *
# from currency_calculator import *
from currency_comparer import *

import redis.exceptions
import requests
import telebot
# RedisError
# HTTPError


def exception_handler(func):
    # def wrapper(self, msg: str, param):
    def wrapper(*args, **kwargs):
        self = args[0]
        try:
            # return_value = func(self, msg, param)
            return_value = func(*args, **kwargs)
            return return_value
        except ExceptionValueCommandParamCount:
            self._io_controller.show_message("Ошибка запроса перевода валюты: количество аргументов должно быть 3!")
        except ExceptionValueCommandQuantity:
            self._io_controller.show_message("Ошибка запроса перевода валюты: первый аргумент должен быть числом!")
        except ExceptionCommand:
            self._io_controller.show_message("Неизвестная команда!")
        except ExceptionCurrencyName as e:
            self._io_controller.show_message(f"Неверное имя валюты: {e.name}!")
        except ExceptionCurrencyCalculator:
            self._io_controller.show_message("Не получилось вычислить!")
        except redis.exceptions.RedisError:
            self._io_controller.show_message("Проблема с системой кэширования Redis!")
        except requests.HTTPError:
            self._io_controller.show_message("Проблема доступом к сети Интернет!")

    return wrapper


class Handler:
    pass

class Application:
    @staticmethod
    def _create_io_controller() -> IOController:
        raise ExceptionAbstract("Application._create_io_controller")

    @staticmethod
    def _create_cacher() -> Cacher:
        return CacherRedis()

    def _create_calculator(self) -> CurrencyCalculator:
        return CurrencyCalculatorCryptocompare(self._settings)

    def _create_currency_comparer(self) -> CurrencyComparer:
        return CurrencyComparerCached(self._create_cacher(), self._create_calculator())

    @exception_handler
    def _proceed_command_value(self, args: str, param=None):
        params = args.split()
        if len(params) != 3:
            raise ExceptionValueCommandParamCount()

        if not params[0].isnumeric():
            ExceptionValueCommandQuantity()

        price = self._currency_comparer.get_currency_price_by_captions(params[1], params[2])
        qty1 = float(params[0])

        self._io_controller.show_currency(qty1, params[1], qty1 * price, params[2], param)

    @exception_handler
    def _proceed_command_help(self, param=None):
        self._io_controller.show_message(param)

    @exception_handler
    def _proceed_command_values(self, param=None):
        self._io_controller.show_values(self._currency_comparer, param)

    # @exception_handler
    # def _proceed_command(self, command: str, param=None):
    #     args = command.split(maxsplit=1)
    #     true_command = args[0]
    #     if len(args) > 1:
    #         arg = args[1]
    #     else:
    #         arg = None
    #
    #     if true_command in ["start", "help"]:
    #         self._io_controller.show_info(param)
    #     elif true_command == "values":
    #         self._io_controller.show_values(self._currency_comparer, param)
    #     elif true_command == "value":
    #         self._proceed_command_value(arg, param)
    #     else:
    #         raise ExceptionCommand("Application._proceed_command: Unknown command")

    @exception_handler
    def _proceed_message(self, msg: str, param=None):
        self._proceed_command_value(msg, param)

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._io_controller = self._create_io_controller()
        self._currency_comparer = self._create_currency_comparer()

    def run(self):
        raise ExceptionAbstract("Application.run")


class ApplicationConsole(Application):
    @staticmethod
    def _create_io_controller() -> IOController:
        return IOControllerConsole()

    def _proceed_input(self, command: str, param=None):
        args = command.split(maxsplit=1)
        true_command = args[0]
        if len(args) > 1:
            arg = args[1]
        else:
            arg = None

        if true_command in ["start", "help"]:
            self._proceed_command_help(param)
        elif true_command == "values":
            self._proceed_command_values(param)
            # self._io_controller.show_values(self._currency_comparer, param)
        elif true_command == "value":
            # self._proceed_command_value(arg, param)
            self._proceed_command_value(arg, param)
        else:
            raise ExceptionCommand("Application._proceed_command: Unknown command")

    def run(self):
        while True:
            command = self._io_controller.read_command()
            if command[0] == '/':
                self._proceed_input(command[1:])
            else:
                self._proceed_message(command)


class ApplicationTelegramBot(Application):
    @staticmethod
    def _create_io_controller() -> IOController:
        pass
        # return IOControllerConsole()

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)
        self._bot = bot = telebot.TeleBot(settings.telegram_bot_token)

        @self._bot.message_handler(commands=['start', 'help'])
        def handler_start_help(message: telebot.types.Message):
            self._io_controller.show_info(message)

        @self._bot.message_handler(commands=['values'])
        def handler_start_help(message: telebot.types.Message):
            self._io_controller.show_values(self._currency_comparer, message)

    def run(self):
        self._bot.polling(none_stop=True)
        # while True:
        #     command = self._io_controller.read_command()
        #     if command[0] == '/':
        #         self._proceed_command(command[1:])
        #     else:
        #         self._proceed_message(command)