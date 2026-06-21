import pandas as pd
from pathlib import Path

excel_path = Path("/Users/jelly/Desktop/work/酒店数字员工/酒店OTA全面诊断系统_开发交付总文档_v2_精简版.xlsx")
output_path = Path("/Users/jelly/Desktop/work/酒店数字员工/酒店OTA全面诊断系统_开发交付总文档_v2_精简版.md")

xls = pd.ExcelFile(excel_path)
parts = []

for sheet_name in xls.sheet_names:
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    df = df.fillna("")
    parts.append(f"# Sheet：{sheet_name}\n")
    parts.append(df.to_markdown(index=False))
    parts.append("\n\n")

output_path.write_text("\n".join(parts), encoding="utf-8")

print(f"已生成：{output_path}")