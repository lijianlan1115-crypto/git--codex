#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V27 关键数据提取器
提取：
1. v27-edge.json - 影响传播分析
2. v27-field.json - 指标影响分析
"""

import json
import sys

# 默认输入文件路径
DEFAULT_FILE_PATH = "/Users/jelly/Public/trae-file/6.24考核/6.24考核工作流/repos/hotel--ota-ai/docs/architecture_reference/v27/酒店OTA_AI数字员工_协作开发总地图_V27_项目修复可执行契约版.json"

def extract_edges(data):
    """提取边数据，用于影响传播分析"""
    edges = []
    
    # 从 edges 字段提取
    edges_data = data.get("edges", {})
    if isinstance(edges_data, dict):
        for edge_id, edge_info in edges_data.items():
            from_node = edge_info.get("from_node")
            to_node = edge_info.get("to_node")
            edge_type = edge_info.get("edge_type", "data_flow")
            
            if from_node and to_node:
                edges.append({
                    "from": from_node,
                    "to": to_node,
                    "type": edge_type
                })
    
    # 如果 edges 为空，尝试从 nodes 的 downstream 构建
    if not edges:
        nodes = data.get("nodes", {})
        if isinstance(nodes, dict):
            for node_id, node_info in nodes.items():
                downstream = node_info.get("downstream", [])
                if downstream:
                    for target_node in downstream:
                        # 清理下游节点名称（可能包含 "或" 等文字）
                        target_clean = target_node.strip().split()[0].split("或")[0]
                        if target_clean and target_clean != node_id:
                            edges.append({
                                "from": node_id,
                                "to": target_clean,
                                "type": "data_flow"
                            })
    
    return edges

def extract_fields(data):
    """提取字段影响关系，用于指标影响分析"""
    fields = {}
    
    # 从 field_registry 提取字段信息
    field_registry = data.get("field_registry", {})
    if isinstance(field_registry, dict):
        for field_id, field_info in field_registry.items():
            field_name = field_info.get("zh_name", field_id)
            downstream_nodes = field_info.get("downstream_node", [])
            
            if downstream_nodes:
                affected_skills = []
                for node in downstream_nodes:
                    # 从节点找到对应的技能
                    node_clean = node.strip().split()[0].split("或")[0]
                    if node_clean:
                        affected_skills.append(node_clean)
                
                if affected_skills:
                    fields[field_name] = affected_skills
    
    # 转换为列表格式
    result = []
    for field_name, affects in fields.items():
        result.append({
            "field": field_name,
            "affects": affects
        })
    
    return result

def main():
    # 获取输入文件路径
    input_file = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FILE_PATH
    
    print(f"🚀 开始提取 V27 关键数据...")
    print(f"  输入: {input_file}")
    
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 1. 提取 edges
        print("\n📊 提取 edges...")
        edges = extract_edges(data)
        with open("v27-edge.json", "w", encoding="utf-8") as f:
            json.dump(edges, f, indent=2, ensure_ascii=False)
        print(f"✅ v27-edge.json: {len(edges)} 条边")
        
        # 2. 提取 fields
        print("\n📊 提取 fields...")
        fields = extract_fields(data)
        with open("v27-field.json", "w", encoding="utf-8") as f:
            json.dump(fields, f, indent=2, ensure_ascii=False)
        print(f"✅ v27-field.json: {len(fields)} 个字段")
        
        print("\n🎉 提取完成！")
        
    except FileNotFoundError:
        print(f"❌ 文件不存在: {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 提取失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()