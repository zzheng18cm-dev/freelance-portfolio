"""
通用网页数据采集器 (Web Scraper)
--------------------------------
演示：多页翻页抓取 → 数据清洗 → 导出 CSV / Excel。
默认采集 https://books.toscrape.com （公开的爬虫练习站，稳定可跑），
换成其它列表页只需改 BASE_URL 和下面的解析选择器即可。

依赖: requests, beautifulsoup4 (Excel 导出可选 openpyxl)
    pip install requests beautifulsoup4 openpyxl
运行: python scraper.py
"""

import csv
import re
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Demo-Scraper/1.0"}
MAX_PAGES = 5          # 演示抓前 5 页，设为 None 抓到没有下一页为止
DELAY = 0.5            # 每页间隔，做个有礼貌的爬虫，避免给对方服务器压力

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def parse_page(html):
    """从一页 HTML 里解析出书籍列表。"""
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for item in soup.select("article.product_pod"):
        title = item.h3.a["title"].strip()
        price_raw = item.select_one("p.price_color").get_text(strip=True)
        m = re.search(r"[\d.]+", price_raw)          # 用正则取数字，避免货币符号/编码干扰
        price = float(m.group()) if m else 0.0
        rating_cls = item.select_one("p.star-rating")["class"][1]
        availability = item.select_one("p.instock.availability").get_text(strip=True)
        rows.append({
            "标题": title,
            "价格(£)": price,
            "评分": RATING_MAP.get(rating_cls, 0),
            "库存状态": availability,
        })
    return rows


def scrape():
    all_rows, page = [], 1
    while True:
        if MAX_PAGES and page > MAX_PAGES:
            break
        url = BASE_URL.format(page)
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"               # 强制 utf-8，避免 requests 猜错编码导致 £ 乱码
        if resp.status_code != 200:
            print(f"第 {page} 页返回 {resp.status_code}，停止。")
            break
        rows = parse_page(resp.text)
        if not rows:
            print(f"第 {page} 页无数据，结束。")
            break
        all_rows.extend(rows)
        print(f"已抓取第 {page} 页，本页 {len(rows)} 条，累计 {len(all_rows)} 条。")
        page += 1
        time.sleep(DELAY)
    return all_rows


def export_csv(rows, path="books.csv"):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"已导出 CSV: {path}")


def export_excel(rows, path="books.xlsx"):
    try:
        from openpyxl import Workbook
    except ImportError:
        print("未安装 openpyxl，跳过 Excel 导出（pip install openpyxl 可启用）。")
        return
    wb = Workbook()
    ws = wb.active
    ws.title = "books"
    headers = list(rows[0].keys())
    ws.append(headers)
    for r in rows:
        ws.append([r[h] for h in headers])
    wb.save(path)
    print(f"已导出 Excel: {path}")


if __name__ == "__main__":
    data = scrape()
    if data:
        export_csv(data)
        export_excel(data)
        print(f"\n完成，共 {len(data)} 条数据。")
    else:
        print("未抓到数据。")
