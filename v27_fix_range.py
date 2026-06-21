#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 V27 文件中的范围表达问题
将 "N005-N021" 格式拆分为单独的节点引用
"""

import json
import re

def parse_node_range(node_str):
    """解析节点范围表达式，返回所有节点列表"""
    # 匹配范围模式 Nxxx-Nyyy
    range_pattern = re.compile(r'N(\d{3})-N(\d{3})')
    match = range_pattern.match(node_str.strip())
    
    if match:
        start = int(match.group(1))
        end = int(match.group(2))
        return [f"N{i:03d}" for i in range(start, end + 1)]
    else:
        # 不是范围，返回原节点
        return [node_str.strip()]

def fix_edge_file(input_file="v27-edge.json", output_file="v27-edge.json"):
    """修复 edge 文件中的范围表达"""
    with open(input_file, "r", encoding="utf-8") as f:
        edges = json.load(f)
    
    fixed_edges = []
    
    for edge in edges:
        from_node = edge["from"]
        to_node = edge["to"]
        
        # 解析 from 节点（通常不会是范围，但以防万一）
        from_nodes = parse_node_range(from_node)
        
        # 解析 to 节点
        to_nodes = parse_node_range(to_node)
        
        # 生成所有组合
        for f in from_nodes:
            for t in to_nodes:
                if f != t:  # 排除自环
                    fixed_edges.append({
                        "from": f,
                        "to": t,
                        "type": edge["type"]
                    })
    
    # 去重（保持顺序）
    seen = set()
    result = []
    for edge in fixed_edges:
        key = f"{edge['from']}->{edge['to']}->{edge['type']}"
        if key not in seen:
            seen.add(key)
            result.append(edge)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 修复 edge 文件: {len(edges)} → {len(result)} 条边")
    return result

def fix_field_file(input_file="v27-field.json", output_file="v27-field.json"):
    """修复 field 文件中的范围表达"""
    with open(input_file, "r", encoding="utf-8") as f:
        fields = json.load(f)
    
    fixed_fields = []
    
    for field in fields:
        field_name = field["field"]
        affects = field["affects"]
        
        # 展开所有范围表达
        expanded_affects = []
        for node in affects:
            expanded_affects.extend(parse_node_range(node))
        
        # 去重（保持顺序）
        seen = set()
        unique_affects = []
        for node in expanded_affects:
            if node not in seen:
                seen.add(node)
                unique_affects.append(node)
        
        fixed_fields.append({
            "field": field_name,
            "affects": unique_affects
        })
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(fixed_fields, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 修复 field 文件: {len(fields)} 个字段，展开了范围表达")
    return fixed_fields

def main():
    print("🚀 开始修复 V27 文件中的范围表达...")
    print()
    
    fix_edge_file()
    fix_field_file()
    
    print()
    print("🎉 修复完成！")
    print("   - v27-edge.json: 范围表达已拆分为标准边")
    print("   - v27-field.json: 范围表达已拆分为标准节点ID")

if __name__ == "__main__":
    main()