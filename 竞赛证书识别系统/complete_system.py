"""
完整系统主程序（命令行辅助脚本）
功能：初始化数据库、设置截止时间、导出数据示例、启动 Streamlit 界面
"""
from __future__ import annotations
import argparse
import os
import subprocess
from datetime import datetime

from database import init_db
from admin_panel import set_deadline, export_all_csv, export_all_excel


def main():
    parser = argparse.ArgumentParser(description="竞赛证书识别系统 管理脚本")
    parser.add_argument("--init-db", action="store_true", help="初始化数据库并创建管理员")
    parser.add_argument("--set-deadline", type=str, help="设置提交截止时间（ISO 格式，例如 2025-01-15T23:59:59）")
    parser.add_argument("--export-csv", type=str, help="将已提交数据导出为CSV，指定输出路径")
    parser.add_argument("--export-xlsx", type=str, help="将已提交数据导出为Excel，指定输出路径")
    parser.add_argument("--run-ui", action="store_true", help="使用 Streamlit 运行 Web 界面（调用: streamlit run app.py）")

    args = parser.parse_args()

    if args.init_db:
        init_db()
        print("数据库已初始化并确保管理员存在。")

    if args.set_deadline:
        ok = set_deadline(args.set_deadline)
        if ok:
            print(f"截止时间已设置：{args.set_deadline}")

    if args.export_csv:
        out = export_all_csv(args.export_csv)
        print(f"CSV 导出完成：{out}")

    if args.export_xlsx:
        out = export_all_excel(args.export_xlsx)
        print(f"Excel 导出完成：{out}")

    if args.run_ui:
        print("启动 Streamlit 应用：streamlit run app.py")
        # 使用 subprocess 调用，用户需要在终端中执行；这里尝试直接启动
        try:
            subprocess.run(["streamlit", "run", "app.py"], check=False)
        except FileNotFoundError:
            print("未找到 streamlit。请先安装并在终端中运行：pip install streamlit，然后执行：streamlit run app.py")


if __name__ == "__main__":
    main()
