# 文件批量整理工具

把杂乱文件夹里的文件按**类型**（图片/文档/视频/音频/压缩包/程序/其它）自动归类，可选再按**修改月份**分层。

## 亮点
- **纯标准库**，零依赖，任何装了 Python 的电脑直接跑
- `--dry-run` 预览模式：先看会怎么移动，确认无误再执行，**防误操作**
- 重名自动加序号，**绝不覆盖**已有文件

## 运行
```bash
# 先预览（不会动文件）
python organize.py "C:/Users/你/Downloads" --by-date --dry-run

# 确认后执行
python organize.py "C:/Users/你/Downloads" --by-date
```

## 技术点
- pathlib 路径处理、shutil 移动文件
- argparse 命令行参数
- 防覆盖（unique_path）、dry-run 安全设计

## 可扩展
按文件名关键词归类、定时自动整理（配 Windows 计划任务）、重复文件检测、批量重命名规则。
