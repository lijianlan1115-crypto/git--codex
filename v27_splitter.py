import json
import sys

# 默认输入文件路径（使用项目内的副本，更稳定）
DEFAULT_FILE_PATH = "/Users/jelly/Public/trae-file/6.24考核/6.24考核工作流/repos/hotel--ota-ai/docs/architecture_reference/v27/酒店OTA_AI数字员工_协作开发总地图_V27_项目修复可执行契约版.json"

def split_v27(file_path):

    with open(file_path, "r", encoding="utf-8") as f:
        v27 = json.load(f)

    skills = []
    nodes = []
    mappings = []

    # ------------------------
    # 1. 提取 skills（字典格式）
    # ------------------------
    skills_data = v27.get("skills", {})
    if isinstance(skills_data, dict):
        for skill_id, skill_info in skills_data.items():
            skills.append({
                "id": skill_id,
                "name": skill_info.get("skill_name"),
                "desc": skill_info.get("description"),
                "agent_id": skill_info.get("agent_ids"),
                "node_ids": skill_info.get("node_ids", []),
                "blueprint_ids": skill_info.get("blueprint_ids", []),
                "inputs": skill_info.get("input_fields", []),
                "outputs": skill_info.get("output_fields", []),
                "runtime_commands": skill_info.get("runtime_commands", []),
                "acceptance": skill_info.get("acceptance", [])
            })
    elif isinstance(skills_data, list):
        for skill in skills_data:
            skills.append({
                "id": skill.get("id"),
                "name": skill.get("name"),
                "desc": skill.get("desc"),
                "input": skill.get("input", []),
                "output": skill.get("output", [])
            })

    # ------------------------
    # 2. 提取 nodes（字典格式）
    # ------------------------
    nodes_data = v27.get("nodes", {})
    if isinstance(nodes_data, dict):
        for node_id, node_info in nodes_data.items():
            nodes.append({
                "id": node_id,
                "name": node_info.get("node_name"),
                "maps_to": node_info.get("skill_id"),
                "agent_id": node_info.get("agent_id"),
                "phase": node_info.get("phase"),
                "module": node_info.get("module"),
                "layer": node_info.get("layer"),
                "inputs": node_info.get("inputs", []),
                "outputs": node_info.get("outputs", []),
                "downstream": node_info.get("downstream", []),
                "blueprint_ids": node_info.get("blueprint_ids", []),
                "algorithm_field_basis": node_info.get("algorithm_field_basis"),
                "source_field_basis": node_info.get("source_field_basis"),
                "canonical_outputs": node_info.get("canonical_outputs", [])
            })
    elif isinstance(nodes_data, list):
        for node in nodes_data:
            nodes.append({
                "id": node.get("id"),
                "name": node.get("name"),
                "maps_to": node.get("skill_id")
            })

    # ------------------------
    # 3. 提取 mapping（尝试多个可能的键名）
    # ------------------------
    # 尝试不同的键名
    file_mapping = v27.get("file_mapping", {}) or v27.get("mapping", {}) or v27.get("source_alias_mapping", {})
    
    if isinstance(file_mapping, dict):
        for file_name, skill_list in file_mapping.items():
            mappings.append({
                "file": file_name,
                "skill": skill_list
            })
    elif isinstance(file_mapping, list):
        for m in file_mapping:
            mappings.append({
                "file": m.get("file"),
                "skill": m.get("skills", [])
            })

    # ------------------------
    # 4. 输出文件
    # ------------------------
    with open("v27-skill.json", "w", encoding="utf-8") as f:
        json.dump(skills, f, indent=2, ensure_ascii=False)

    with open("v27-node.json", "w", encoding="utf-8") as f:
        json.dump(nodes, f, indent=2, ensure_ascii=False)

    with open("v27-mapping.json", "w", encoding="utf-8") as f:
        json.dump(mappings, f, indent=2, ensure_ascii=False)

    print("✔ V27拆分完成")
    print(f"  - 输入文件: {file_path}")
    print(f"  - 输出: v27-skill.json, v27-node.json, v27-mapping.json")


if __name__ == "__main__":
    # 如果命令行参数指定了文件路径，则使用指定路径
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        # 否则使用默认路径
        input_file = DEFAULT_FILE_PATH
    
    print(f"🚀 开始拆分 V27 文件...")
    print(f"  输入: {input_file}")
    
    try:
        split_v27(input_file)
    except FileNotFoundError:
        print(f"❌ 文件不存在: {input_file}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 拆分失败: {e}")
        sys.exit(1)