from fastapi import FastAPI, Header, HTTPException
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime
import base64
import json
import os
import subprocess

app = FastAPI(title="Codex研发协同变更分析与测试预警工作流")

# =========================
# 配置
# =========================

BASE_DIR = Path("/Users/jelly/Public/trae-file/6.24考核/6.24考核工作流")
REPOS_DIR = BASE_DIR / "repos"
OUTPUTS_DIR = BASE_DIR / "outputs"
KNOWLEDGE_DIR = BASE_DIR / "knowledge_base"
RUNNER_PATH = BASE_DIR / "codex_runner.sh"
DEFAULT_REPO_NAME = "hotel--ota-ai"

# 启动服务前建议设置：
# export COZE_TOKEN="换成一个很长的随机字符串"
API_TOKEN = os.getenv("COZE_TOKEN", "change-me-to-a-long-random-token")

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# V27 数据加载
# =========================

V27_DATA = {
    "edges": [],
    "fields": [],
    "skills": [],
    "nodes": [],
    "mapping": [],
}


def load_v27_data():
    files = {
        "edges": "v27-edge.json",
        "fields": "v27-field.json",
        "skills": "v27-skill.json",
        "nodes": "v27-node.json",
        "mapping": "v27-mapping.json",
    }

    for key, filename in files.items():
        file_path = BASE_DIR / filename
        if not file_path.exists():
            print(f"未找到 {filename}")
            continue

        try:
            V27_DATA[key] = json.loads(file_path.read_text(encoding="utf-8"))
            print(f"加载 {filename}: {len(V27_DATA[key])}")
        except Exception as e:
            print(f"加载失败 {filename}: {e}")


load_v27_data()


# =========================
# 通用工具
# =========================


def verify_token(authorization: str):
    if not API_TOKEN or API_TOKEN == "change-me-to-a-long-random-token":
        raise HTTPException(status_code=500, detail="服务端未配置 COZE_TOKEN")

    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="unauthorized")


def run_command(args: List[str], cwd: Path, timeout: int = 60):
    result = subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        timeout=timeout,
    )
    output = ((result.stdout or "") + "\n" + (result.stderr or "")).strip()
    return result.returncode, output


def resolve_repo_dir(repo: str = "") -> Path:
    repo_value = repo or DEFAULT_REPO_NAME
    repo_path = Path(repo_value)

    if repo_path.is_absolute():
        resolved = repo_path.resolve()
    else:
        resolved = (REPOS_DIR / repo_value).resolve()

    repos_root = REPOS_DIR.resolve()
    if repos_root != resolved and repos_root not in resolved.parents:
        raise HTTPException(status_code=400, detail="repo 必须位于 repos 目录内")

    if not resolved.exists():
        raise HTTPException(status_code=404, detail=f"仓库不存在: {resolved}")

    return resolved


def normalize_files(files: Any) -> List[str]:
    if not files:
        return []
    if isinstance(files, str):
        return [files]
    if isinstance(files, list):
        return [str(item) for item in files]
    return [str(files)]


def truncate_text(text: str, limit: int = 12000) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[内容过长已截断]"


def load_knowledge_context(query: str, limit: int = 4) -> str:
    """从本地知识库中挑选与需求最相关的片段给 Codex。

    知识库由 scripts/build_knowledge_base.py 从
    /Users/jelly/Desktop/work/酒店数字员工 抽取生成。
    """
    index_path = KNOWLEDGE_DIR / "index.json"
    summary_path = KNOWLEDGE_DIR / "CODEX_KNOWLEDGE.md"
    if not index_path.exists():
        return "本地知识库尚未生成。可运行 scripts/build_knowledge_base.py 生成。"

    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return f"本地知识库索引读取失败：{exc}"

    query_lower = (query or "").lower()
    scored = []
    for item in index:
        haystack = " ".join(
            [
                item.get("relative_path", ""),
                item.get("type", ""),
                " ".join(item.get("keywords", [])),
                item.get("preview", ""),
            ]
        ).lower()
        score = 0
        for token in re_split_query(query_lower):
            if token and token in haystack:
                score += 1
        if score:
            scored.append((score, item))

    if not scored:
        scored = [(1, item) for item in index[:limit]]

    scored.sort(key=lambda pair: pair[0], reverse=True)
    chunks = []
    if summary_path.exists():
        chunks.append(truncate_text(summary_path.read_text(encoding="utf-8"), 2500))

    for _, item in scored[:limit]:
        chunk_path = Path(item["chunk"])
        if chunk_path.exists():
            chunks.append(truncate_text(chunk_path.read_text(encoding="utf-8"), 3500))

    return "\n\n---\n\n".join(chunks)


def re_split_query(query: str) -> List[str]:
    raw_tokens = query.replace("/", " ").replace("_", " ").replace("-", " ").split()
    important = [
        "价格",
        "库存",
        "收益",
        "渠道",
        "订单",
        "房态",
        "测试",
        "验收",
        "字段",
        "agent",
        "ota",
        "adr",
        "revpar",
        "occ",
        "pms",
        "openclaw",
    ]
    return list(dict.fromkeys(raw_tokens + important))


# =========================
# Git 能力
# =========================


def git_status(repo_dir: Path) -> str:
    _, output = run_command(["git", "status", "--short"], repo_dir)
    return output


def git_recent_log(repo_dir: Path, limit: int = 5) -> str:
    _, output = run_command(["git", "log", f"-{limit}", "--pretty=format:%h|%an|%ad|%s", "--date=iso"], repo_dir)
    return output


def git_worktree_diff(repo_dir: Path) -> str:
    _, output = run_command(["git", "diff", "--"], repo_dir)
    if output:
        return output

    _, staged = run_command(["git", "diff", "--cached", "--"], repo_dir)
    return staged


def git_commit_diff(repo_dir: Path, commit: str) -> str:
    if not commit:
        return ""
    _, output = run_command(["git", "show", "--format=fuller", "--stat", "--patch", commit], repo_dir)
    return output


def git_changed_files(repo_dir: Path, commit: str = "") -> List[str]:
    if commit:
        _, output = run_command(["git", "show", "--name-only", "--format=", commit], repo_dir)
    else:
        _, output = run_command(["git", "diff", "--name-only"], repo_dir)
    return [line.strip() for line in output.splitlines() if line.strip()]


def git_pull(repo_dir: Path):
    return run_command(["git", "pull", "--ff-only"], repo_dir, timeout=120)


# =========================
# Codex CLI 调用
# =========================


def call_codex_cli(prompt: str, repo_dir: Path, mode: str = "analyze", timeout: int = 300):
    """通过本地 runner 调用 Codex CLI。

    mode=analyze 使用 read-only；mode=apply 使用 workspace-write。
    """
    if not RUNNER_PATH.exists():
        return {"success": False, "error": f"runner 不存在: {RUNNER_PATH}", "raw": ""}

    if not os.access(RUNNER_PATH, os.X_OK):
        return {"success": False, "error": f"runner 不可执行，请先 chmod +x: {RUNNER_PATH}", "raw": ""}

    encoded_prompt = base64.b64encode(prompt.encode("utf-8")).decode("ascii")

    env = os.environ.copy()
    env.update(
        {
            "HOME": "/Users/jelly",
            "PATH": "/opt/homebrew/bin:/Users/jelly/.npm-global/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
            "USER": "jelly",
            "LOGNAME": "jelly",
            "SHELL": "/bin/zsh",
            "TERM": "xterm-256color",
            "LANG": "zh_CN.UTF-8",
            "LC_ALL": "zh_CN.UTF-8",
        }
    )

    try:
        result = subprocess.run(
            [str(RUNNER_PATH), mode, encoded_prompt, str(repo_dir)],
            cwd=str(repo_dir),
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout,
        )

        output = ((result.stdout or "") + "\n" + (result.stderr or "")).strip()
        return {
            "success": result.returncode == 0,
            "raw": output[:12000],
            "error": "" if result.returncode == 0 else output[:4000],
            "returncode": result.returncode,
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Codex 执行超时", "raw": ""}
    except Exception as e:
        return {"success": False, "error": str(e), "raw": ""}


# =========================
# V27 业务影响映射
# =========================

KEYWORDS = [
    "adr",
    "revpar",
    "occ",
    "price",
    "revenue",
    "booking",
    "hotel",
    "room",
    "inventory",
    "rate",
    "收入",
    "价格",
    "库存",
    "订单",
    "利润",
    "酒店",
    "房型",
    "渠道",
]


def extract_keywords(text: str):
    lower_text = (text or "").lower()
    return [keyword.upper() if keyword.isascii() else keyword for keyword in KEYWORDS if keyword.lower() in lower_text]


def node_search_blob(node: Dict[str, Any]) -> str:
    parts = [
        node.get("id", ""),
        node.get("name", ""),
        node.get("module", ""),
        node.get("layer", ""),
        node.get("agent_id", ""),
        json.dumps(node.get("inputs", []), ensure_ascii=False),
        json.dumps(node.get("outputs", []), ensure_ascii=False),
    ]
    return " ".join(str(part) for part in parts).lower()


def infer_affected_nodes(diff_text: str, files: List[str]) -> List[str]:
    text = " ".join([diff_text or "", " ".join(files)]).lower()
    matched = []

    for node in V27_DATA["nodes"]:
        blob = node_search_blob(node)
        if any(keyword.lower() in text and keyword.lower() in blob for keyword in KEYWORDS):
            matched.append(node.get("id"))

    for field in V27_DATA["fields"]:
        field_name = str(field.get("field", "")).lower()
        if field_name and field_name in text:
            matched.extend(field.get("affects", []))

    if not matched:
        # 兜底：代码变更通常先影响权限/数据/策略链路，便于演示继续向下传播。
        matched = ["N004", "N005"]

    return sorted({node_id for node_id in matched if node_id})


def propagate_nodes(affected_nodes: List[str]) -> List[str]:
    propagated = list(affected_nodes)
    frontier = list(affected_nodes)

    while frontier:
        current = frontier.pop(0)
        for edge in V27_DATA["edges"]:
            if edge.get("from") != current:
                continue
            target = edge.get("to")
            if target and target not in propagated:
                propagated.append(target)
                frontier.append(target)

    return propagated


def describe_nodes(node_ids: List[str]) -> List[Dict[str, Any]]:
    node_map = {node.get("id"): node for node in V27_DATA["nodes"]}
    descriptions = []

    for node_id in node_ids:
        node = node_map.get(node_id, {})
        descriptions.append(
            {
                "id": node_id,
                "name": node.get("name", ""),
                "module": node.get("module", ""),
                "layer": node.get("layer", ""),
                "agent_id": node.get("agent_id", ""),
            }
        )

    return descriptions


def analyze_v27_impact(diff_text: str, files: List[str], requirement: str = ""):
    combined_text = "\n".join([requirement or "", diff_text or "", "\n".join(files)])
    keywords = extract_keywords(combined_text)
    affected_nodes = infer_affected_nodes(combined_text, files)
    propagated = propagate_nodes(affected_nodes)

    risk = "low"
    if len(files) >= 3 or len(propagated) > 5:
        risk = "medium"
    if len(files) >= 6 or len(propagated) > 10 or any(k in keywords for k in ["REVENUE", "PRICE", "库存", "价格", "收入"]):
        risk = "high"

    test_cases = [f"检查节点 {node['id']} {node['name']} 的输入输出是否符合预期" for node in describe_nodes(propagated[:5])]
    for keyword in keywords[:5]:
        test_cases.append(f"验证业务指标 {keyword} 的计算、展示和边界值")

    lines_changed = diff_text.count("\n") if diff_text else 0
    estimated_hours = max(1, min(32, lines_changed // 40 or len(files) or 1))

    return {
        "keywords": keywords,
        "affected_nodes": affected_nodes,
        "affected_node_details": describe_nodes(affected_nodes),
        "propagated_nodes": propagated,
        "propagated_node_details": describe_nodes(propagated),
        "scope": len(propagated),
        "risk_level": risk,
        "test_cases": test_cases,
        "estimated_cost": {"hours": estimated_hours, "complexity": risk},
    }


# =========================
# Prompt 和报告
# =========================


def build_analyze_prompt(requirement: str, diff_text: str, files: List[str], recent_log: str, status: str):
    knowledge_context = load_knowledge_context("\n".join([requirement or "", diff_text[:2000], " ".join(files)]))
    return f"""你是研发协同变更分析助手。请基于需求、Git diff、提交记录和项目结构，输出适合开发与测试同步的分析。

要求：
1. 说明改了什么或准备改什么。
2. 识别影响文件、影响模块、输入输出、配置、工作区、Agent 或测试环境。
3. 判断是否影响其他开发人员和测试人员。
4. 给出风险等级：low / medium / high。
5. 生成验证方案：测试什么、怎么测、通过标准、失败标准。
6. 不要编造不存在的代码事实；不确定时标记“需人工确认”。

本地知识库上下文：
{knowledge_context}

需求变更：
{requirement or "未提供"}

当前 Git 状态：
{status or "无"}

最近提交：
{recent_log or "无"}

涉及文件：
{", ".join(files) if files else "未指定"}

Git diff：
{truncate_text(diff_text, 20000) or "无 diff，需根据需求和代码结构推断"}
"""


def build_apply_prompt(requirement: str, files: List[str], recent_log: str, status: str):
    knowledge_context = load_knowledge_context("\n".join([requirement or "", " ".join(files)]))
    return f"""你是 Codex 代码修改助手。请在当前 Git 仓库中实现下面的需求变更。

工作要求：
1. 先阅读相关代码和项目结构，再修改必要文件。
2. 只修改与需求直接相关的代码和文档，不做无关重构。
3. 修改完成后说明改了哪些文件、为什么改、如何验证。
4. 如果需求信息不足，优先做最小可行修改，并在结果中列出需人工确认点。
5. 不提交 git commit。

本地知识库上下文：
{knowledge_context}

需求变更：
{requirement}

建议关注文件：
{", ".join(files) if files else "由你根据项目结构判断"}

当前 Git 状态：
{status or "无"}

最近提交：
{recent_log or "无"}
"""


def render_markdown_report(title: str, payload: Dict[str, Any]) -> str:
    impact = payload.get("impact", {})
    codex = payload.get("codex", {})
    input_data = payload.get("input", {})
    files = input_data.get("files", [])

    node_lines = []
    for node in impact.get("propagated_node_details", [])[:12]:
        node_lines.append(f"- {node.get('id')} {node.get('name')} | {node.get('module')} | {node.get('agent_id')}")

    test_lines = [f"- {item}" for item in payload.get("test_cases", [])]

    return f"""# {title}

生成时间：{payload.get("generated_at", "")}

## 1. 变更内容

- 仓库：{input_data.get("repo", "")}
- 分支：{input_data.get("branch", "")}
- 提交：{input_data.get("commit", "")}
- 需求：{input_data.get("requirement", "") or "未提供"}
- 修改文件：{", ".join(files) if files else "未指定"}

## 2. 影响范围

- 风险等级：{payload.get("risk_level")}
- 影响节点数量：{impact.get("scope")}
- 命中关键词：{", ".join(impact.get("keywords", [])) or "无"}

{chr(10).join(node_lines) if node_lines else "- 暂无节点命中"}

## 3. 协同风险

- 是否影响其他开发：{"是，需同步相关模块负责人" if payload.get("risk_level") in ["medium", "high"] else "低概率，仍建议同步变更说明"}
- 是否影响测试：是，需按测试清单回归验证
- 是否影响正式环境：{"高风险，发布前需增加验收" if payload.get("risk_level") == "high" else "需按常规发布流程确认"}
- 是否影响其他工作区：需结合分支和部署环境确认

## 4. 验证方案

{chr(10).join(test_lines) if test_lines else "- 暂无测试项"}

## 5. 通过标准

- 相关单元测试、接口测试或人工验收通过。
- V27 影响节点的关键输入输出符合预期。
- 未出现新增异常、数据缺失或权限绕过。
- 开发、测试已确认协同风险。

## 6. 失败标准

- 修改后关键指标计算异常。
- 相关 Agent、节点或字段契约不一致。
- 测试环境出现回归问题。
- Codex 输出中存在未解决的需人工确认点。

## 7. Codex 分析结果

```text
{codex.get("raw", "") or codex.get("error", "") or "未调用 Codex"}
```
"""


def save_outputs(name: str, payload: Dict[str, Any]):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    json_path = OUTPUTS_DIR / f"{name}-{timestamp}.json"
    md_path = OUTPUTS_DIR / f"{name}-{timestamp}.md"
    latest_json_path = OUTPUTS_DIR / f"{name}-latest.json"
    latest_md_path = OUTPUTS_DIR / f"{name}-latest.md"

    markdown = render_markdown_report(payload.get("title", "变更分析报告"), payload)
    json_text = json.dumps(payload, ensure_ascii=False, indent=2)

    json_path.write_text(json_text, encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")
    latest_json_path.write_text(json_text, encoding="utf-8")
    latest_md_path.write_text(markdown, encoding="utf-8")

    return {
        "json": str(json_path),
        "markdown": str(md_path),
        "latest_json": str(latest_json_path),
        "latest_markdown": str(latest_md_path),
    }


def build_payload(
    title: str,
    repo_dir: Path,
    input_payload: Dict[str, Any],
    diff_text: str,
    files: List[str],
    requirement: str,
    codex_result: Dict[str, Any],
):
    impact_result = analyze_v27_impact(diff_text, files, requirement)
    payload = {
        "title": title,
        "status": "success",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "input": input_payload,
        "codex": codex_result,
        "impact": impact_result,
        "risk_level": impact_result["risk_level"],
        "test_cases": impact_result["test_cases"],
        "estimated_cost": impact_result["estimated_cost"],
        "repo_status": git_status(repo_dir),
        "v27_loaded": {
            "nodes": len(V27_DATA["nodes"]),
            "edges": len(V27_DATA["edges"]),
            "fields": len(V27_DATA["fields"]),
            "skills": len(V27_DATA["skills"]),
            "mapping": len(V27_DATA["mapping"]),
        },
    }
    payload["outputs"] = save_outputs("change_summary", payload)
    return payload


# =========================
# HTTP 接口
# =========================


@app.post("/analyze-change")
def analyze_change(data: Dict[str, Any], authorization: str = Header(default="")):
    verify_token(authorization)

    repo_dir = resolve_repo_dir(data.get("repo", ""))
    requirement = data.get("requirement", "")
    commit = data.get("commit", "")
    branch = data.get("branch", "")
    files = normalize_files(data.get("files", []))
    pull_latest = bool(data.get("pull_latest", False))

    if pull_latest:
        git_pull(repo_dir)

    diff_text = data.get("diff", "")
    if not diff_text:
        diff_text = git_commit_diff(repo_dir, commit) if commit else git_worktree_diff(repo_dir)

    if not files:
        files = git_changed_files(repo_dir, commit)

    status = git_status(repo_dir)
    recent_log = git_recent_log(repo_dir)
    prompt = build_analyze_prompt(requirement, diff_text, files, recent_log, status)
    codex_result = call_codex_cli(prompt, repo_dir, mode="analyze")

    input_payload = {
        "mode": "analyze",
        "repo": str(repo_dir),
        "branch": branch,
        "commit": commit,
        "requirement": requirement,
        "files": files,
        "diff_preview": truncate_text(diff_text, 800),
    }

    return build_payload("研发协同变更影响分析报告", repo_dir, input_payload, diff_text, files, requirement, codex_result)


@app.post("/apply-change")
def apply_change(data: Dict[str, Any], authorization: str = Header(default="")):
    verify_token(authorization)

    repo_dir = resolve_repo_dir(data.get("repo", ""))
    requirement = data.get("requirement", "")
    files = normalize_files(data.get("files", []))
    pull_latest = bool(data.get("pull_latest", False))

    if not requirement:
        raise HTTPException(status_code=400, detail="apply-change 必须提供 requirement")

    if pull_latest:
        git_pull(repo_dir)

    before_status = git_status(repo_dir)
    recent_log = git_recent_log(repo_dir)
    prompt = build_apply_prompt(requirement, files, recent_log, before_status)
    codex_result = call_codex_cli(prompt, repo_dir, mode="apply", timeout=600)

    actual_diff = git_worktree_diff(repo_dir)
    actual_files = git_changed_files(repo_dir)

    input_payload = {
        "mode": "apply",
        "repo": str(repo_dir),
        "requirement": requirement,
        "files": actual_files or files,
        "before_status": before_status,
        "diff_preview": truncate_text(actual_diff, 800),
    }

    payload = build_payload("需求变更实现与测试预警报告", repo_dir, input_payload, actual_diff, actual_files or files, requirement, codex_result)

    patch_path = OUTPUTS_DIR / "codex_patch.diff"
    patch_path.write_text(actual_diff, encoding="utf-8")
    payload["outputs"]["patch"] = str(patch_path)
    return payload


@app.post("/codex-impact")
def codex_impact(data: Dict[str, Any], authorization: str = Header(default="")):
    return analyze_change(data, authorization)


@app.post("/run")
def run(data: Dict[str, Any], authorization: str = Header(default="")):
    change_input = data.get("change_input", data)
    if isinstance(change_input, str):
        try:
            change_input = json.loads(change_input)
        except Exception:
            change_input = {"diff": change_input}
    return analyze_change(change_input, authorization)


@app.get("/latest-report")
def latest_report():
    latest_md = OUTPUTS_DIR / "change_summary-latest.md"
    if not latest_md.exists():
        raise HTTPException(status_code=404, detail="暂无报告")
    return {"path": str(latest_md), "content": latest_md.read_text(encoding="utf-8")}


@app.get("/knowledge/status")
def knowledge_status():
    index_path = KNOWLEDGE_DIR / "index.json"
    manifest_path = KNOWLEDGE_DIR / "source_manifest.json"
    index = []
    manifest = []

    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    return {
        "knowledge_dir": str(KNOWLEDGE_DIR),
        "built": index_path.exists(),
        "documents": len(manifest),
        "chunks": len(index),
        "summary": str(KNOWLEDGE_DIR / "CODEX_KNOWLEDGE.md"),
    }


@app.get("/health")
def health():
    default_repo = REPOS_DIR / DEFAULT_REPO_NAME
    return {
        "status": "ok",
        "base_dir": str(BASE_DIR),
        "default_repo": str(default_repo),
        "default_repo_exists": default_repo.exists(),
        "runner_exists": RUNNER_PATH.exists(),
        "runner_executable": os.access(RUNNER_PATH, os.X_OK),
        "outputs_dir": str(OUTPUTS_DIR),
        "knowledge_dir": str(KNOWLEDGE_DIR),
        "knowledge_built": (KNOWLEDGE_DIR / "index.json").exists(),
        "v27_loaded": {
            "nodes": len(V27_DATA["nodes"]),
            "edges": len(V27_DATA["edges"]),
            "fields": len(V27_DATA["fields"]),
            "skills": len(V27_DATA["skills"]),
            "mapping": len(V27_DATA["mapping"]),
        },
    }


@app.get("/")
def root():
    return {
        "message": "基于Codex的研发协同变更分析与测试预警工作流",
        "endpoints": [
            "/health",
            "/knowledge/status",
            "/analyze-change",
            "/apply-change",
            "/codex-impact",
            "/latest-report",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
