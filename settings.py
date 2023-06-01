class Settings:
    def __init__(self, cryptocompare_key, redis_host, redis_port, redis_psw, telegram_bot_token, caching_time):
        self.__cryptocompare_key = cryptocompare_key
        self.__redis_host = redis_host
        self.__redis_port = redis_port
        self.__redis_psw = redis_psw
        self.__caching_time = caching_time
        self.__telegram_bot_token = telegram_bot_token

    @property
    def cryptocompare_key(self):
        return self.__cryptocompare_key

    @property
    def redis_host(self):
        return self.__redis_host

    @property
    def redis_port(self):
        return self.__redis_port

    @property
    def redis_psw(self):
        return self.__redis_psw

    @property
    def caching_time(self):
        return self.__caching_time

    @property
    def telegram_bot_token(self):
        return self.__telegram_bot_token
