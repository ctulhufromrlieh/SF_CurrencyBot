from currency_comparer import *

import redis.exceptions
import requests
import telebot


def exception_handler(func):
    def wrapper(*args, **kwargs):
        # todo: redo these two evil things
        self = args[0]
        param = args[-1]
        try:
            return_value = func(*args, **kwargs)
            return return_value
        except ExceptionValueCommandParamCount:
            self._show_message("Ошибка запроса перевода валюты: количество аргументов должно быть 3!", param)
        except ExceptionValueCommandQuantity:
            self._show_message("Ошибка запроса перевода валюты: первый аргумент должен быть числом!", param)
        except ExceptionCommand:
            self._show_message("Неизвестная команда!", param)
        except ExceptionCurrencyName as e:
            self._show_message(f"Неверное имя валюты: {e.name}!", param)
        except ExceptionCurrencyCalculator:
            self._show_message("Не получилось вычислить!", param)
        except redis.exceptions.RedisError:
            self._show_message("Проблема с системой кэширования Redis!", param)
        except requests.HTTPError:
            self._show_message("Проблема доступом к сети Интернет!", param)

    return wrapper


class Application:
    def _show_message(self, msg: str, param=None) -> None:
        ExceptionAbstract("Application._show_message")

    def _show_values(self, currency_comparer: CurrencyComparer, param=None) -> None:
        currency_names = currency_comparer.get_currency_names()
        if len(currency_names) == 0:
            self._show_message("Нет доступных валют!", param)
        else:
            msg = "Доступны следующие валюты:"
            for curr_name in currency_names:
                msg += "\n" + curr_name

            self._show_message(msg, param)

    def _show_currency(self, qty1: float, caption1: str, qty2: float, caption2: str, param=None) -> None:
        msg = f"{qty1} {caption1} = {qty2} {caption2}"
        self._show_message(msg, param)

    def _show_currency_ex(self, qty1: float, caption1: str, qty2: float, caption2: str, time: datetime, param=None) -> None:
        time_str = time.strftime("%H:%M:%S")
        msg = f"{qty1} {caption1} = {qty2} {caption2}\n({time_str})"
        self._show_message(msg, param)

    def _show_info(self, param=None):
        msg = """Приветствую!
        Данный бот служит для работы с валютами.
        Доступны следующие команды:
        /start, /help - показ данного сообщения
        /values - показ списка доступных валют
        /value <кол-во 1> <валюта1> <валюта2> 
        - показ количества валюты 2, равноценного количеству валюты 1
        Сообщение вида <кол-во 1> <валюта1> <валюта2>
        - показ количества валюты 2, равноценного количеству валюты 1"""
        self._show_message(msg, param)

    @staticmethod
    def _create_cacher() -> Cacher:
        return CacherRedis()

    def _create_calculator(self) -> CurrencyCalculator:
        return CurrencyCalculatorCryptocompare(self._settings)

    def _create_currency_comparer(self) -> CurrencyComparer:
        return CurrencyComparerCached(self._create_cacher(), self._create_calculator(), self._settings)

    @exception_handler
    def _proceed_command_value(self, args: str, param=None):
        params = args.split()
        if len(params) != 3:
            raise ExceptionValueCommandParamCount()

        if not params[0].isnumeric():
            ExceptionValueCommandQuantity()

        cvp = self._currency_comparer.get_cvp_by_captions(params[1], params[2])
        price = cvp.price
        name1 = self._currency_comparer.get_currency_name_by_id(cvp.id1)
        name2 = self._currency_comparer.get_currency_name_by_id(cvp.id2)

        try:
            qty1 = float(params[0])
        except ValueError:
            raise ExceptionValueCommandQuantity

        self._show_currency_ex(qty1, name1, qty1 * price, name2, cvp.time, param)

    @exception_handler
    def _proceed_command(self, command: str, param=None):
        args = command.split(maxsplit=1)
        true_command = args[0]
        if len(args) > 1:
            arg = args[1]
        else:
            arg = None

        if true_command.lower() in ["start", "help"]:
            # self._io_controller.show_info(param)
            self._show_info(param)
        elif true_command.lower() == "values":
            # self._io_controller.show_values(self._currency_comparer, param)
            self._show_values(self._currency_comparer, param)
        elif true_command.lower() == "value":
            self._proceed_command_value(arg, param)
        else:
            raise ExceptionCommand("Application._proceed_command: Unknown command")

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._currency_comparer = self._create_currency_comparer()

    def run(self):
        raise ExceptionAbstract("Application.run")


class ApplicationConsole(Application):
    def _show_message(self, msg: str, param=None) -> None:
        print(msg)

    @exception_handler
    def _proceed_input(self, command: str):
        args = command.split(maxsplit=1)
        true_command = args[0]
        if len(args) > 1:
            arg = args[1]
        else:
            arg = None

        if true_command in ["start", "help"]:
            self._show_info()
        elif true_command == "values":
            self._show_values(self._currency_comparer)
        elif true_command == "value":
            self._proceed_command_value(arg)
        else:
            raise ExceptionCommand("Application._proceed_command: Unknown command")

    def _proceed_message(self, msg: str):
        self._proceed_command_value(msg)

    def run(self):
        while True:
            command = input()
            if command[0] == '/':
                self._proceed_input(command[1:])
            else:
                self._proceed_message(command)


class ApplicationTelegramBot(Application):

    def _show_message(self, msg: str, param=None) -> None:
        message = param
        self._bot.reply_to(message, msg)

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings)
        self._bot = telebot.TeleBot(settings.telegram_bot_token)

        @self._bot.message_handler(commands=['start', 'help'])
        def handler_start_help(message: telebot.types.Message):
            self._show_info(message)

        @self._bot.message_handler(commands=['values'])
        def handler_values(message: telebot.types.Message):
            self._show_values(self._currency_comparer, message)

        @self._bot.message_handler(commands=['value'])
        def handler_value(message: telebot.types.Message):
            # self._show_values(self._currency_comparer, message)
            args = message.text.split(maxsplit=1)
            if len(args) > 1:
                arg = args[1]
            else:
                arg = None
            self._proceed_command_value(arg, message)

        @self._bot.message_handler(content_types=['text'])
        def handle_value(message: telebot.types.Message):
            self._proceed_command_value(message.text, message)

    def run(self):
        # self._bot.skip_pending = True
        # self._bot.infinity_polling()
        self._bot.polling(none_stop=True)
