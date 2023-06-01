from datetime import datetime

from common_types import *
from cacher import *
from currency_calculator import *


class CurrencyData:
    def __init__(self, id: str, name: str, aliases) -> None:
        self.__id = id
        self.__name = name
        self.__aliases = aliases

    @property
    def id(self) -> str:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name

    def is_currency(self, caption: str) -> bool:
        if caption.upper() == self.__id or caption.lower() == self.__name.lower():
            return True
        else:
            if self.__aliases is None:
                return False
            else:
                for alias in self.__aliases:
                    if alias.lower() in caption.lower():
                        return True
                return False


class CurrencyValuePair:
    def __init__(self, id1: str, id2: str, price: float, time: datetime) -> None:
        self.__id1 = id1
        self.__id2 = id2
        self.__price = price
        self.__time = time

    def create_reversed(self):
        return CurrencyValuePair(self.__id2, self.__id1, 1 / self.__price, self.__time)

    def is_actual(self, caching_time):
        return (datetime.now() - self.__time).total_seconds() < caching_time

    @property
    def id1(self):
        return self.__id1

    @property
    def id2(self):
        return self.__id2

    @property
    def price(self):
        return self.__price

    @property
    def time(self):
        return self.__time


class CurrencyComparer:
    def __init__(self):
        self.__currencies = [
            CurrencyData("RUB", "Рубль", ["рубл"]),
            CurrencyData("EUR", "Евро", ["евр"]),
            CurrencyData("USD", "Доллар", ["доллар", "бакс", "уе"]),
            CurrencyData("CNY", "Юань", ["юан"]),
            CurrencyData("BTC", "Биткоин", ["биткоен", "биток", "битк"])
        ]

    def _get_cdid_by_id(self, currency_id: str) -> int:
        if not currency_id:
            return False

        for curr_cd_index, curr_cd in enumerate(self.__currencies):
            if curr_cd.id == currency_id:
                return curr_cd_index

        return -1

    def is_valid_id(self, currency_id: str) -> bool:
        return not self._get_cdid_by_id(currency_id) == -1

    def get_data_by_caption(self, caption: str):
        for curr_cd in self.__currencies:
            if curr_cd.is_currency(caption):
                return curr_cd

        return None

    def get_id_by_caption(self, caption: str):
        cd = self.get_data_by_caption(caption)
        if cd:
            return cd.id
        else:
            return None

    def _get_cvp(self, id1: str, id2: str) -> CurrencyValuePair:
        raise ExceptionAbstract("CurrencyComparer.get_cvp")

    def get_currency_names(self):
        return [f"{cd.name} ({cd.id})" for cd in self.__currencies]

    # def get_currency_price_by_ids(self, id_what: str, id_in_what: str) -> float:
    #     if not self.is_valid_id(id_what):
    #         raise ExceptionCurrencyName(id_what)
    #     if not self.is_valid_id(id_in_what):
    #         raise ExceptionCurrencyName(id_in_what)
    #
    #     cvp = self._get_cvp(id_what, id_in_what)
    #     return cvp.price

    def get_cvp_by_ids(self, id_what: str, id_in_what: str) -> CurrencyValuePair:
        if not self.is_valid_id(id_what):
            raise ExceptionCurrencyName(id_what)
        if not self.is_valid_id(id_in_what):
            raise ExceptionCurrencyName(id_in_what)

        cvp = self._get_cvp(id_what, id_in_what)
        return cvp

    # def get_currency_price_by_captions(self, caption_what: str, caption_in_what: str) -> float:
    #     id1 = self.get_id_by_caption(caption_what)
    #     if not id1:
    #         raise ExceptionCurrencyName(caption_what)
    #     id2 = self.get_id_by_caption(caption_in_what)
    #     if not id2:
    #         raise ExceptionCurrencyName(caption_in_what)
    #
    #     return self.get_currency_price_by_ids(id1, id2)

    def get_cvp_by_captions(self, caption_what: str, caption_in_what: str) -> CurrencyValuePair:
        id1 = self.get_id_by_caption(caption_what)
        if not id1:
            raise ExceptionCurrencyName(caption_what)
        id2 = self.get_id_by_caption(caption_in_what)
        if not id2:
            raise ExceptionCurrencyName(caption_in_what)

        return self.get_cvp_by_ids(id1, id2)

    def get_currency_name_by_id(self, id: str) -> str:
        cdid = self._get_cdid_by_id(id)
        if cdid != -1:
            return self.__currencies[cdid].name
        else:
            ExceptionCurrencyName(id)


class CurrencyComparerCached(CurrencyComparer):
    def __init__(self, cacher: Cacher, calculator: CurrencyCalculator, settings: Settings):
        super().__init__()
        self.__cacher = cacher
        self.__calculator = calculator
        self.__settings = settings

    def _get_caching_time(self):
        # raise ExceptionAbstract("CurrencyComparerCached.get_caching_time")
        return self.__settings.caching_time

    @staticmethod
    def _cvp_str_to_obj(cvp_str: str) -> CurrencyValuePair:
        cvp_dict = json.loads(cvp_str)
        # cvp_obj = CurrencyValuePair(cvp_dict["id1"], cvp_dict["id2"], cvp_dict["price"], cvp_dict["time"])
        cvp_obj = CurrencyValuePair(cvp_dict["id1"], cvp_dict["id2"], cvp_dict["price"], datetime.fromtimestamp(cvp_dict["time"]))
        return cvp_obj

    @staticmethod
    def _cvp_obj_to_str(cvp_obj: CurrencyValuePair) -> str:
        # cvp_dict = {"id1": cvp_obj.id1, "id2": cvp_obj.id2, "price": cvp_obj.price, "time": cvp_obj.time}
        cvp_dict = {"id1": cvp_obj.id1, "id2": cvp_obj.id2, "price": cvp_obj.price, "time": cvp_obj.time.timestamp()}
        cvp_str = json.dumps(cvp_dict)
        return cvp_str

    @staticmethod
    def _get_cached_value_name(id1: str, id2: str) -> str:
        return f"currency_data_{id1}_{id2}"

    def _get_cvp_from_cache(self, id1: str, id2: str, is_search_reversed: bool):
        cvp_str = self.__cacher.get_value(self._get_cached_value_name(id1, id2))
        if cvp_str:
            cvp = self._cvp_str_to_obj(cvp_str)
            if cvp.is_actual(self._get_caching_time()):
                return cvp

        if is_search_reversed:
            anti_cvp = self._get_cvp_from_cache(id2, id1, False)
            if anti_cvp:
                cvp = anti_cvp.create_reversed()
                self._set_cvp_to_cache(cvp)
                return cvp

        return None

    def _set_cvp_to_cache(self, cvp: CurrencyValuePair) -> None:
        cvp_str = self._cvp_obj_to_str(cvp)
        self.__cacher.set_value(self._get_cached_value_name(cvp.id1, cvp.id2), cvp_str)
        # raise ExceptionAbstract("CurrencyComparer.set_cvp_to_cache")

    def _get_cvp_calculated(self, id1: str, id2: str) -> CurrencyValuePair:
        price = self.__calculator.get_price(id1, id2)
        if not price:
            raise ExceptionCurrencyCalculator

        return CurrencyValuePair(id1, id2, price, datetime.now())

    def _get_cvp(self, id1: str, id2: str) -> CurrencyValuePair:
        cvp = self._get_cvp_from_cache(id1, id2, True)
        if cvp:
            return cvp
        else:
            cvp = self._get_cvp_calculated(id1, id2)
            self._set_cvp_to_cache(cvp)
            return cvp


# class CurrencyComparerCryptocomparer(CurrencyComparerCached):
#     def __init__(self, settings: Settings) -> None:
#         super().__init__(CacherRedis(), CurrencyCalculatorTest())
#         # super().__init__(CacherRedis(), CurrencyCalculatorCryptocompare(settings))
#         self.__settings = settings
#
#     def _get_caching_time(self):
#         return self.__settings.caching_time
