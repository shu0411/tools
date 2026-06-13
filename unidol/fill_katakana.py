"""
UNIDOL CSVカタカナ補完ツール

使い方:
  # カタカナ列が空の行だけ補完（デフォルト）
  python fill_katakana.py input.csv

  # 全行のカタカナ列をひらがな列から再変換（既存値も上書き）
  python fill_katakana.py input.csv --all

  # 別ファイルに出力
  python fill_katakana.py input.csv --output output.csv
  python fill_katakana.py input.csv --all --output output.csv
"""

import csv
import argparse

from unidol_utils import FIELDNAMES, hiragana_to_katakana


def fill_katakana(input_csv: str, output_csv: str, overwrite_all: bool = False) -> None:
    with open(input_csv, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    filled = 0
    for row in rows:
        if (overwrite_all or not row["reading_katakana"]) and row["reading_hiragana"]:
            converted = hiragana_to_katakana(row["reading_hiragana"])
            if converted:
                row["reading_katakana"] = converted
                filled += 1

    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    label = "再変換" if overwrite_all else "補完"
    print(f"{label}: {filled} 件処理しました")
    print(f"出力: {output_csv}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="入力CSVファイル")
    parser.add_argument("--output", type=str, default=None, help="出力先（省略時は入力ファイルを上書き）")
    parser.add_argument("--all", action="store_true", help="既存のカタカナ値も含めて全行再変換する")
    args = parser.parse_args()

    output = args.output or args.input
    fill_katakana(args.input, output, overwrite_all=args.all)


if __name__ == "__main__":
    main()
