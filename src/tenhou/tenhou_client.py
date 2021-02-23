from __future__ import annotations

from json import dumps, loads
from random import uniform
from threading import Thread
from time import sleep
from typing import Optional
from urllib.parse import unquote

from websocket import WebSocketTimeoutException, create_connection

from config import settings

from .action_handler import ActionHandler
from .action_message import ActionMessage
from .constants import RANK_PROMOTIONS
from .exceptions import TenhouClientError

logger = settings.APP_LOGGER


class TenhouClient(ActionHandler):
    """天鳳のクライアント"""

    def __init__(self) -> None:
        super().__init__()
        self._is_running = False
        self._is_in_lobby = False
        self._is_in_game = False

        self._socket = create_connection(
            settings.TENHOU_WS_URL,
            host=settings.TENHOU_WS_HOST,
            origin=settings.TENHOU_WS_ORIGIN,
            timeout=0.5,
        )

    def __enter__(self) -> TenhouClient:
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self._socket.close()

    def run_forever(self) -> None:
        """キーボード操作で止めるかエラーになるまでループ"""

        self._is_running = True
        self._start_keep_alive()

        while self._is_running:
            try:
                self._enter_lobby()
                self._reserve_game()
                self._play_game()
            except TenhouClientError as e:
                logger.exception(e)
                self._is_running = False
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt")
                self._is_running = False

    def _start_keep_alive(self) -> None:
        """10秒ごとに接続確認のメッセージを投げる処理を別スレッドで開始"""

        def keep_alive():
            while self._is_running:
                if self._is_in_lobby or self._is_in_game:
                    self._send_message("<Z/>")
                    self._divided_sleep(10.0)

        Thread(target=keep_alive).start()

    def _enter_lobby(self) -> None:
        """ロビー入室"""

        helo_action = self._generate_helo()
        self._divided_sleep(1.0)
        self._send_action(helo_action)
        # 接続タイムアウトの0.5s * 3までHELOメッセージが返ってくるのを待ってみる
        for _ in range(3):
            action = self._recv_action()
            if action:
                self._handle_action(action)
            if self._is_in_lobby:
                break
        else:
            # HELOメッセージが返ってこなければログイン失敗
            raise TenhouClientError("Login failed")

    def _reserve_game(self) -> None:
        """対局予約"""

        join_action = self._generate_join()
        self._divided_sleep(1.0)
        self._send_action(join_action)
        # 接続タイムアウトの0.5s * 30までGOメッセージが返ってくるのを待ってみる
        for _ in range(30):
            action = self._recv_action()
            if action:
                self._handle_action(action)
            if self._is_in_game:
                break
        else:
            # GOメッセージが返ってこなければマッチング失敗
            raise TenhouClientError("Matching Failed")

    def _play_game(self) -> None:
        """対局"""

        while self._is_in_game:
            action = self._recv_action()
            if action:
                self._handle_action(action)

    def _handle_helo(self, action: ActionMessage) -> None:
        """HELOメッセージの処理"""

        super()._handle_helo(action)
        user_name = unquote(action.get_str("uname"))
        if "PF4" in action:
            _rank, _point, _rating, *_ = action.get_list("PF4")
            rank, promotion = RANK_PROMOTIONS[int(_rank)]
            point = int(_point)
            rating = int(float(_rating))
            logger.info("Enter lobby: %s %s %d/%d %d", user_name, rank, point, promotion, rating)
        else:
            logger.info("Enter lobby: %s", user_name)
        self._is_in_lobby = True

    def _handle_go(self, action: ActionMessage) -> None:
        """GOメッセージの処理"""

        super()._handle_go(action)
        self._is_in_lobby = False
        self._is_in_game = True

        action = self._generate_gok()
        self._send_action(action)
        self._random_sleep()
        action = self._generate_nextready()
        self._send_action(action)

    def _handle_taikyoku(self, action: ActionMessage) -> None:
        """TAIKYOKUメッセージの処理"""

        super()._handle_taikyoku(action)

    def _handle_init(self, action: ActionMessage) -> None:
        """INITメッセージの処理"""

        super()._handle_init(action)

    def _handle_t(self, action: ActionMessage) -> None:
        """Tタグの処理"""

        super()._handle_t(action)
        actor = action.get_int("actor")
        pai = action.get_int("pai") if "pai" in action else None

        if actor == 0:
            # ツモ切る
            assert pai is not None
            action = self._generate_d(pai)
            self._random_sleep()
            self._send_action(action)

    def _handle_d(self, action: ActionMessage) -> None:
        """Dタグの処理"""

        super()._handle_d(action)

        if "t" in action:
            # 鳴かない
            action = self._generate_n()
            self._random_sleep()
            self._send_action(action)

    def _handle_agari(self, action: ActionMessage) -> None:
        """AGARIタグの処理"""

        super()._handle_agari(action)

        if "owari" in action:
            self._is_in_game = False
            return

        action = self._generate_nextready()
        self._random_sleep()
        self._send_action(action)

    def _handle_ryuukyoku(self, action: ActionMessage) -> None:
        """RYUUKYOKUタグの処理"""

        super()._handle_ryuukyoku(action)

        if "owari" in action:
            self._is_in_game = False
            return

        action = self._generate_nextready()
        self._random_sleep()
        self._send_action(action)

    @staticmethod
    def _generate_helo() -> ActionMessage:
        """HELOメッセージを生成"""

        user_id = settings.USER_ID or "NoName"
        user_sx = settings.USER_SX
        return ActionMessage("HELO", name=user_id, sx=user_sx)

    @staticmethod
    def _generate_join() -> ActionMessage:
        """JOINメッセージを生成"""

        game_lobby = settings.GAME_LOBBY
        game_type = settings.GAME_TYPE
        is_test_play = settings.GAME_IS_TEST_PLAY
        if not is_test_play:
            game_type |= 0x1
        t = f"{game_lobby},{game_type}"
        return ActionMessage("JOIN", t=t)

    @staticmethod
    def _generate_gok() -> ActionMessage:
        """GOKメッセージを生成"""

        return ActionMessage("GOK")

    @staticmethod
    def _generate_nextready() -> ActionMessage:
        """NEXTREADYメッセージを生成"""

        return ActionMessage("NEXTREADY")

    @staticmethod
    def _generate_d(pai: int) -> ActionMessage:
        """Dメッセージを生成"""

        return ActionMessage("D", p=pai)

    @staticmethod
    def _generate_n() -> ActionMessage:
        """Nメッセージを生成"""

        return ActionMessage("N")

    def _send_message(self, message: str) -> None:
        """メッセージ送信"""

        logger.debug("<-: %s", message)
        self._socket.send(message)

    def _send_action(self, action: ActionMessage) -> None:
        """アクションを送信"""

        message = dumps(action, separators=(",", ":"))
        self._send_message(message)

    def _recv_message(self) -> Optional[str]:
        """メッセージを受信"""

        try:
            message = self._socket.recv()
        except WebSocketTimeoutException:
            return None
        logger.debug("->: %s", message)
        return message

    def _recv_action(self) -> Optional[ActionMessage]:
        """アクションを受信"""

        message = self._recv_message()
        if not message:
            return None
        return ActionMessage(**loads(message))

    def _divided_sleep(self, secs: float) -> None:
        """キーボード入力を受け付けるために、0.5秒ずつに分けてスリープ"""

        while self._is_running:
            if secs > 0.5:
                sleep(0.5)
                secs -= 0.5
            else:
                sleep(secs)
                break

    def _random_sleep(self) -> None:
        """1.0s～2.0sの間でランダムにスリープ"""

        self._divided_sleep(uniform(1.0, 2.0))
