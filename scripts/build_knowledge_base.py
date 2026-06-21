#!/usr/bin/env python3
from pathlib import Path
from xml.etree import ElementTree
import argparse
import hashlib
import json
import re
import subprocess
import zipfile

DEFAULT_SOURCE_DIR = Path("/Users/jelly/Desktop/work/酒店数字员工")
DEFAULT_OUTPUT_DIR = Path("/Users/jelly/Public/trae-file/6.24考核/6.24考核工作流/knowledge_base")

TEXT_EXTS = {".md", ".txt", ".json", ".yaml", ".yml", ".csv", ".html", ".py", ".sql"}
OFFICE_EXTS = {".docx", ".xlsx"}
PDF_EXTS = {".pdf"}
SKIP_PARTS = {".git", "__pycache__", "venv", "logs"}


def should_skip(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts) or path.name.startswith(".DS_Store")


def clean_text(text: str) -> str:
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def read_text_file(path: Path) -> str:
    for encoding in ["utf-8", "utf-8-sig", "gb18030"]:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return ""


def extract_docx(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as zf:
            xml_text = zf.read("word/document.xml")
        root = ElementTree.fromstring(xml_text)
        texts = []
        for node in root.iter():
            if node.tag.endswith("}t") and node.text:
                texts.append(node.text)
        return "\n".join(texts)
    except Exception as exc:
        return f"[DOCX解析失败] {exc}"


def extract_xlsx(path: Path, max_cells: int = 1200) -> str:
    try:
        values = []
        with zipfile.ZipFile(path) as zf:
            shared_strings = []
            if "xl/sharedStrings.xml" in zf.namelist():
                root = ElementTree.fromstring(zf.read("xl/sharedStrings.xml"))
                for item in root.iter():
                    if item.tag.endswith("}t") and item.text:
                        shared_strings.append(item.text)

            sheet_names = [name for name in zf.namelist() if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")]
            for sheet_name in sheet_names:
                values.append(f"\n## {sheet_name}")
                root = ElementTree.fromstring(zf.read(sheet_name))
                for cell in root.iter():
                    if not cell.tag.endswith("}c"):
                        continue
                    cell_type = cell.attrib.get("t")
                    ref = cell.attrib.get("r", "")
                    value_node = next((child for child in cell if child.tag.endswith("}v")), None)
                    if value_node is None or value_node.text is None:
                        continue
                    value = value_node.text
                    if cell_type == "s":
                        try:
                            value = shared_strings[int(value)]
                        except Exception:
                            pass
                    values.append(f"{ref}: {value}")
                    if len(values) >= max_cells:
                        values.append("[内容过长，已截断]")
                        return "\n".join(values)
        return "\n".join(values)
    except Exception as exc:
        return f"[XLSX解析失败] {exc}"


def extract_pdf(path: Path) -> str:
    try:
        result = subprocess.run(
            ["pdftotext", str(path), "-"],
            text=True,
            capture_output=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
    except Exception:
        pass
    return "[PDF文本未抽取] 建议安装 poppler：brew install poppler，或手动转为 Markdown。"


def extract_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in TEXT_EXTS:
        return read_text_file(path)
    if suffix == ".docx":
        return extract_docx(path)
    if suffix == ".xlsx":
        return extract_xlsx(path)
    if suffix == ".pdf":
        return extract_pdf(path)
    return ""


def classify(path: Path, text: str) -> str:
    blob = f"{path} {text[:1000]}".lower()
    if "需求" in blob or "requirement" in blob:
        return "需求文档"
    if "功能逻辑" in blob or "算法" in blob:
        return "功能蓝图"
    if "字段" in blob or "契约" in blob or "schema" in blob:
        return "字段契约"
    if "测试" in blob or "验收" in blob:
        return "测试验收"
    if "agent" in blob or "技能" in blob:
        return "Agent技能"
    if path.suffix.lower() in {".xlsx", ".csv"}:
        return "数据样例"
    return "项目资料"


def keywords_for(path: Path, text: str):
    candidates = [
        "价格",
        "库存",
        "收益",
        "RevPAR",
        "ADR",
        "OCC",
        "OTA",
        "渠道",
        "房态",
        "订单",
        "字段",
        "Agent",
        "测试",
        "验收",
        "飞书",
        "PMS",
        "OpenClaw",
        "诊断",
    ]
    blob = f"{path.name}\n{text[:3000]}".lower()
    return [word for word in candidates if word.lower() in blob]


def chunk_text(text: str, max_chars: int = 5000):
    text = clean_text(text)
    if not text:
        return []
    return [text[i : i + max_chars] for i in range(0, len(text), max_chars)]


def build(source_dir: Path, output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)
    chunks_dir = output_dir / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    manifest = []
    index = []

    for path in sorted(source_dir.rglob("*")):
        if not path.is_file() or should_skip(path):
            continue
        if path.suffix.lower() not in TEXT_EXTS | OFFICE_EXTS | PDF_EXTS:
            continue

        text = extract_file(path)
        if not text.strip():
            continue

        rel = path.relative_to(source_dir)
        digest = hashlib.sha1(str(rel).encode("utf-8")).hexdigest()[:12]
        doc_type = classify(path, text)
        kws = keywords_for(path, text)
        chunks = chunk_text(text)

        manifest.append(
            {
                "source_path": str(path),
                "relative_path": str(rel),
                "type": doc_type,
                "keywords": kws,
                "chunks": len(chunks),
            }
        )

        for idx, chunk in enumerate(chunks, start=1):
            chunk_name = f"{digest}-{idx:03d}.md"
            chunk_path = chunks_dir / chunk_name
            chunk_path.write_text(
                f"# {rel}\n\n类型：{doc_type}\n关键词：{', '.join(kws) or '无'}\n\n---\n\n{chunk}\n",
                encoding="utf-8",
            )
            index.append(
                {
                    "chunk": str(chunk_path),
                    "source_path": str(path),
                    "relative_path": str(rel),
                    "type": doc_type,
                    "keywords": kws,
                    "preview": clean_text(chunk[:300]),
                }
            )

    (output_dir / "source_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    summary_lines = [
        "# Codex 本地知识库索引",
        "",
        f"资料来源：{source_dir}",
        f"文档数量：{len(manifest)}",
        f"知识片段：{len(index)}",
        "",
        "## 使用方式",
        "",
        "Codex 修改或分析代码前，先读取本文件，再按关键词从 `knowledge_base/chunks/` 读取相关片段。",
        "",
        "## 资料清单",
        "",
    ]
    for item in manifest[:200]:
        summary_lines.append(f"- [{item['type']}] {item['relative_path']} | 关键词：{', '.join(item['keywords']) or '无'} | chunks：{item['chunks']}")

    (output_dir / "CODEX_KNOWLEDGE.md").write_text("\n".join(summary_lines), encoding="utf-8")
    return {"documents": len(manifest), "chunks": len(index), "output_dir": str(output_dir)}


def main():
    parser = argparse.ArgumentParser(description="把酒店数字员工资料整理成本地 Codex 知识库")
    parser.add_argument("--source", default=str(DEFAULT_SOURCE_DIR), help="资料来源目录")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_DIR), help="知识库输出目录")
    args = parser.parse_args()

    result = build(Path(args.source), Path(args.output))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
