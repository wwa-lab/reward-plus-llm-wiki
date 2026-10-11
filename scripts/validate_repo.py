#!/usr/bin/env python3
"""校验 reward-plus-llm-wiki 的结构、登记表、ID、front matter 与内部链接。

Python 标准库 only，不引入第三方依赖。只读：不修改任何文件，不访问网络。

用法:
    python3 scripts/validate_repo.py [--root /path/to/repo]

退出码: 0 = 无 ERROR, 1 = 存在 ERROR。
"""

from __future__ import annotations

import argparse
import json
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
# project 目录名：严格为 PRJ-####（不带 slug，与 AGENTS.md / README 的 raw/PRJ-####/<类型>/ 一致）
RAW_PROJECT_RE = re.compile(r"^PRJ-\d{4}$")

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
    "templates/batch-job-template.md",
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

# 知识页 front matter 里的关系字段 —— 取值应为已登记的 ID
RELATION_KEYS = [
    "related_functions", "related_programs", "related_rules", "related_data",
    "related_interfaces", "related_projects", "related_config", "related_terms",
    "related_systems", "partner_system", "physical_ref",
]

# 这些前缀"行即记录"，登记表本身就是内容，不要求另建知识页
ROW_ONLY_PREFIXES = {"TERM", "SRC"}

# 按约定"默认不提交"的材料路径 —— 校验证据引用时豁免存在性检查
DEFAULT_UNCOMMITTED_RE = re.compile(r"^raw/(?:[^/]+|_shared)/control-files/")


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


def _strip_comment(value: str) -> str:
    """去掉行内 YAML 注释，但不破坏引号内的 #。

    反例：`title: "积分累积 # 2024 改版"` —— 简单按 " #" 切会把标题截成 `积分累积`。
    """
    if value[:1] in ('"', "'"):
        quote = value[0]
        end = value.find(quote, 1)
        return value[: end + 1] if end != -1 else value
    idx = value.find(" #")
    return value[:idx] if idx != -1 else value


def _unquote(value: str) -> str:
    return _strip_comment(value.strip()).strip().strip('"').strip("'")


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
        if not line or line.lstrip().startswith("#") or line.startswith((" ", "\t", "-")):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = _unquote(value)
    return data


def front_matter_list(path: Path, key: str) -> list[str]:
    """取 front matter 里某个键的列表值（支持 `[a, b]` 与逐行 `- a` 两种写法）。"""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    if not text.startswith("---"):
        return []
    end = text.find("\n---", 3)
    if end == -1:
        return []
    items: list[str] = []
    collecting = False
    for line in text[3:end].splitlines():
        if re.match(rf"^{re.escape(key)}\s*:", line):
            collecting = True
            inline = re.search(r"\[(.*)\]", line)
            if inline:
                items += [x for x in (_unquote(p) for p in inline.group(1).split(",")) if x]
            continue
        if not collecting:
            continue
        if not line.strip():
            continue
        if line.startswith((" ", "\t")):
            m = re.match(r"^\s+-\s*(.+)$", line)
            if m:
                item = _unquote(m.group(1))
                if item:
                    items.append(item)
            continue
        collecting = False
    return items


def evidence_refs(path: Path) -> list[str]:
    """解析 source_refs 的路径字符串列表；不支持的 YAML 形态显式报错。

    仅用于知识页证据，不改变关系字段或 docs/ 的元数据约定。
    支持行内列表与逐行列表，不支持对象、嵌套结构或多行字符串。
    """
    text = path.read_text(encoding="utf-8")
    end = text.find("\n---", 3)
    if not text.startswith("---") or end == -1:
        return []  # front matter 缺失由 check_artifacts 报告
    lines = text[3:end].splitlines()
    declarations = [i for i, line in enumerate(lines) if re.match(r"^source_refs\s*:", line)]
    if not declarations:
        return []
    if len(declarations) != 1:
        raise ValueError("source_refs 不能重复声明")

    def scalar(value: str) -> str:
        value = value.strip()
        if value.startswith('"'):
            match = re.fullmatch(r'("(?:[^"\\]|\\.)*")\s*(?:#.*)?', value)
            if not match:
                raise ValueError("source_refs 包含无效的双引号字符串")
            try:
                result = json.loads(match.group(1))
            except ValueError as exc:
                raise ValueError("source_refs 双引号字符串包含不支持的转义") from exc
        elif value.startswith("'"):
            match = re.fullmatch(r"'((?:[^']|'')*)'\s*(?:#.*)?", value)
            if not match:
                raise ValueError("source_refs 包含无效的单引号字符串")
            result = match.group(1).replace("''", "'")
        else:
            result = re.split(r"\s+#", value, maxsplit=1)[0].strip()
            if (not result or result[0] in "#[]{}&*!>|"
                    or result.startswith("- ")
                    or re.search(r":(?:\s|$)", result)
                    or result.lower() in {"null", "~", "true", "false"}
                    or re.fullmatch(r"[-+]?\d+(?:\.\d+)?", result)):
                raise ValueError("source_refs 只支持路径字符串列表，不支持对象或其他 YAML 类型")
        if not result.strip():
            raise ValueError("source_refs 不能包含空路径")
        return result

    start = declarations[0]
    inline = lines[start].partition(":")[2].strip()
    body = []
    for line in lines[start + 1:]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith((" ", "\t", "-")):
            break
        body.append(line)
    if inline and not inline.startswith("#"):
        match = re.fullmatch(r"\[(.*)\]\s*(?:#.*)?", inline)
        if not match or body:
            raise ValueError("source_refs 必须是行内列表或逐行路径列表")
        content = match.group(1).strip()
        if not content:
            return []
        # 只在引号外切分逗号，保留路径中的逗号与 #。
        token = r'''\s*("(?:[^"\\]|\\.)*"|'(?:[^']|'')*'|[^,\[\]{}"']+)\s*(,|$)'''
        refs = []
        pos = 0
        while pos < len(content):
            item = re.match(token, content[pos:])
            if not item:
                raise ValueError("source_refs 行内列表包含不支持的格式")
            refs.append(scalar(item.group(1)))
            pos += item.end()
        return refs
    refs = []
    indent = None
    for line in body:
        item = re.fullmatch(r"( *)-\s+(.+)", line)
        if not item or (indent is not None and len(item.group(1)) != indent):
            raise ValueError("source_refs 逐行列表只支持 '- 路径'，不支持嵌套结构")
        indent = len(item.group(1))
        refs.append(scalar(item.group(2)))
    return refs


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
                f"raw/{name}/: 目录名应为 'PRJ-####'（不带 slug）。"
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


def iter_artifacts(root: Path):
    """遍历所有登记在 DIR_PREFIXES 下的知识页（跳过 README）。"""
    for rel_dir in DIR_PREFIXES:
        directory = root / rel_dir
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.md")):
            if path.name != "README.md":
                yield rel_dir, path


def parse_registry_rows(text: str) -> tuple[list[str], list[list[str]]]:
    """解析登记表，返回（表头列名, 数据行）。跳过表头与分隔行。"""
    header: list[str] = []
    rows: list[list[str]] = []
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not header:
            if cells and cells[0] == "ID":
                header = cells
            continue
        if all(set(c) <= set("-: ") for c in cells if c):
            continue
        rows.append(cells)
    return header, rows


def check_evidence_refs(root: Path, rep: Report) -> None:
    """front matter 的 source_refs 必须指向存在的材料。

    演练暴露的问题：证据引用写在 front matter 或正文代码路径里时，
    原先的链接检查完全覆盖不到——路径写错没人发现，证据链静默断裂。
    """
    for rel_dir, path in iter_artifacts(root):
        rel = path.relative_to(root)
        try:
            refs = evidence_refs(path)
        except ValueError as exc:
            rep.error(f"{rel}: {exc}")
            continue
        fm = front_matter(path) or {}
        if fm.get("status") == "EVIDENCE_FOUND" and not refs:
            rep.error(f"{rel}: status 为 EVIDENCE_FOUND，source_refs 必须包含至少一个非空路径")
        for ref in refs:
            if not ref.startswith(("raw/", "knowledge/", "tests/")):
                continue  # LAN 路径等非仓库路径，不在校验范围
            if DEFAULT_UNCOMMITTED_RE.match(ref):
                rep.note(f"{rel}: 证据引用 {ref} 属于『默认不提交』的材料，跳过存在性检查")
                continue
            if not (root / ref).exists():
                rep.warn(
                    f"{rel}: source_refs 指向不存在的路径 -> {ref}"
                    f"（若材料仍在 LAN 未入库，请在 knowledge/registry/source-materials.md 登记 LAN 路径）"
                )


def check_relations(root: Path, rep: Report, registered: dict[str, set[str]]) -> None:
    """知识页 front matter 的关系字段必须引用已登记的 ID。

    演练暴露的问题：`related_programs: [PROG-9999]` 这类悬空引用原先无人检查。
    """
    for rel_dir, path in iter_artifacts(root):
        rel = path.relative_to(root)
        for key in RELATION_KEYS:
            for value in front_matter_list(path, key):
                for pid, num in ID_ANY_RE.findall(value):
                    fid = f"{pid}-{num}"
                    if fid not in registered.get(pid, set()):
                        rep.warn(f"{rel}: {key} 引用了未登记的 ID '{fid}'")


def check_registry_page_consistency(root: Path, rep: Report, registered: dict[str, set[str]]) -> None:
    """登记表与知识页必须互相对应，且状态一致。

    演练暴露的问题：
    * 登记行存在但知识页缺失（约定要求同一次提交完成）——原先无人检查；
    * 知识页 status 与登记表 status 不一致（约定说"登记表是权威来源"）——原先无人检查。
    """
    pages: dict[str, tuple[str, str]] = {}  # ID -> (路径, status)
    for rel_dir, path in iter_artifacts(root):
        fm = front_matter(path)
        if fm is None:
            continue
        m = FILENAME_RE.match(path.name)
        if not m:
            continue
        pages[f"{m.group(1)}-{m.group(2)}"] = (str(path.relative_to(root)), fm.get("status", ""))

    reg_dir = root / "knowledge" / "registry"
    for name, prefix in REGISTRY_PREFIX.items():
        path = reg_dir / name
        if not path.is_file():
            continue
        header, rows = parse_registry_rows(path.read_text(encoding="utf-8"))
        status_idx = header.index("状态") if "状态" in header else None
        for cells in rows:
            m = ID_ANY_RE.search(cells[0]) if cells else None
            if not m:
                continue
            fid = f"{m.group(1)}-{m.group(2)}"
            if prefix not in ROW_ONLY_PREFIXES and fid not in pages:
                rep.warn(
                    f"knowledge/registry/{name}: 登记了 {fid} 但没有对应的知识页"
                    f"（约定：登记行与知识页在同一次提交里完成）"
                )
            if status_idx is not None and status_idx < len(cells) and fid in pages:
                reg_status = cells[status_idx].strip().strip("`")
                page_path, page_status = pages[fid]
                if reg_status and page_status and reg_status != page_status:
                    rep.warn(
                        f"{page_path}: status '{page_status}' 与 knowledge/registry/{name} 里 {fid} 的 "
                        f"'{reg_status}' 不一致（登记表是权威来源，请改知识页或修登记表）"
                    )


def check_orphan_raw_projects(root: Path, rep: Report, registered: dict[str, set[str]]) -> None:
    """raw/ 下的 project 目录必须有对应的 PRJ- 登记行。

    反向（登记了 PRJ 但没有材料目录）不报错：材料可以留在 LAN 上，登记行仍然是有效的。
    """
    raw = root / "raw"
    if not raw.is_dir():
        return
    for entry in sorted(raw.iterdir()):
        if not entry.is_dir() or not RAW_PROJECT_RE.match(entry.name):
            continue
        fid = entry.name
        if fid not in registered.get("PRJ", set()):
            rep.warn(f"raw/{entry.name}/: 没有对应的 {fid} 登记行（见 knowledge/registry/projects.md）")


def check_misplaced_artifacts(root: Path, rep: Report) -> None:
    """带 ID 文件名的知识页必须放在 DIR_PREFIXES 规定的目录里。

    演练暴露的问题：把 FUNC-0001-*.md 放进 knowledge/architecture/ 这类未登记目录，
    原先完全绕过命名/front matter/前缀检查。
    """
    for base in ("knowledge", "tests"):
        directory = root / base
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.md")):
            if path.name == "README.md" or not FILENAME_RE.match(path.name):
                continue
            rel_dir = str(path.parent.relative_to(root))
            if rel_dir not in DIR_PREFIXES:
                rep.error(
                    f"{path.relative_to(root)}: 带 ID 的知识页必须放在登记目录里，"
                    f"'{rel_dir}/' 不是（允许：{'、'.join(sorted(DIR_PREFIXES))}）"
                )


def check_registry_refs(root: Path, rep: Report, registered: dict[str, set[str]]) -> None:
    """登记表里 ID 列之外的列所引用的 ID，也必须已登记。

    登记表是"权威来源"。权威层里出现悬空引用（例如 DATA 行的"读写方"写了 `PROG-0003`
    但 programs.md 里没有这一行），比知识页里的悬空引用更严重。
    """
    reg_dir = root / "knowledge" / "registry"
    for name in REGISTRY_PREFIX:
        path = reg_dir / name
        if not path.is_file():
            continue
        _, rows = parse_registry_rows(path.read_text(encoding="utf-8"))
        dangling: set[str] = set()
        for cells in rows:
            for cell in cells[1:]:
                for pid, num in ID_ANY_RE.findall(cell):
                    fid = f"{pid}-{num}"
                    if fid not in registered.get(pid, set()):
                        dangling.add(fid)
        if dangling:
            rep.warn(
                f"knowledge/registry/{name}: 引用了未登记的 ID {'、'.join(sorted(dangling))}"
                f"（登记表是权威来源，悬空引用要先补登记行）"
            )


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
        for key, locations in real.items():
            if len(locations) > 1:
                rep.error(f"knowledge/registry/{name}: ID 重复 '{key}'（{'、'.join(locations)}）")
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
            try:
                rel_target = resolved.relative_to(root.resolve()).as_posix()
            except ValueError:
                rel_target = ""
            # 按约定默认不提交的材料（配置快照）clone 后本来就不存在，不算断链
            if DEFAULT_UNCOMMITTED_RE.match(rel_target):
                continue
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
    check_registry_refs(root, rep, registered)
    check_artifacts(root, rep, registered)
    check_evidence_refs(root, rep)
    check_relations(root, rep, registered)
    check_registry_page_consistency(root, rep, registered)
    check_orphan_raw_projects(root, rep, registered)
    check_misplaced_artifacts(root, rep)
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
