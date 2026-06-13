"""
UNIDOL スクレイパー共通定数・関数
"""

FIELDNAMES = ["id", "team_name", "reading_hiragana", "reading_katakana", "year", "region", "university", "url"]

BASE_URL = "http://unidol.jp/teams/detail/"
SLEEP_SEC = 0.5  # サーバー負荷軽減（変えないでください）


def hiragana_to_katakana(text: str) -> str:
    """ひらがな → カタカナ変換（変換できない文字は除外、→/～ はーに変換）"""
    NORMALIZE = {"→": "ー", "～": "ー", "〜": "ー"}
    result = []
    for c in text:
        if c in NORMALIZE:
            result.append(NORMALIZE[c])
        elif "ぁ" <= c <= "ん":
            result.append(chr(ord(c) + 0x60))
        elif "ァ" <= c <= "ン" or c == "ー":
            result.append(c)
        # それ以外は除外
    return "".join(result)
