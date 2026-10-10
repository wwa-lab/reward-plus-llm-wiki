#!/usr/bin/env python3
"""校验 reward-plus-llm-wiki 的结构、登记表、ID、front matter 与内部链接。

Python 标准库 only，不引入第三方依赖。只读：不修改任何文件，不访问网络。

用法:
    python3 scripts/validate_repo.py [--root /path/to/repo]

退出码: 0 = 无 ERROR, 1 = 存在 ERROR。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# 期望的结构
# ---------------------------------------------------------------------------

# raw/ 的材料类型。规则说明在 raw/_types/<类型>.md；
# 材料本身在 raw/<PRJ-####>/<类型>/ 或 raw/_shared/<类型>/，不直接放在 raw/<类型>/。
RAW_TYPES = [
    "code-scan-results",
    "fe-menus",
    "business-documents",
    "test-cases",
    "test-results",
    "diagrams-and-images",
    "data-dictionary",
    "control-files",
]

# raw/ 下允许出现的非 project 条目
RAW_RESERVED = {"README.md", "_types", "_shared"}
# project 目录名：PRJ-#### 或 PRJ-####-<slug>
RAW_PROJECT_RE = re.compile(r"^PRJ-\d{4}(?:-[a-z0-9-]+)?$")

REQUIRED_FILES = [
    "README.md",
    "CONTRIBUTING.md",
    "AGENTS.md",
    ".gitignore",
    "raw/README.md",
    "raw/_types/README.md",
    "raw/_shared/README.md",
    "knowledge/README.md",
    "knowledge/registry/README.md",
    "knowledge/registry/functions.md",
    "knowledge/registry/programs.md",
    "knowledge/registry/business-rules.md",
    "knowledge/registry/data-entities.md",
    "knowledge/registry/interfaces.md",
    "knowledge/registry/menu-entries.md",
    "knowledge/registry/batch-jobs.md",
    "knowledge/registry/test-cases.md",
    "knowledge/registry/source-materials.md",
    "knowledge/registry/systems.md",
    "knowledge/registry/terms.md",
    "knowledge/registry/concepts.md",
    "knowledge/registry/control-params.md",
    "knowledge/registry/projects.md",
    "knowledge/functions/README.md",
    "knowledge/programs/README.md",
    "knowledge/business-rules/README.md",
    "knowledge/data-and-interfaces/README.md",
    "knowledge/external-systems/README.md",
    "knowledge/domain/README.md",
    "knowledge/domain/concepts/README.md",
    "knowledge/configuration/README.md",
    "knowledge/menus-and-navigation/README.md",
    "knowledge/batch-and-jobs/README.md",
    "knowledge/projects/README.md",
    "knowledge/architecture/README.md",
    "analysis/README.md",
    "analysis/reports/README.md",
    "requirements/README.md",
    "tests/README.md",
    "templates/README.md",
    "templates/function-template.md",
    "templates/program-template.md",
    "templates/business-rule-template.md",
    "templates/data-entity-template.md",
    "templates/interface-template.md",
    "templates/menu-entry-template.md",
    "templates/test-case-template.md",
    "templates/source-record-template.md",
    "templates/system-template.md",
    "templates/concept-template.md",
    "templates/control-param-template.md",
    "templates/project-template.md",
    "agents/README.md",
    "agents/workflows/README.md",
    "scripts/README.md",
    "docs/knowledge-model.md",
    "docs/evidence-and-validation.md",
    "docs/workflows.md",
]

# raw/ 各类型的规则文件
REQUIRED_FILES += [f"raw/_types/{t}.md" for t in RAW_TYPES]

REQUIRED_DIRS = [
    "raw/_types",
    "raw/_shared",
    "knowledge/registry",
    "knowledge/functions",
    "knowledge/programs",
    "knowledge/business-rules",
    "knowledge/data-and-interfaces",
    "knowledge/external-systems",
    "knowledge/domain",
    "knowledge/domain/concepts",
    "knowledge/configuration",
    "knowledge/menus-and-navigation",
    "knowledge/batch-and-jobs",
    "knowledge/projects",
    "knowledge/architecture",
    "analysis/reports",
    "requirements",
    "tests/validation",
    "templates",
    "agents/workflows",
    "scripts",
    "docs",
]

# 目录 -> 允许的 ID 前缀（一个目录可能容纳多种前缀）
DIR_PREFIXES = {
    "knowledge/functions": ["FUNC"],
    "knowledge/programs": ["PROG"],
    "knowledge/business-rules": ["RULE"],
    "knowledge/data-and-interfaces": ["DATA", "IF"],
    "knowledge/external-systems": ["SYS"],
    "knowledge/domain/concepts": ["CONCEPT"],
    "knowledge/configuration": ["CFG"],
    "knowledge/menus-and-navigation": ["MENU"],
    "knowledge/batch-and-jobs": ["JOB"],
    "knowledge/projects": ["PRJ"],
    "tests/validation": ["TEST"],
}

# 登记表文件 -> 前缀
REGISTRY_PREFIX = {
    "functions.md": "FUNC",
    "programs.md": "PROG",
    "business-rules.md": "RULE",
    "data-entities.md": "DATA",
    "interfaces.md": "IF",
    "menu-entries.md": "MENU",
    "batch-jobs.md": "JOB",
    "test-cases.md": "TEST",
    "source-materials.md": "SRC",
    "systems.md": "SYS",
    "terms.md": "TERM",
    "concepts.md": "CONCEPT",
    "control-params.md": "CFG",
    "projects.md": "PRJ",
}

ALL_PREFIXES = [
    "FUNC", "PROG", "RULE", "DATA", "IF", "SYS", "TERM", "CONCEPT", "CFG", "MENU", "JOB", "PRJ", "TEST", "SRC",
]
PREFIX_ALT = "|".join(sorted(ALL_PREFIXES, key=len, reverse=True))

STATUS_VALUES = {
    "EVIDENCE_FOUND",
    "INFERRED",
    "NEEDS_REVIEW",
    "SME_CONFIRMED",
    "CONFLICTED",
    "SUPERSEDED",
}
CONFIDENCE_VALUES = {"high", "medium", "low", "unknown"}

REQUIRED_FRONTMATTER = ["id", "title", "artifact_type", "status", "created_at", "updated_at"]

# docs/ 是仓库自身的说明文档，不占用登记 ID，因此不要求 id 字段。
DOCS_REQUIRED_FRONTMATTER = ["title", "artifact_type", "status", "created_at", "updated_at"]

FILENAME_RE = re.compile(rf"^({PREFIX_ALT})-(\d{{4}})(?:-([a-z0-9-]+))?\.md$")
ID_ANY_RE = re.compile(rf"\b({PREFIX_ALT})-(\d{{4}})\b")
# 匹配形如「当前最大 ID：0」（允许前后有 markdown 加粗符号）
MAXID_RE = re.compile(r"当前最大\s*ID\D{0,8}(\d+)")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def note(self, msg: str) -> None:
        self.info.append(msg)


# ---------------------------------------------------------------------------
# 解析辅助
# ---------------------------------------------------------------------------


def front_matter(path: Path) -> dict | None:
    """解析顶层 YAML front matter（简单键值，不需要第三方库）。"""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    data: dict = {}
    for line in text[3:end].splitlines():
        line = line.split(" #", 1)[0].rstrip()
        if not line or line.lstrip().startswith("#") or line.startswith((" ", "\t", "-")):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def has_key_block(path: Path, key: str) -> bool:
    """front matter 里是否存在某个键（含嵌套列表键）。"""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    if not text.startswith("---"):
        return False
    end = text.find("\n---", 3)
    if end == -1:
        return False
    return re.search(rf"^{re.escape(key)}:", text[3:end], flags=re.M) is not None


# ---------------------------------------------------------------------------
# 检查项
# ---------------------------------------------------------------------------


def check_structure(root: Path, rep: Report) -> None:
    for rel in REQUIRED_FILES:
        if not (root / rel).is_file():
            rep.error(f"缺少必需文件：{rel}")
    for rel in REQUIRED_DIRS:
        if not (root / rel).is_dir():
            rep.error(f"缺少必需目录：{rel}")


def check_raw_layout(root: Path, rep: Report) -> None:
    """raw/ 必须按 project 组织：raw/<PRJ-####>/<类型>/ 或 raw/_shared/<类型>/。

    材料类型目录不允许直接出现在 raw/ 根下——那会丢掉"这批材料属于哪次交付"这个维度。
    """
    raw = root / "raw"
    if not raw.is_dir():
        return

    for entry in sorted(raw.iterdir()):
        name = entry.name
        if name in RAW_RESERVED:
            continue
        if entry.is_file():
            rep.error(f"raw/{name}: raw/ 根下不允许放文件（只允许 README.md）")
            continue
        if not RAW_PROJECT_RE.match(name):
            rep.error(
                f"raw/{name}/: 目录名应为 'PRJ-####' 或 'PRJ-####-<slug>'。"
                f"材料类型目录不能直接放在 raw/ 下，应为 raw/<PRJ-####>/<类型>/ 或 raw/_shared/<类型>/"
            )
            continue
        for sub in sorted(entry.iterdir()):
            if sub.name == "_MANIFEST.md":
                continue
            if sub.is_file():
                rep.warn(f"raw/{name}/{sub.name}: project 目录下只应放 _MANIFEST.md 与类型子目录")
                continue
            if sub.name not in RAW_TYPES:
                rep.error(f"raw/{name}/{sub.name}/: 不是已知材料类型（应为 {'/'.join(RAW_TYPES)} 之一，新类型要先加进 raw/_types/）")
        if not (entry / "_MANIFEST.md").is_file():
            rep.warn(f"raw/{name}/: 缺少 _MANIFEST.md（交付清单：谁给的、什么时候、范围、LAN 来源）")

    shared = raw / "_shared"
    if shared.is_dir():
        for sub in sorted(shared.iterdir()):
            if sub.name == "README.md":
                continue
            if sub.is_file():
                rep.warn(f"raw/_shared/{sub.name}: _shared/ 下只应放 README.md 与类型子目录")
                continue
            if sub.name not in RAW_TYPES:
                rep.error(f"raw/_shared/{sub.name}/: 不是已知材料类型（应为 {'/'.join(RAW_TYPES)} 之一）")


def check_registries(root: Path, rep: Report) -> dict[str, set[str]]:
    """校验全部登记表，返回 前缀 -> 已登记 ID 集合。"""
    reg_dir = root / "knowledge" / "registry"
    registered: dict[str, set[str]] = {p: set() for p in ALL_PREFIXES}
    if not reg_dir.is_dir():
        return registered

    for name, prefix in REGISTRY_PREFIX.items():
        path = reg_dir / name
        if not path.is_file():
            rep.error(f"缺少登记表：knowledge/registry/{name}")
            continue
        text = path.read_text(encoding="utf-8")

        m = MAXID_RE.search(text)
        if not m:
            rep.error(f"knowledge/registry/{name}: 未找到『当前最大 ID』标记")
            last_id = -1
        else:
            last_id = int(m.group(1))

        found: dict[str, list[str]] = {}
        for line_no, line in enumerate(text.splitlines(), start=1):
            # 只解析表格行：说明文字里的示例 ID（例如「新 ID = FUNC-0001」）不算记录
            if not line.lstrip().startswith("|"):
                continue
            # 只有首列（ID 列）代表本表实体；其余列是关系引用，允许指向其他实体类型
            cells = line.strip().strip("|").split("|")
            id_cell = cells[0].strip() if cells else ""
            for pid, num in ID_ANY_RE.findall(id_cell):
                found.setdefault(f"{pid}-{num}", []).append(f"第{line_no}行")
                if pid != prefix:
                    rep.error(f"knowledge/registry/{name}: ID 列 '{pid}-{num}' 不属于本表前缀 '{prefix}'")
                elif pid in registered:
                    registered[pid].add(f"{pid}-{num}")

        # 占位行（`—`）不算记录
        real = {k: v for k, v in found.items() if not k.startswith("—")}
        if not real and last_id == 0:
            rep.note(f"knowledge/registry/{name}: 表内无记录（当前最大 ID = 0）—— 初始状态，正常")
        highest = 0
        for key in real:
            highest = max(highest, int(key.split("-")[1]))
        if last_id < highest:
            rep.error(f"knowledge/registry/{name}: 当前最大 ID = {last_id}，低于表内最高 ID {highest}")

    # 跨表重复 ID
    seen: dict[str, str] = {}
    for prefix, ids in registered.items():
        for pid in ids:
            if pid in seen:
                rep.error(f"ID 重复：{pid} 出现在 {seen[pid]} 与 {prefix} 两张登记表")
            seen[pid] = prefix
    return registered


def check_artifacts(root: Path, rep: Report, registered: dict[str, set[str]]) -> None:
    for rel_dir, prefixes in DIR_PREFIXES.items():
        directory = root / rel_dir
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.md")):
            rel = path.relative_to(root)
            if path.name == "README.md":
                continue
            m = FILENAME_RE.match(path.name)
            if not m:
                rep.error(f"{rel}: 文件名不符合 '<前缀>-####[-slug].md'（允许前缀：{'/'.join(prefixes)}）")
                continue
            prefix, num = m.group(1), m.group(2)
            if prefix not in prefixes:
                rep.error(f"{rel}: 前缀 '{prefix}' 不属于 {rel_dir}/（应为 {'/'.join(prefixes)}）")
                continue
            fid = f"{prefix}-{num}"

            fm = front_matter(path)
            if fm is None:
                rep.error(f"{rel}: 缺少或无法解析 YAML front matter")
                continue
            for key in REQUIRED_FRONTMATTER:
                if key not in fm:
                    rep.error(f"{rel}: front matter 缺少 '{key}'")
            status = fm.get("status", "")
            if status and status not in STATUS_VALUES:
                rep.error(f"{rel}: status '{status}' 不是合法状态（应为 {sorted(STATUS_VALUES)}）")
            confidence = fm.get("confidence", "")
            if confidence and confidence not in CONFIDENCE_VALUES:
                rep.error(f"{rel}: confidence '{confidence}' 不合法（应为 {sorted(CONFIDENCE_VALUES)}）")

            doc_id = fm.get("id", "")
            if doc_id and doc_id != fid:
                rep.error(f"{rel}: front matter 的 id '{doc_id}' 与文件名 '{fid}' 不一致")

            if fid not in registered.get(prefix, set()):
                rep.error(f"{rel}: ID '{fid}' 未登记在 knowledge/registry/ 对应表中")

            if status == "EVIDENCE_FOUND" and not has_key_block(path, "source_refs"):
                rep.warn(f"{rel}: status 为 EVIDENCE_FOUND 但缺少 source_refs")
            if status == "SME_CONFIRMED":
                if not fm.get("reviewed_by") or not fm.get("reviewed_at"):
                    rep.error(f"{rel}: status 为 SME_CONFIRMED 但缺少 reviewed_by / reviewed_at")


def check_docs(root: Path, rep: Report) -> None:
    """docs/ 用描述性文件名，但仍需合规 front matter。"""
    docs = root / "docs"
    if not docs.is_dir():
        return
    for path in sorted(docs.glob("*.md")):
        rel = path.relative_to(root)
        fm = front_matter(path)
        if fm is None:
            rep.error(f"{rel}: 缺少或无法解析 YAML front matter")
            continue
        for key in DOCS_REQUIRED_FRONTMATTER:
            if key not in fm:
                rep.error(f"{rel}: front matter 缺少 '{key}'")
        status = fm.get("status", "")
        if status and status not in STATUS_VALUES:
            rep.error(f"{rel}: status '{status}' 不是合法状态")
        doc_id = fm.get("id", "")
        if doc_id and not re.fullmatch(r"[A-Z]{2,4}-\d{4}", doc_id):
            rep.error(f"{rel}: 文档 id '{doc_id}' 应符合 '<前缀>-####'")


def check_links(root: Path, rep: Report) -> None:
    for path in sorted(root.rglob("*.md")):
        if ".git" in path.parts or ".workbuddy-ai" in path.parts:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for target in LINK_RE.findall(text):
            target = target.strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#", "<")):
                continue
            clean = target.split("#", 1)[0].split("?", 1)[0]
            if not clean:
                continue
            resolved = (path.parent / clean).resolve()
            if not resolved.exists():
                rep.warn(f"{path.relative_to(root)}: 链接指向不存在的文件 -> {target}")


def check_duplicate_files(root: Path, rep: Report) -> None:
    seen: dict[str, str] = {}
    for rel_dir in list(DIR_PREFIXES) + ["knowledge/architecture"]:
        directory = root / rel_dir
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.md")):
            m = FILENAME_RE.match(path.name)
            if not m:
                continue
            key = f"{m.group(1)}-{m.group(2)}"
            if key in seen:
                rep.error(f"ID 被两个文件占用 '{key}'：{seen[key]} 与 {path.relative_to(root)}")
            seen[key] = str(path.relative_to(root))


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 reward-plus-llm-wiki 仓库结构与知识产物")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent), help="仓库根目录")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"根目录不存在：{root}")
        return 1

    rep = Report()
    check_structure(root, rep)
    check_raw_layout(root, rep)
    registered = check_registries(root, rep)
    check_artifacts(root, rep, registered)
    check_docs(root, rep)
    check_duplicate_files(root, rep)
    check_links(root, rep)

    print(f"校验目标：{root}\n")
    if rep.info:
        print(f"INFO ({len(rep.info)})")
        for msg in rep.info:
            print(f"  - {msg}")
        print()
    if rep.warnings:
        print(f"WARNING ({len(rep.warnings)})")
        for msg in rep.warnings:
            print(f"  - {msg}")
        print()
    if rep.errors:
        print(f"ERROR ({len(rep.errors)})")
        for msg in rep.errors:
            print(f"  - {msg}")
        print()
        print("结果：未通过")
        return 1

    print(f"结果：通过（{len(rep.warnings)} 条警告，{len(rep.info)} 条提示）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
