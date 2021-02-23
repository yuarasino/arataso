from abc import ABC

from .action_message import ActionMessage


class ActionHandler(ABC):
    """受信したアクションのハンドラ"""

    def _handle_action(self, action: ActionMessage) -> None:
        """アクションをタグ別のハンドラに振り分けて処理"""

        handler_name = f"_handle_{action.tag.lower()}"
        if handler_name in dir(self):
            getattr(self, handler_name)(action)
        elif action.is_pai_tag():
            handler_name = f"_handle_{action.tag.lower()}"
            getattr(self, handler_name)(action)
        else:
            return None

    def _handle_helo(self, action: ActionMessage) -> None:
        pass

    def _handle_go(self, action: ActionMessage) -> None:
        pass

    def _handle_taikyoku(self, action: ActionMessage) -> None:
        pass

    def _handle_init(self, action: ActionMessage) -> None:
        pass

    def _handle_t(self, action: ActionMessage) -> None:
        pass

    def _handle_d(self, action: ActionMessage) -> None:
        pass

    def _handle_agari(self, action: ActionMessage) -> None:
        pass

    def _handle_ryuukyoku(self, action: ActionMessage) -> None:
        pass
