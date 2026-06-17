# 通用网页数据采集器

一个 Python 爬虫示例：多页翻页抓取列表数据 → 清洗 → 导出 CSV / Excel。

## 功能
- 自动翻页抓取，可设置最大页数
- 解析标题、价格、评分、库存等字段
- 内置请求间隔（有礼貌的爬虫，降低被封风险）
- 一键导出 CSV（带 BOM，Excel 直接打开不乱码）+ Excel

## 运行
```bash
pip install requests beautifulsoup4 openpyxl
python scraper.py
```
运行后在当前目录生成 `books.csv` 和 `books.xlsx`。

## 技术点
- requests 发请求 + 自定义 User-Agent
- BeautifulSoup CSS 选择器解析 DOM
- 数据类型清洗（价格转 float、评分文字转数字）
- csv / openpyxl 导出

## 可定制
换目标站点只需改 `BASE_URL` 和 `parse_page()` 里的选择器。可扩展：代理池、并发、增量去重、入库（MySQL/MongoDB）、定时任务。

> 演示站点用的是公开的爬虫练习站 books.toscrape.com，稳定可复现。实际接单会按目标站点的结构和反爬策略定制。
