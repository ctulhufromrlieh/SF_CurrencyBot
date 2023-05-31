import config
import settings
import application

if __name__ == "__main__":
    settings = settings.Settings(config.cryptocompare_key, config.redis_host, config.redis_port, config.redis_psw,
                                 config.telegram_bot_token, config.caching_time)

    app = application.ApplicationConsole(settings)

    app.run()

