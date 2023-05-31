class ExceptionAbstract(Exception):
    def __init__(self, path: str) -> None:
        super().__init__(f"{path}: Abstract Error!")


class ExceptionCommand(Exception):
    pass


class ExceptionValueCommand(Exception):
    pass


class ExceptionValueCommandParamCount(ExceptionValueCommand):
    pass


class ExceptionValueCommandQuantity(ExceptionValueCommand):
    pass


class ExceptionCurrency(Exception):
    pass


class ExceptionCurrencyName(Exception):
    def __init__(self, name: str) -> None:
        self.__name = name

    @property
    def name(self):
        return self.__name


class ExceptionCurrencyCalculator(ExceptionCurrency):
    pass
