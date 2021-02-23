# ユーザー設定
USER_ID = "NoName"
USER_SX = "M"

# ゲーム設定
GAME_LOBBY = 0
GAME_TYPE = 64
GAME_IS_TEST_PLAY = True
GAME_IS_TOURNAMENT = False

# 天鳳設定
TENHOU_WS_URL = ""
TENHOU_WS_HOST = ""
TENHOU_WS_ORIGIN = ""

# アプリケーション設定
from .logger import app_logger, console_handler  # noqa: E402

app_logger.addHandler(console_handler)

APP_VERSION = "0.1.0"
APP_LOGGER = app_logger

# gitで管理したくない情報で上書き
try:
    from .local_settings import *  # noqa: F403,F401
except ImportError:
    pass
