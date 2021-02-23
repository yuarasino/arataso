from config import settings
from tenhou.tenhou_client import TenhouClient

logger = settings.APP_LOGGER


def main():
    logger.info("App Version: %s", settings.APP_VERSION)

    with TenhouClient() as client:
        client.run_forever()


if __name__ == "__main__":
    main()
