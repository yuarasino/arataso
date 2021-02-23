from config import settings

logger = settings.APP_LOGGER


def main():
    logger.info("App Version: %s", settings.APP_VERSION)


if __name__ == "__main__":
    main()
