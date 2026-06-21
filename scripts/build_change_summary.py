#!/usr/bin/env python3
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import server  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="生成本地 Git 代码库变更影响分析报告")
    parser.add_argument("--repo", default=server.DEFAULT_REPO_NAME, help="repos 下的仓库名或绝对路径")
    parser.add_argument("--requirement", default="", help="需求变更说明")
    parser.add_argument("--commit", default="", help="要分析的提交，不传则分析本地未提交 diff")
    parser.add_argument("--diff-file", default="", help="外部 diff 文件")
    parser.add_argument("--files", nargs="*", default=[], help="涉及文件")
    parser.add_argument("--no-codex", action="store_true", help="只做 V27 映射，不调用 Codex")
    args = parser.parse_args()

    repo_dir = server.resolve_repo_dir(args.repo)
    diff_text = ""

    if args.diff_file:
        diff_text = Path(args.diff_file).read_text(encoding="utf-8")
    elif args.commit:
        diff_text = server.git_commit_diff(repo_dir, args.commit)
    else:
        diff_text = server.git_worktree_diff(repo_dir)

    files = args.files or server.git_changed_files(repo_dir, args.commit)
    status = server.git_status(repo_dir)
    recent_log = server.git_recent_log(repo_dir)

    if args.no_codex:
        codex_result = {"success": True, "raw": "未调用 Codex，仅生成 V27 影响分析。", "returncode": 0}
    else:
        prompt = server.build_analyze_prompt(args.requirement, diff_text, files, recent_log, status)
        codex_result = server.call_codex_cli(prompt, repo_dir, mode="analyze")

    payload = server.build_payload(
        "研发协同变更影响分析报告",
        repo_dir,
        {
            "mode": "cli-analyze",
            "repo": str(repo_dir),
            "commit": args.commit,
            "requirement": args.requirement,
            "files": files,
            "diff_preview": server.truncate_text(diff_text, 800),
        },
        diff_text,
        files,
        args.requirement,
        codex_result,
    )

    print(json.dumps(payload["outputs"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
