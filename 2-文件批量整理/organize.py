"""
文件批量整理工具 (File Organizer)
---------------------------------
把一个杂乱文件夹里的文件，按类型自动归类到子文件夹（图片/文档/视频/音频/压缩包/其它），
可选按修改月份再分一层。支持 --dry-run 预览（不真正移动），安全防误操作。

纯 Python 标准库，无需安装任何依赖。
运行: python organize.py "C:/要整理的文件夹" --by-date --dry-run
去掉 --dry-run 才会真正移动。
"""

import argparse
import shutil
from pathlib import Path
from datetime import datetime

CATEGORIES = {
    "图片": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".heic"},
    "文档": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".csv"},
    "视频": {".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv"},
    "音频": {".mp3", ".wav", ".flac", ".aac", ".m4a"},
    "压缩包": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "程序": {".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".go", ".json"},
}


def category_of(suffix):
    suffix = suffix.lower()
    for name, exts in CATEGORIES.items():
        if suffix in exts:
            return name
    return "其它"


def unique_path(target: Path) -> Path:
    """目标已存在时自动加序号，避免覆盖。"""
    if not target.exists():
        return target
    stem, suffix, i = target.stem, target.suffix, 1
    while True:
        cand = target.with_name(f"{stem}_{i}{suffix}")
        if not cand.exists():
            return cand
        i += 1


def organize(folder: str, by_date: bool, dry_run: bool):
    base = Path(folder)
    if not base.is_dir():
        print(f"目录不存在: {folder}")
        return
    moved = 0
    for f in base.iterdir():
        if f.is_dir() or f.name.startswith("."):
            continue
        cat = category_of(f.suffix)
        dest_dir = base / cat
        if by_date:
            month = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m")
            dest_dir = dest_dir / month
        dest = unique_path(dest_dir / f.name)
        print(f"{'[预览] ' if dry_run else ''}{f.name}  ->  {dest.relative_to(base)}")
        if not dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(f), str(dest))
        moved += 1
    print(f"\n{'将整理' if dry_run else '已整理'} {moved} 个文件。"
          + ("（预览模式，未实际移动，去掉 --dry-run 执行）" if dry_run else ""))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="按类型/日期批量整理文件夹")
    ap.add_argument("folder", help="要整理的文件夹路径")
    ap.add_argument("--by-date", action="store_true", help="在类型下再按修改月份分子文件夹")
    ap.add_argument("--dry-run", action="store_true", help="只预览不实际移动")
    args = ap.parse_args()
    organize(args.folder, args.by_date, args.dry_run)
