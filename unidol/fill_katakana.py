"""
UNIDOL CSVカタカナ補完ツール
カタカナ列が空の行に対して、ひらがな列から変換して埋める。

使い方:
  # 別ファイルに出力
  python fill_katakana.py fixed_unidol_teams_reading.csv --output filled.csv

  # 元ファイルを上書き
  python fill_katakana.py fixed_unidol_teams_reading.csv
"""

import csv
import re
import sys
import argparse

from unidol.unidol_utils import FIELDNAMES, hiragana_to_katakana


def fill_katakana(input_csv: str, output_csv: str) -> None:
    with open(input_csv, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    filled = 0
    for row in rows:
        if not row["reading_katakana"] and row["reading_hiragana"]:
            converted = hiragana_to_katakana(row["reading_hiragana"])
            if converted:
                row["reading_katakana"] = converted
                filled += 1

    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"変換: {filled} 件埋めました")
    print(f"出力: {output_csv}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="入力CSVファイル")
    parser.add_argument("--output", type=str, default=None, help="出力先（省略時は入力ファイルを上書き）")
    args = parser.parse_args()

    output = args.output or args.input
    fill_katakana(args.input, output)


if __name__ == "__main__":
    main()
