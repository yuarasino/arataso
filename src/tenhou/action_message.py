from typing import Any

from .constants import PAI_TAG_PATTERN


class ActionMessage(dict[str, Any]):
    """アクションを送受信するためのメッセージ"""

    def __init__(self, tag: str, **kwargs) -> None:
        super().__init__(tag=tag, **kwargs)

    @property
    def tag(self) -> str:
        """タグ"""

        return self["tag"]

    def is_pai_tag(self) -> bool:
        """タグが牌の情報を持っているか"""

        if match := PAI_TAG_PATTERN.match(self.tag):
            _tag, _pai = match.groups()
            self._add_pai_info(_tag, _pai)
            return True
        else:
            return False

    def get_str(self, key: str) -> str:
        """文字列として値を取得"""

        return str(self[key])

    def get_int(self, key: str) -> int:
        """整数として値を取得"""

        return int(self[key])

    def get_list(self, key: str) -> list[str]:
        """文字列のリストとして値を取得"""

        return self.get_str(key).split(",")

    def _add_pai_info(self, _tag: str, _pai: str) -> None:
        """アクションをした人と牌の情報を付与"""

        if _tag in "TUVW":
            tag = "T"
            actor = "TUVW".index(_tag)
        else:
            tag = "D"
            actor = "DEFGdefg".index(_tag)
        pai = int(_pai) if _pai else None
        self["tag"] = tag
        self["actor"] = actor
        if pai is not None:
            self["pai"] = pai
