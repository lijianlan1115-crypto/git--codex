#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 V27 JSON 文件转换为 Markdown 格式
"""

import json
import os

def json_to_md(json_file, md_file):
    """将单个 JSON 文件转换为 Markdown"""
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    md_lines = []
    md_lines.append(f"# {os.path.basename(json_file).replace('.json', '').replace('-', ' ').title()}")
    md_lines.append("")
    md_lines.append(f"共 **{len(data)}** 条记录")
    md_lines.append("")
    
    if isinstance(data, list) and data:
        first_item = data[0]
        if isinstance(first_item, dict):
            keys = list(first_item.keys())
            
            # 表格格式
            md_lines.append("| " + " | ".join(keys) + " |")
            md_lines.append("| " + " | ".join(["---"] * len(keys)) + " |")
            
            for item in data:
                row = []
                for key in keys:
                    value = item.get(key, "")
                    if isinstance(value, list):
                        value = ", ".join(str(v) for v in value)  # 显示全部
                    elif isinstance(value, dict):
                        value = json.dumps(value, ensure_ascii=False)[:50] + "..."
                    row.append(str(value)[:200])  # 适当放宽长度限制
                md_lines.append("| " + " | ".join(row) + " |")
        else:
            # 简单列表
            for i, item in enumerate(data, 1):
                md_lines.append(f"{i}. {item}")
    
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    
    print(f"✅ {json_file} → {md_file}")

def main():
    print("🚀 开始将 JSON 转换为 Markdown...")
    
    files = [
        ("v27-skill.json", "v27-skill.md"),
        ("v27-node.json", "v27-node.md"),
        ("v27-mapping.json", "v27-mapping.md"),
        ("v27-edge.json", "v27-edge.md"),
        ("v27-field.json", "v27-field.md")
    ]
    
    for json_file, md_file in files:
        if os.path.exists(json_file):
            json_to_md(json_file, md_file)
        else:
            print(f"⚠️ 文件不存在: {json_file}")
    
    print("\n🎉 转换完成！")

if __name__ == "__main__":
    main()