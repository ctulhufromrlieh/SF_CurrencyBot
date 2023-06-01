import requests
import json

from common_types import *
from settings import Settings


class CurrencyCalculator:
    def get_price(self, id1: str, id2: str) -> float:
        ExceptionAbstract("CurrencyCalculator.get_price:")


class CurrencyCalculatorTest(CurrencyCalculator):
    def get_price(self, id1: str, id2: str) -> float:
        return 22


class CurrencyCalculatorCryptocompare(CurrencyCalculator):
    def __init__(self, settings: Settings) -> None:
        self.__settings = settings

    def get_price(self, id1: str, id2: str) -> float:
        req_str = f"https://min-api.cryptocompare.com/data/price?fsym={id1}&tsyms={id2}&api_key={self.__settings.cryptocompare_key}"
        r = requests.get(req_str)
        if r.status_code == 200:
            response = json.loads(r.content)
            # print(r.content)
            # print("------------------------")
            # print(response)

            price = response.get(id2)
            return price
        else:
            r.raise_for_status()
