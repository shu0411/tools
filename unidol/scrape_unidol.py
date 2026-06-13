"""
UNIDOL チーム名・読み仮名スクレイパー
使い方:
  # 動作確認（1〜20件）
  python scrape_unidol.py --test

  # 全件（1〜1121）
  python scrape_unidol.py

  # 範囲指定
  python scrape_unidol.py --start 1 --end 100

  # 任意のIDをカンマ区切りで指定
  python scrape_unidol.py --ids "100,200,300"
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import sys
import argparse

from unidol_utils import BASE_URL, SLEEP_SEC, FIELDNAMES, hiragana_to_katakana


def scrape_team(session: requests.Session, team_id: int) -> dict | None:
    url = f"{BASE_URL}{team_id}"
    try:
        resp = session.get(url, timeout=10, allow_redirects=True)

        # リダイレクトで /teams に飛んだ → 存在しないID
        if "/teams/detail/" not in resp.url:
            return None

        soup = BeautifulSoup(resp.content, "html.parser")

        name_tag = soup.find(class_="team_detail_info_name_title")
        kana_tag = soup.find(class_="team_detail_info_name_title_kana")
        year_tag = soup.find("a", class_="left_side_menu_link_list_arrow_active")
        region_tag = soup.find("a", class_="left_side_menu_link_item_active")

        if not name_tag:
            return None

        team_name = name_tag.get_text(strip=True)
        reading_raw = kana_tag.get_text(strip=True) if kana_tag else ""

        # ひらがなが1文字以上あればその部分だけカタカナに変換、なければカタカナ列は空
        reading_hiragana = reading_raw
        reading_katakana = hiragana_to_katakana(reading_raw) if re.search(r"[ぁ-ん]", reading_raw) else ""

        year_text = ""
        if year_tag:
            span = year_tag.find("span", class_="left_side_menu_link_list_content")
            year_text = span.get_text(strip=True).replace("年チーム", "") if span else ""

        region_text = ""
        if region_tag:
            span = region_tag.find("span", class_="left_side_menu_link_item_content")
            region_text = span.get_text(strip=True) if span else ""

        university_text = ""
        detail_tag = soup.find(class_="team_detail_info_name_detail")
        if detail_tag:
            for row in detail_tag.find_all(class_="table_row"):
                cells = row.find_all(class_="table_cell")
                if len(cells) >= 2 and cells[0].get_text(strip=True) == "大学":
                    university_text = cells[1].get_text(strip=True)
                    break

        return {
            "id": team_id,
            "team_name": team_name,
            "reading_hiragana": reading_hiragana,
            "reading_katakana": reading_katakana,
            "year": year_text,
            "region": region_text,
            "university": university_text,
            "url": url,
        }

    except requests.RequestException as e:
        print(f"  [ERROR] id={team_id}: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="1〜20のみ実行（動作確認）")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=1121)
    parser.add_argument("--ids", type=str, help="カンマ区切りで任意のIDを指定 例: 100,200,300")
    args = parser.parse_args()

    if args.ids:
        id_list = [int(x.strip()) for x in args.ids.split(",")]
        print(f"スクレイピング開始: {args.ids}  (待機 {SLEEP_SEC}s/件)")
    elif args.test:
        id_list = list(range(1, 21))
        print(f"スクレイピング開始: 1 〜 20  (待機 {SLEEP_SEC}s/件)")
    else:
        id_list = list(range(args.start, args.end + 1))
        print(f"スクレイピング開始: {args.start} 〜 {args.end}  (待機 {SLEEP_SEC}s/件)")
        if args.end == 1121:
            print(f"予想時間: 約 {int(1121 * SLEEP_SEC / 60)} 分")
    print()

    results = []
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0 (compatible; UNIDOL-scraper)"})

    for team_id in id_list:
        data = scrape_team(session, team_id)
        if data:
            results.append(data)
            line = (
                f"  [{team_id:4d}] {data['team_name']:<30} "
                f"| {data['reading_hiragana']:<30} "
                f"-> {data['reading_katakana']:<30} "
                f"| {data['year']:<12} {data['region']}"
            )
            print(line.encode(sys.stdout.encoding or "utf-8", errors="replace").decode(sys.stdout.encoding or "utf-8"))
        else:
            print(f"  [{team_id:4d}] -")
        time.sleep(SLEEP_SEC)

    # BOM付きUTF-8 → Excelで直接開いても文字化けしない
    output = "unidol_teams_reading.csv"
    with open(output, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n完了: {len(results)} チーム取得")
    print(f"出力: {output}")


if __name__ == "__main__":
    main()
