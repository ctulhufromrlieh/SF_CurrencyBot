import redis
# import json

from common_types import ExceptionAbstract
import config


class Cacher:
    def get_value(self, name: str):
        raise ExceptionAbstract("Cacher.get_value")

    def set_value(self, name: str, value):
        raise ExceptionAbstract("Cacher.set_value")

    def del_value(self, name: str):
        raise ExceptionAbstract("Cacher.del_value")


class CacherRedis(Cacher):
    def __init__(self):
        self.__redis = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            password=config.redis_psw
        )

    def get_value(self, name: str):
        return self.__redis.get(name)

    def set_value(self, name: str, value):
        return self.__redis.set(name, value)

    def del_value(self, name: str) -> None:
        self.__redis.delete(name)
