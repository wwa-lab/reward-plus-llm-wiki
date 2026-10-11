# 业界对标调研：面向 Agent 的文档治理 + IBM i 遗留分析生态

- 日期：2026-10-10
- 性质：**分析报告，非权威知识**。结论未经评审，引用时须注明"来自分析报告，未经评审"。
- 输入材料：**无 `raw/` 材料**。这是一次外部对标调研，输入为公开规范、开源仓库与厂商文档（清单见附录 A）。
- 覆盖范围：调研 4 个方向、34 个外部来源；其中 **21 项由本次会话直接核实**（`gh api` 实测 star/404/archived、规范原文逐字比对、本仓 `scripts/validate_repo.py` 源码自证），**13 项为子调研一手引用但未逐条复核**，**7 项为厂商宣传**（见附录 A 的核实等级列）。未覆盖：迁移方法论（Konveyor/KAI、AWS 6R、strangler fig）、数据目录治理（DataHub/OpenMetadata/SKOS/PROV）——本次未选。
- 冲突：4 处（见第 4 节），其中 1 处需要我们裁决。

---

## 1. 一句话结论

**我们没有跑偏，但只用了业界最朴素的那一层。**

- 在"Agent 友好"这件事上，业界四家（AGENTS.md 嵌套规则、Claude Code path-scoped rules、Agent Skills 三层渐进披露、aider token 预算）解的是**同一个问题：不要无条件全量加载**。而我们的入口材料是**全量、无条件、且没有任何一行式摘要**。
- 在"状态治理"上，业界（PEP / KEP / MADR）把**证据强度**和**生命周期**拆成两个正交维度，并用**机器门禁**强制；我们把两者压在一个 `status` 字段里，且校验全靠人手动跑。
- 在"证据从哪来"上，IBM i 的证据**可以从系统里直接问出来**（SQL Services + `DSPPGMREF *OUTFILE` + 现成 CLI 导 CSV），我们 `raw/_types/` 现有 8 类材料**至少缺 6 个品类**，其中最关键的是"按发布批次的对象变更清单"——那正是 `PRJ-####` 的一手证据来源。
- **我们独有、业界没有的东西不要改**：`EVIDENCE_FOUND`/`INFERRED` 二分、`CONFLICTED` 作为一等状态、`confidence` 与 `status` 正交、`source_refs` 带 `PRJ-` 交付批次维度。上述所有业界体系的默认假设都是"文档 = 作者断言"，无一区分"抄自证据"与"我推的"——对逆向工程遗留系统，这是刚需，是我们的优势。

---

## 2. 有直接证据的结论

### 2.1 Agent 文档治理：业界的共同主题是"相关性门控"

**AGENTS.md 标准**（https://agents.md/ ，逐字核实）

- FAQ 里有"required fields?"条目 → 规范**刻意极简，无必填字段、无规定章节结构、无机器可读字段**。
- 逐字原文：`closest AGENTS.md to the edited file wins; explicit user chat prompts override everything.`
- 逐字原文：`monorepo? Use nested AGENTS.md files for subprojects`
- 采纳量级（`gh api search/code` 的 `total_count`，本次实测）：`filename:AGENTS.md` → **1,097,728**；`filename:CLAUDE.md` → **874,496**；`filename:llms.txt` → **180,224**；`filename:.cursorrules` → **34,688**。
  **方法局限（必须一起读）**：该接口只索引默认分支、计的是**文件数不是仓库数**、`total_count` 为近似值。只可用于比较量级：AGENTS.md ≈ CLAUDE.md > llms.txt ≫ .cursorrules。

**Claude Code memory 官方文档**（https://code.claude.com/docs/en/memory ，逐字核实）

- `Size: target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence. Move instructions that matter for only part of the codebase into path-scoped rules, which load only when Claude works with matching files.`
- **`Imports help you organize a long file but don't reduce its context cost, because imported files also load at launch.`** ← 关键：**不要用 `@import`/链接当作省上下文的手段**。
- `Consistency: if two instructions contradict each other, Claude may pick one arbitrarily.`
- auto memory 只加载 `first 200 lines or 25KB`；`.claude/rules/` 的 `paths` 列表共享 1,000 个展开模式 + 4 MiB 预算。
- **子目录 AGENTS.md 的加载时机**：`As Claude works in subdirectories: a subdirectory's AGENTS.md, when Claude opens a file there with the Read tool and that subdirectory has none of the three CLAUDE.md files of its own` ← **这是天然的按需加载**：不碰 `raw/` 就不会加载 `raw/AGENTS.md`。

**Cursor Rules**（https://cursor.com/docs/context/rules ，逐字核实片段）

- 规则文件必须是 **`.mdc`**（纯 `.md` 不被识别，因为没有 frontmatter）。
- `alwaysApply is true, the rule will be applied to every chat session. Otherwise, the descrip…` → 四种触发方式完全由 frontmatter 组合决定：`alwaysApply:true`（无条件）／给 `globs`（按路径自动附加）／只给 `description`（**Agent 读描述自行判断是否拉入**）／都不给（仅 `@提及` 生效）。

**Anthropic Agent Skills 规范**（https://agentskills.io/specification ；仓库内 `spec/agent-skills-spec.md` 已退化为 3 行指针，本次核实。`anthropics/skills` 180,212★）

- `description`：**必填、≤1024 字符、非空**，`Describes what the skill does and when to use it`。
- **渐进式披露三层**（逐字核实）：元数据 **~100 tokens**（启动即对所有 skill 加载）→ 正文 **5000 tokens recommended**（激活时才加载）→ 资源（仅在需要时加载）。
- 逐字原文：`under 500 lines. Move detailed reference material to separate files.`
- 仓库实况印证：`skills/<name>/SKILL.md` + 语言特定的嵌套 `README.md`（如 `skills/claude-api/python/claude-api/README.md`）——**详细参考确实被挪到独立文件**。

**llms.txt 规范**（https://llmstxt.org/ ，逐字核实）

- 结构：可选 BOM → **H1 项目名（唯一必需章节）** → blockquote 简述 → 零或多段非标题内容 → 零或多个 H2 分节的"文件列表"，每项为必需的 `[name] (url)`（原文两者相连，此处空格是为避开 `check_links`，见 §2.3 盲区 9）+ 可选 `: 说明`。
- 逐字原文：`The "Optional" section is used, by convention, for secondary information: links an agent can skip when a shorter context is needed.`

**Diátaxis**（`evildmp/diataxis-documentation-framework` 1,248★；`source/how-to-use-diataxis.rst` 逐字核实）

- `Use Diátaxis as a guide, not a plan`
- **`It certainly does not mean that you should create empty structures for tutorials/howto guides/reference/explanation with nothing in them. Don't do that. It's horrible.`**
- `don't try to work on the big picture` / `Diátaxis is designed to guide small steps`

**对照我们**

| 维度 | 业界做法 | 我们的现状 |
|---|---|---|
| 规则加载 | 嵌套 AGENTS.md「最近的胜出」+ path-scoped rules + description 触发 | **只有根目录一份 AGENTS.md，无条件全量加载**；嵌套机制完全没用 |
| 入口体积 | Claude 官方阈值 200 行/文件 | AGENTS.md 80 行（合规）；但 README 386 行 + CONTRIBUTING + docs/workflows + agents/README + 15 模板，**无一处标注"何时才需要读"** |
| 一行式摘要 | Skills 的 `description` ≤1024 字符决定是否加载全文；llms.txt 每链接一行说明 | **模板与流程文档都没有一行式摘要/触发条件** |
| 廉价"先查再建" | llms.txt 式索引：~1 token/页 | 规则 1 要求检索 `knowledge/registry/` 与已有知识页，但**没有单一索引**，需逐个打开 |
| 指令冲突 | Claude 官方明说"矛盾指令会任选一条" | `docs/workflows.md` 的 **W0–W10** 与 `agents/workflows/README.md` 的 **WF-001…WF-010** 两套编号并存，无映射表 |
| 文档象限 | Diátaxis 反对混写，也**反对建空目录** | `knowledge/` = reference（纯粹、健康）；`docs/workflows.md`+`CONTRIBUTING.md` = how-to；`analysis/reports/` = explanation；**README.md 混写**（是什么 + ID 规范 + §7.9 可复制提示词，横跨三象限） |

### 2.2 状态生命周期：业界是两维正交 + 机器门禁

**Python PEP**（`python/peps` 5,025★，pushed 2026-10-09；`check-peps.py` 本次逐字核实）

- `ALL_STATUSES`（第 61–74 行）：`Accepted / Active / April Fool! / Deferred / Draft / Final / Provisional / Rejected / Superseded / Withdrawn`
- `Type` 只能是 `Standards Track / Informational / Process`（第 338 行）
- 非法状态直接产出错误：`if line not in ALL_STATUSES: yield line_num, "Status must be a valid PEP status"`（第 331–332 行）→ **CI 里的机器门禁**
- 编号 4 位、不得有前导零、<100 为 meta-PEP、**文件名即编号**（与我们的 ID 设计同构）

**Kubernetes KEP**（`kubernetes/enhancements` 3,964★；`api/proposal.go` 本次逐字核实）

- `ValidStatuses`（第 74–82 行）：`provisional / implementable / implemented / deferred / rejected / withdrawn / replaced`
- **独立第二维** `ValidStages`（第 44–51 行）：`alpha / beta / stable / deprecated / disabled / removed`
- 并有跨字段一致性断言（`status: implemented` 必须 `stage: stable`）

**MADR**（`adr/madr` 2,541★；`template/adr-template.md` 本次逐字核实）

```yaml
status: "{proposed | rejected | accepted | deprecated | … | superseded by ADR-0123}"
date: {YYYY-MM-DD when the decision was last updated}
decision-makers: {list everyone involved in the decision}
consulted: {list everyone whose opinions are sought (typically subject-matter experts); and with whom there is a two-way communication}
informed: {list everyone who is kept up-to-date on progress; and with whom there is a one-way communication}
```

**adr-tools**（`npryce/adr-tools` 5,728★，pushed 2024-04-25，**已停更**）：产出 `Supercedes [1. …]` 与 `Superceded by [2. …]` 的**双向**链接。

**对照我们**

| 维度 | 业界 | 我们 |
|---|---|---|
| 维度数 | **两维正交**：KEP `status`（评审生命周期）× `stage`（成熟度） | **一维**：`status` 同时承载证据强度（`EVIDENCE_FOUND`/`INFERRED`/`CONFLICTED`）与生命周期（`NEEDS_REVIEW`/`SME_CONFIRMED`/`SUPERSEDED`）；`confidence` 部分缓解但不等价 |
| 取代关系 | PEP `Replaces` + `Superseded-By` **成对强制**；adr-tools 双向链接 | **单向**：旧页标 `SUPERSEDED` 指向新 ID，新页**无回指字段** |
| 前置依赖 | PEP `Requires` | 只有 `related_*`，**不区分"依赖"与"相关"** |
| 演进轨迹 | PEP `Post-History`（日期 + 讨论链接的时间线） | 只有单个 `updated_at`，**演进轨迹丢失** |
| 评审现场 | PEP `Discussions-To`（权威讨论帖 URL） | 无对应字段 |
| 谁拍板 / 谁被咨询 | MADR `decision-makers` / `consulted` / `informed` **三分** | 只有 `reviewed_by`，**把拍板人与被咨询的 SME 混为一谈** |
| reviewer vs approver | KEP 分离（approvers 决定能否进 `implementable`） | 未分离 |
| 页面归属人 | KEP `owning-sig` / `editor` | **无"这一页归谁维护"** |
| 机器门禁 | PEP `check-peps.py`、KEP Go 测试（含跨字段断言），都在 CI 跑 | `scripts/validate_repo.py` 存在但**无 CI**，全靠人手动跑 |
| **我们独有** | 无一家区分"抄自证据"与"我推的"；无一家把"来源互斥且都有效"建成一等状态 | **`EVIDENCE_FOUND`/`INFERRED` 二分、`CONFLICTED` 一等状态、`confidence` 与 `status` 正交、`source_refs` 带 `PRJ-` 交付批次维度** |
| 编号永不复用 | PEP 1 原文只说"the next available PEP number not used by a published or **in-PR** PEP"，**无 "never reused" 字样**（不可复用是从"in-PR 也占用"+ 单调递增推出的，属**推断**） | 我们明文"永不复用、永不重排"——**比 PEP 更强** |

**arc42**（https://docs.arc42.org/ ，1,308★）12 章中有两章我们完全没有等价物：**§11 Risks and Technical Debt**、**§10 Quality Requirements**。我们的 `CONFLICTED` 条目、覆盖率缺口、"因证据不足没做的事"目前**散落在每次对话的完成报告里**，没有长期台账。

**CODEOWNERS**（GitHub 官方文档，子调研一手引用）：`last matching pattern takes the most precedence`、`an approval from any of the owners is sufficient`，且**必须给 `/.github/CODEOWNERS` 自身设 owner**，否则门禁可被绕过。这是把规则 6「`SME_CONFIRMED` 只能人标」变成**机器可执行**的唯一零依赖手段（GitHub 原生功能）。

### 2.3 校验工具链：一半在造轮子，一半必须自建，两个真空区

**先自证我们的盲区**（本次直接读 `scripts/validate_repo.py` 源码，非二手）

| 位置 | 事实 | 后果 |
|---|---|---|
| `check_links` 第 679 行 | `if target.startswith(("http://", "https://", "mailto:", "#", "<")): continue` | **所有外链完全不查** → 指向 IBM 文档/厂商页的链接腐烂无人知晓 |
| `check_links` 第 681 行 | `clean = target.split("#", 1)[0].split("?", 1)[0]` | **fragment 被丢弃** → 形如「方括号文本 + 圆括号 `y.md#不存在的标题`」的链接静默通过 |
| `check_links` 第 693 行 | `rep.warn(...)` | 断链只是**警告**，不是错误 |
| `LINK_RE` 第 188 行 | `re.compile(r"\[[^\]]*\]\(([^)]+)\)")` 直接扫全文，**不跳过围栏代码块与行内代码** | 文档里写"链接语法示例"必然误报——**本报告落盘时自证：3 条警告全部来自示例文本**（见 §7 处置记录） |
| `front_matter` 第 255 行 | `if not line or line.lstrip().startswith("#") or line.startswith((" ", "\t", "-")): continue` | **缩进行与列表行全被跳过** → 嵌套 YAML 完全不可见；不支持块标量/锚点/重复键检测；一切值皆字符串 |
| 全文件 | 搜 `secret\|credential\|private_key\|password\|token\|api_key` → **0 命中** | **零机密/PII 扫描**，而 AGENTS.md 规则 #10 与 `raw/*/control-files/`「敏感，默认不提交」正是需要它的地方；README 自己写明"`.gitignore` 不是安全控制手段" |
| 仓库根 | **无 `.github/`**（无 workflows、无 CODEOWNERS）、无 `.pre-commit-config.yaml` / `package.json` / `requirements.txt` / `pyproject.toml`；`tests/validation/` 是空目录 | 13 个 check 全靠人手动跑；规则 #6 无任何机器强制 |

**工具事实**（star 全部本次 `gh api` 实测）

| 工具 | URL | ★ | 能力边界 | 运行时 |
|---|---|---|---|---|
| Vale | https://github.com/vale-cli/vale | 6,223 | 散文 linter，但**不止**：12 种 check（existence/substitution/occurrence/repetition/consistency/conditional/capitalization/metric/readability/spelling/sequence/**script**）；原生解析 YAML/TOML/JSON front matter；`Vocabularies` 的 `accept.txt`/`reject.txt` 可**强制精确大小写 + 禁用词** | **单个 Go 二进制，无 Node、无 pip** |
| markdownlint | https://github.com/DavidAnson/markdownlint | 6,374 | 53 条格式规则；MD044 `proper-names` 强制精确大小写；MD051 校验 fragment；但 **front matter 被多数规则忽略**，**无跨文件能力** | Node |
| lychee | https://github.com/lycheeverse/lychee | 3,998 | 同时处理相对路径 + 外链；对比表中唯一声明 "Respect rate limits"；retry/backoff、缓存、GitHub token | Rust 二进制 |
| muffet | https://github.com/raviqqe/muffet | 2,614 | **不适合我们**：不读 Markdown、不支持相对 URL，是站点爬虫 | Go |
| super-linter | https://github.com/super-linter/super-linter | 10,617 | Markdown→markdownlint+Prettier；natural language 走 **textlint 而非 Vale**；Docker 巨像 | Docker |
| pre-commit-hooks | https://github.com/pre-commit/pre-commit-hooks | 6,709 | 文件卫生 + **`detect-private-key` / `detect-aws-credentials`** / `check-case-conflict` / `check-yaml` / `check-merge-conflict` / `check-added-large-files` | Python |
| check-jsonschema | https://github.com/python-jsonschema/check-jsonschema | 345 | JSON Schema CLI + pre-commit hook；**不抽取 Markdown front matter**，需前置步骤 | Python |
| cspell | https://github.com/streetsidesoftware/cspell | 1,699 | 可加自定义词典（`PGM1100`/`PTSACCT`） | Node |

**大仓实况**（子调研读了 workflow 原文，附 URL；本次未逐条复核 → 二手）

- `github/docs`：`.github/workflows/content-lint-markdown.yml` 用 changed-files **只 lint 变更文件**，自定义 linter 在 `src/content-linter/`（**TypeScript**，规则 ID 形如 `GHD059`），三个配置桶含专门的 `githubDocsFrontmatterConfig`；workflow 注释提到另有 **weekly 全量 sweep** 兜底跨文件影响（删文章导致别页引用断裂，diff 里看不到）。
- `rust-lang/book`：`mdbook test`（**文档即测试**）+ aspell + shellcheck + 自制 Rust 二进制 `lfp` + `ci/validate.sh`。
- **反例 `kubernetes/website`**：`.github/workflows/` 几乎不做文档 lint，靠 Prow/OWNERS + 人工评审。→ **"大仓都在 CI 里 lint 散文"不成立。**

**三分类结论**

- **① 我们在造轮子**：`check_links` 的外链与 fragment 部分（lychee / markdownlint MD051 更好）；文件卫生（trailing-whitespace、end-of-file-fixer、mixed-line-ending、BOM、merge-conflict、large-files —— 脚本里一行都没有，pre-commit-hooks 免费提供）；Markdown 格式（完全没有）；slug 大小写冲突（`check-case-conflict` 覆盖"仅大小写不同"的文件名冲突）。
- **② 必须自建**：`check_registries`、`check_registry_refs`、`check_registry_page_consistency`、`check_relations`、`check_evidence_refs`、`check_orphan_raw_projects`、`check_misplaced_artifacts`、`check_artifacts`、`check_raw_layout` —— 这 9 个的核心是**跨文件集合对账**（登记表行 ↔ 知识页 ↔ `source_refs` 路径 ↔ 关系字段引用的 ID 是否登记 ↔ 状态一致）。**Vale 与 markdownlint 都是逐文件作用域、无跨文件共享状态，做不到**（此判断属**推断**，基于其作用域模型，未找到反例文档）。这也正是 `github/docs` 要自建 TypeScript 规则层的原因。→ **我们这套 Python 是该自建的，不是造轮子。**
- **③ 盲区**（按严重度）：1. **机密/PII 扫描（最严重）**；2. 外链腐烂；3. 锚点/fragment；4. **术语一致性 / 禁用词 / 强制大小写**（我们有 6 个固定状态词、14 个 ID 前缀、禁止中英夹杂、IBM i 标识符天生大写，**却一条自动检查都没有**）；5. 拼写；6. front matter schema 校验（只有"必需 key 存在 + status 在枚举里 + id 匹配正则"，无类型/结构约束）；7. **CI 与审批门禁本身**；8. 文档即测试（对我们价值低——`tests/validation/` 空、知识页无可执行代码块，属**推断**）；9. **`LINK_RE` 不跳过代码块/行内代码**（低危但已实际发生：本报告因引用链接语法示例产生 3 条假警告）。
- **噪音，别采纳**：`alex`（包容性用语，与 IBM i 迁移知识库无关）、`super-linter`（Docker 巨像且 natural language 不走 Vale）、`muffet`（读不了 Markdown）、`textlint`（Node 插件生态，精确大小写模型弱于 Vale vocabularies）。

### 2.4 IBM i 生态：证据可以从系统里"问"出来

**开源工具链**（star / pushed_at 本次实测）

| 项目 | URL | 活跃度 | 产出什么 |
|---|---|---|---|
| Code for IBM i | https://github.com/codefori/vscode-ibmi （**注意：`codefori/Code-for-i` 返回 404**，本次实测） | 424★，pushed 2026-10-09，MIT | 对象浏览器、源码成员编辑/编译、按成员文本与创建/变更日期过滤 |
| Db2 for i | https://github.com/codefori/vscode-db2i | 77★，2026-10-09 | **SQL 结果集可直接导出 `csv:` / `json:` / `sql:` / `udtf:` / `rpg:`；还能用 `cl:` 前缀在 SQL 脚本里跑 CL 命令**（例 `cl: dspffd sample/employee`）← 批量产出扫描结果的关键 |
| RPGLE Language Tools | https://github.com/codefori/vscode-rpgle | 59★，2026-10-09 | go-to-definition / **show references** / workspace symbols / linter |
| **IBM i MCP Server + `ibmi` CLI** | https://github.com/IBM/ibmi-mcp-server | 85★，2026-10-07，Apache-2.0 | **命令行可脚本化**：`ibmi sql "…" --format csv --output x.csv`、`--stream --format json`(NDJSON)、`ibmi schemas/tables/columns/related/describe/validate`；`ibmi describe` 用 `QSYS2.GENERATE_SQL` 出 DDL；自带 `find_least_recently_used_objects` / `find_stale_objects` / `find_dependent_objects`（仓库存在性与活跃度已实测；**子命令细节未逐条复核**） |
| rpgleparser | https://github.com/rpgleparser/rpgleparser | 61★，**pushed 2025-07-12（约 15 个月未动）** | ANTLR 的 RPGLE 语法/解析器 |
| grammars-v4 | https://github.com/antlr/grammars-v4 | 11,060★，2026-10-09 | 有 `cobol85/`（`Cobol85.g4` + `Cobol85Preprocessor.g4`）；**没有 `rpg/` 目录** |
| IBM/ibmi-oss-examples | https://github.com/IBM/ibmi-oss-examples | 97★，2026-09-28，**已 archived** | 开源工具示例 |

**否证（本次实测）**：`rpgleparser/sonar-rpgle` → **404**；`gh search repos` 对 `sonar rpgle` / `sonarqube rpg` / `sonar ibmi` 均 **0 条** → **不存在开源 RPG SonarQube 插件**。

**IBM i 官方手段**（子调研从 ibm.com 核实并附 URL，本次未逐条复核 → 一手但二手传递）

- 索引页：https://www.ibm.com/support/pages/ibm-i-services-sql 、https://www.ibm.com/support/pages/ibm-i-services
- 程序↔绑定：`QSYS2.PROGRAM_INFO`、`QSYS2.BOUND_MODULE_INFO`、`QSYS2.BOUND_SRVPGM_INFO`、`QSYS2.PROGRAM_EXPORT_IMPORT_INFO`、`QSYS2.PROGRAM_RESOLVED_ACTIVATIONS()`、`QSYS2.PROGRAM_RESOLVED_IMPORTS`
- 对象清单/使用度：`QSYS2.OBJECT_STATISTICS()`（含 `LAST_USED_TIMESTAMP`、`DAYS_USED_COUNT` → **死代码候选**）、`QSYS2.IFS_OBJECT_STATISTICS`、`QSYS2.SAVE_FILE_OBJECTS()`
- 字段/表：`QSYS2.SYSTABLES`、`QSYS2.SYSCOLUMNS`、`QSYS2.SYSCOLUMNS2`、`QSYS2.SYSROUTINES`、`QSYS2.SYSSCHEMAS`、`SYSMEMBERSTAT`
- 文件→依赖对象：`SYSTOOLS.RELATED_OBJECTS`（返回 INDEX/VIEW/TRIGGER/LOGICAL FILE/MQT/MASK/PERMISSION…）
- DDL 生成：`QSYS2.GENERATE_SQL`；报表：`SYSTOOLS.GENERATE_SPREADSHEET()`、`SYSTOOLS.GENERATE_PDF()`
- 权限：`QSYS2.OBJECT_OWNERSHIP`、`QSYS2.OBJECT_PRIVILEGES()`、`QSYS2.AUTHORIZATION_LIST_USER_INFO`、`QSYS2.AUTHORITY_COLLECTION`、`QSYS2.GROUP_PROFILE_ENTRIES`
- 作业/调度：`QSYS2.SCHEDULED_JOB_INFO`、`QSYS2.SUBSYSTEM_INFO`、`QSYS2.JOB_QUEUE_ENTRIES`、`QSYS2.EXIT_PROGRAM_INFO`、`QSYS2.DATA_QUEUE_INFO`、`QSYS2.JOURNAL_INFO`、`QSYS2.MESSAGE_FILE_DATA`
- CL 命令（真实存在，附官方 URL）：**`DSPPGMREF`**（"a list of the system objects referred to by the specified programs"，参数 `PGM`/`OUTPUT`/`OBJTYPE`/`OUTFILE`/`OUTMBR`，**可写入数据库输出文件，记录格式 `QWHDRPPR`**；无 `DETAIL` 参数）、`ANZOBJCVN`、`DSPFFD`、`DSPMNUA`、`SAVCHGOBJ`；CL 通用 `OUTPUT(*OUTFILE)` 机制
- 死代码官方任务页：https://www.ibm.com/docs/en/ssw_ibm_i_71/rbam6/detob.htm （URL 已核实，正文未抓到）

**否证（重要）**：`QSYS2.OBJECT_DEPENDENCIES`、`QSYS2.SYSROUTINEDEP`、`QSYS2.SYSTOOLS` **在 IBM i 资料中查不到**；`SYSROUTINEDEP`/`*DEP` 属 **Db2 for LUW** 的 `SYSCAT`（https://www.ibm.com/docs/zh/SSEPGG_11.5.0/com.ibm.db2.luw.sql.ref.doc/doc/r0021695.html ）。本次 WebSearch 独立复核也只返回 CSDN 类二手内容、**无 IBM 官方命中** → 支持"不存在"判断，但严格说属"未能证实存在"。**这些名字一律不得写进知识页。**

**变更管理工具**（对 `PRJ-####` 最关键）：ARCAD（Skipper/Observer/Verifier）、Rocket Lifecycle Manager IBM i Edition（原 Aldon LM i，公开用户指南 PDF：https://docs-be.rocketsoftware.com/bundle/Aldonlmi_userguide_V84/raw/resource/enus/Aldonlmi_userguide_V84.pdf ，**正文未能提取，能力未核实**）、Turnover/Precis（**未找到厂商一手页面**，只有第三方课程页 → 未核实）、IBM Rational Synergy。它们记录的"某次发布/变更单改了哪些对象"，**就是我们 `PRJ-####` 想要的一手证据**。

**商业遗留分析工具**（**全部为厂商宣传，能力未核实**）

| 工具 | 来源 | 宣传的产物 |
|---|---|---|
| ARCAD Observer | https://www.arcadsoftware.com/arcad/products/arcad-observer-application-analysis/ ・ https://www.ibm.com/support/pages/arcad-observer-ibm-i | Cross references、Impact Analysis、Documentation（**可直接输出到 Confluence**）、Diagrams、Flowcharts、**Where-used**、Database analysis、List manager |
| Fresche X-Analysis | https://freschesolutions.com/products/x-analysis/ | Impact Analysis（"see where **programs, fields, files and variables** are used"）、Dependency Mapping、Automated Documentation、**Business Rule Extraction（RPG、COBOL、Synon）**、Data Model Extraction、Design & Quality Metrics |
| X-Analysis View | https://freschesolutions.com/products/x-analysis-view/ | data flow diagrams、**call stack**、where-used、object use/access & parameters、**RPG 转伪代码**、从 **DDS** 反出关系数据模型 |
| OpenText/Micro Focus Enterprise Analyzer | https://origin-www.microfocus.com/media/data-sheet/enterprise_analyzer_ds.pdf | "Enterprise-class application repository"、"**Code slicing facility**"、"…**redundant code**"、"**REST API and Jenkins Plugin**"、OpenText Business Rule Manager |
| CAST Imaging | https://learn.castsoftware.com/case-studies/global-advisory-demystifies-and-maps-an-ibm-as400-black-box-system-with-gen-ai | **未找到 IBM i 支持声明**，仅一篇案例研究 |
| watsonx Code Assistant for Z | https://ibm-wsc.github.io/website/wca4z/ | application discovery、code explanation、auto refactoring to business services、**COBOL→Java**、auto-generated tests |
| IBM i Modernization Engine (Merlin) | https://www.ibm.com/cn-zh/products/ibm-i-merlin | URL 核实，能力清单未核实 |

**对照表：业界标准产物 vs 我们 `raw/_types/` 现有 8 类**

现有 8 类：`business-documents`、`code-scan-results`、`control-files`、`data-dictionary`、`diagrams-and-images`、`fe-menus`、`test-cases`、`test-results`。

| 业界标准产物 | 覆盖情况 | 判定 |
|---|---|---|
| 对象/程序清单（创建日、变更日、大小、TEXT、源码成员） | `code-scan-results` 勉强可放 | **半缺口**：应明确"资产清单"是独立产物形态（CSV） |
| 程序↔对象交叉引用（`DSPPGMREF`） | 无 | **缺口** |
| 服务程序/模块绑定依赖（`PROGRAM_EXPORT_IMPORT_INFO` 等） | 无 | **缺口** |
| 字段级 where-used / 字段级血缘 | `data-dictionary` 只有字段定义 | **缺口（商业工具专属）** |
| 文件→依赖 SQL 对象（`RELATED_OBJECTS`） | 无 | **缺口** |
| **死代码 / 未使用对象清单**（`LAST_USED_TIMESTAMP`） | 无 | **缺口** |
| **按发布/变更单的对象变更清单 + 晋升历史** | `PRJ-####` 只是目录维度，**没有对应材料类型** | **缺口（最关键）** |
| 权限与用户 profile / 对象属主 / 授权列表 | 无 | **缺口** |
| 批处理与调度清单（`SCHEDULED_JOB_INFO`、子系统、作业队列、退出程序、数据队列、日志接收器） | 混在 `business-documents` 里 | **缺口** |
| 5250 显示文件（DDS）字段级屏幕图 | `fe-menus` 只到菜单 | **半缺口** |
| 消息文件（`MESSAGE_FILE_DATA`） | 无 | **缺口** |
| 复杂度/质量度量与 lint 结果 | 与 `code-scan-results` 混同 | **半缺口**：建议把"元数据扫描"与"静态分析结论"分开 |
| 覆盖率报告（`*LINE`/`*PROC`） | `test-results` 可放 | 已覆盖，但需规定格式 |
| DDL 反向生成文本 | 无 | **缺口**（`GENERATE_SQL` 产出，属元数据非源码，仍需批准） |
| PTF / OS 基线 | 无 | 缺口（可列为可选） |

**能否纯文本导出**（符合"只放批准的扫描输出、不放源码"约束）

- **可以**：上表除"字段级 where-used / 语句级调用图 / 业务规则抽取 / 自动数据流图"外**全部**。两条路径：(a) `OUTPUT(*OUTFILE)` + `SELECT` 导 CSV；(b) `ibmi sql --format csv --output`（或 db2i 的 `csv:` 前缀、`SYSTOOLS.GENERATE_SPREADSHEET()`）。
- **必然依赖商业工具**：跨语言字段级 where-used、语句级调用图、业务规则抽取、自动流程图/数据流图、代码切片。
- **灰色地带（推断）**：`rpgleparser`（ANTLR）理论上能对 RPGLE 源码离线跑出 caller/callee 或字段引用 CSV——产物是纯文本、不含源码，但需有人在**经批准的环境**里执行；该仓库已约 15 个月未更新，风险需评估。

---

## 3. 推断（未验证）

| # | 推断 | 依据 | 需要什么证据 |
|---|---|---|---|
| I1 | 我们的文档象限归属（`knowledge/`=reference、`docs/workflows.md`+`CONTRIBUTING.md`=how-to、`analysis/reports/`=explanation、README 混写） | Diátaxis 定义 + 抽样阅读，**未逐字读完全部文档** | 逐份通读并按 Diátaxis 判定表核对 |
| I2 | **aider repo map 与我们的路线对比**：map 前提是"仓库里有可解析源码"且有用上下文是结构性的（tree-sitter + personalized PageRank，`--map-tokens` 默认 1024）；我们没源码、需要的是语义/业务性知识，**tree-sitter 与 PageRank 推不出"RULE-0007 取代 RULE-0003"** → 语义层不输。但四种情况会输：① 覆盖率/规模（人工页做不到数千程序全覆盖）② 时效（map 每次重算 vs 人工页**静默腐化**）③ 一旦源码可得 ④ 成本（map 边际成本≈0） | 已核实 `aider/repomap.py` 用 `tree_sitter.Query` + `nx.pagerank` + 默认 1k token 预算；对比结论为推断 | 拿真实程序清单试算覆盖率与人工成本 |
| I3 | Vale / markdownlint **做不了**跨文件集合对账 | 基于二者的逐文件作用域模型，未找到反例文档 | 实测：写一条 Vale `script` 规则尝试跨文件读登记表 |
| I4 | PEP 编号"永不复用" | PEP 1 只说"not used by a published or in-PR PEP"，无 "never reused" 字样 | 找 PEP 编辑流程的明文 |
| I5 | `front_matter()` 改严格模式的具体实现方案（遇缩进映射/块标量/重复键显式报错） | 读了源码第 255 行 | 写测试用例验证不破坏现有 15 个模板 |
| I6 | `ibmi` CLI 的子命令与参数细节 | 仓库存在性与活跃度已实测，子命令未逐条复核 | 在批准环境里跑 `ibmi --help` |
| I7 | "文档即测试"对我们价值低 | `tests/validation/` 为空、知识页无可执行代码块 | 若 Phase 4 引入行为对比脚本则需重估 |

---

## 4. 冲突

| # | 来源 A | 来源 B | 差异 | 谁能裁决 |
|---|---|---|---|---|
| C1 | KEP-0000 文档写 `reviewers` **Required** | `api/proposal.go` 的 `validate:"required"` tag 只覆盖 `Title/kep-number/authors/owning-sig/approvers/status` | **文档与门禁不一致**（外部冲突）。参考价值：这正是我们 `check_registry_page_consistency` 想防的同类漂移——"写在文档里的规则"和"脚本查的规则"会分家 | 无需我们裁决；作为**设计教训**吸收 |
| C2 | 子调研：根目录含 `.vale.ini` 的仓库 **2,320 个** | 本次实测：`search/code?q=filename:.vale.ini` → **4,256 个文件** | 查询口径不同（仓库数 vs 文件数、是否限定根目录），**未复现** | **两个数字都不要引用**为"有多少项目在用 Vale"；只能说"数千量级" |
| C3 | 二手来源称 Google 的 John Mueller 表态 llms.txt 无助于被 AI 发现（一手引文**未取到**） | 同一 Google 的 **Chrome Lighthouse 把 llms.txt 列入 agentic browsing 审计**（此点有一手依据） | llms.txt 的实际价值存在争议 | 未裁决。对我们影响有限：仓库内索引的价值不依赖 SEO 争论 |
| C4 | AGENTS.md「**不引入第三方依赖**」+ README「没有接入任何 MCP 服务」 | 本次调研的高价值建议（CI workflow、Vale、lychee、`ibmi` MCP Server） | **字面冲突** | **需你裁决**。折中三原则见下 |

**C4 的折中方案（供裁决）**：CI runner 上装的工具**永远不进入仓库依赖树**——我们连 `package.json`/`requirements.txt`/`pyproject.toml` 都没有（已核实），没有可被污染的清单文件。

1. **CI-only**：workflow 里按 **commit digest 钉版本**（`github/docs` 就是这么做的）；
2. **`scripts/validate_repo.py` 永不 import 它们**，保持零依赖、可本地裸跑；
3. 在 `CONTRIBUTING.md` / `docs/` 里写成**开发者可选工具**，明说"CI 会跑，本地不装也能贡献"。

注意：README 现在写的是"**没有**接入任何代码扫描 Skill、MCP 服务或 RAG 平台"——这句话描述的是**仓库自身不含这些能力**，与"开发者用 MCP/CLI 从 IBM i 导出 CSV 再放进 `raw/`"并不矛盾，但**措辞需要澄清**，否则会自我打脸。

---

## 5. 缺口

- **本次未覆盖**（你没选）：迁移方法论（Konveyor + KAI 的 rulesets-as-data、AWS 6R、strangler fig、波次规划）；数据目录与元数据治理（DataHub / OpenMetadata / Amundsen 的术语表与认证状态、W3C SKOS 的别名与关系模型、PROV 溯源本体）。**建议下一轮补 SKOS 与 PROV**——它们直接对应我们的 `TERM-`/`aliases` 与 `source_refs`。
- **`requirements/`（Phase 3）只做了目录约定对标**（spec-kit、Kiro），没有真实产物可验证。
- **未核实项**：Kiro inclusion modes 的具体取值；cursor.directory 站内内容（被人机验证挡住）；Rocket LMi 用户指南 PDF 正文；CAST Imaging / Turnover 的真实能力；`github/docs` 与 `rust-lang/book` 的 workflow 细节（二手传递）。
- **需要谁确认**：
  - **SME / 系统负责人**：能否产出 `QSYS2.OBJECT_STATISTICS` 全量 CSV、`DSPPGMREF *OUTFILE` 导出、变更管理工具的发布历史导出；哪些材料获批准进 `raw/`。
  - **仓库管理员**：CODEOWNERS 与分支保护（"Require review from Code Owners"）需要 admin 权限。
  - **你**：C4 的裁决（零依赖约束的边界）、是否引入 `status × stage` 两维、知识索引是手工维护还是加生成脚本。

---

## 6. 改进清单（backlog）

**核实等级**：`实测` = 本次会话直接核实；`一手` = 子调研读到原文；`二手` = 未复核。
**约束列**：`OK` = 与"零依赖"无冲突；`裁决` = 与 AGENTS.md 字面冲突，需你决定。

### P0 — 零依赖、纯 Markdown、马上可做

| # | 建议 | 对标来源（核实等级） | 涉及文件 | 约束 |
|---|---|---|---|---|
| 1 | **加机密/PII 扫描**（纯 stdlib 正则：PEM/私钥块、常见 token 前缀、AWS key 形态、连接串）。规则 #10 目前**零机器防线** | pre-commit `detect-private-key`/`detect-aws-credentials`（实测）；自证盲区（实测） | `scripts/validate_repo.py` | OK |
| 2 | **嵌套 AGENTS.md 做条件加载**：新增 `raw/AGENTS.md`（只读铁律 + `_shared/` 归属）、`knowledge/AGENTS.md`（六状态词 + ID 分配）、`analysis/AGENTS.md`（报告格式）、`templates/AGENTS.md`（选哪个模板）；根 AGENTS.md 的"目录归属"大表瘦身为**路由** | AGENTS.md 官方 "closest wins"（实测）；Claude 官方"子目录 AGENTS.md 在 Read 该目录文件时才加载"（实测） | `AGENTS.md` + 4 个新文件 | OK |
| 3 | **根 AGENTS.md 加"按需加载表"**：给每个指针文件标注"何时才读"。**关键：不要用 `@import`/链接当省上下文手段** | Claude 官方 "Imports … don't reduce its context cost"（实测）；200 行阈值（实测） | `AGENTS.md`、`README.md` 相关文档表 | OK |
| 4 | **front matter 加字段**：`replaces: []`（新页回指被取代 ID，与 `SUPERSEDED` 配对）、`requires: []`（硬前置，区别于 `related_*`）、`change_history: [{date, ref}]`；`reviewed_by` 拆为 **`decision_makers` / `consulted` / `informed`** + 新增 `owner`（页面维护责任人） | PEP `Replaces`/`Superseded-By`/`Requires`/`Post-History`（实测 `check-peps.py`）；MADR RACI 三分（实测模板原文） | `templates/*.md`（15 个）、`docs/knowledge-model.md`、`CONTRIBUTING.md` | OK |
| 5 | **在 `knowledge/registry/README.md` 写死状态机迁移表** + 跨字段断言（`SME_CONFIRMED` 必须同时有 `decision_makers` 与 `reviewed_at`；`SUPERSEDED` 必须有 `superseded_by` 且目标页必须有 `replaces` 回指） | KEP `status × stage` 两维 + 跨字段断言（实测 `proposal.go`） | `knowledge/registry/README.md` | OK |
| 6 | **建"禁用未核实技术名词"清单**（见附录 B），写进证据规范 | 本次否证结果（实测 404 / 官方文档检索） | `docs/evidence-and-validation.md` 或 `CONTRIBUTING.md` | OK |

### P1 — 高价值，需要一点工作量或一次决策

| # | 建议 | 对标来源（核实等级） | 涉及文件 | 约束 |
|---|---|---|---|---|
| 7 | **`raw/_types/` 增设 6 类材料**：`object-inventory`、`cross-references`、`release-manifests`（按对象的变更清单）、`security-authority`、`jobs-and-scheduling`、`generated-ddl`；并把 `code-scan-results` 拆成"元数据扫描"与"静态分析结论/度量"两层 | IBM i SQL Services + `DSPPGMREF`（一手）；商业工具产物清单（厂商宣传） | `raw/_types/*.md`、`raw/README.md`、`README.md` §7.4、`AGENTS.md` 目录归属表、`scripts/validate_repo.py`（未知类型 → ERROR 的白名单） | OK |
| 8 | **写一份"向系统负责人要什么"的材料请求清单**：逐项给出视图名/命令、导出格式（CSV/NDJSON）、批准与脱敏要求 | IBM i 官方文档（一手）；`ibmi` CLI 与 db2i 导出前缀（一手） | `analysis/` 或 `docs/`（新增） | OK |
| 9 | **`validate_repo.py` 四处补强**：`front_matter()` 改**严格模式**（遇缩进映射/块标量/重复键**显式报错**而非静默跳过）；`check_links` 校验 fragment；断链从 `warn` 分级为 `ERROR`；`LINK_RE` 扫描前**剥离围栏代码块与行内代码**（否则文档写链接语法示例就误报） | 自证盲区（实测第 188/255/679/681/693 行） | `scripts/validate_repo.py`、`scripts/README.md` | OK |
| 10 | **建"每页一行"知识索引**：`knowledge/registry/index.md`，每行 = 方括号内「ID + 规范名」+ 圆括号内相对路径 + 冒号 + 一句话摘要 + 状态词（此处不写成真链接，避免 `LINK_RE` 误报）。让规则 1「先查再建」成本从"打开 N 个页面"降到 ~1 token/页 | llms.txt `## Optional` 约定（实测）；Skills `description` 思路（实测） | `knowledge/registry/index.md`（新）、`knowledge/registry/README.md` | **裁决**：手工维护会漂移；生成器是纯 stdlib，但要定性为"**手工触发的辅助脚本**"并写明，避免违反"不声明未实现的自动化能力" |
| 11 | **合并/映射 W0–W10 与 WF-001…WF-010 两套编号**：单一事实源 + 指针，或加显式映射表 | Claude 官方"矛盾指令会任选一条"（实测） | `docs/workflows.md`、`agents/workflows/README.md`、`README.md` | OK |
| 12 | **15 个模板加 `summary:`（≤200 字符）与 `diataxis:` 象限标注**；**拆分混写的 README**（把 §7.9 提示词与 ID 规范挪出去）。**但不要新建四个空象限目录** | Skills `description` ≤1024（实测）；Diátaxis "别建空结构，那很恶心"（实测原文） | `templates/*.md`、`README.md` | OK |
| 13 | **CI + CODEOWNERS**：`.github/workflows/validate.yml` 在 PR 上跑现成的 `python3 scripts/validate_repo.py`（ubuntu-latest 自带 Python 3，**零新依赖**）；参照 `github/docs` 用 changed-files 只校验改动文件 + weekly 全量 sweep 兜底跨文件影响。`.github/CODEOWNERS` 按 SME 领域绑定 `knowledge/` 路径，**并给 CODEOWNERS 自身设 owner** | PEP/KEP 的机器门禁（实测）；`github/docs` workflow（二手）；GitHub 官方 CODEOWNERS 文档（一手） | `.github/workflows/validate.yml`、`.github/CODEOWNERS`（新） | **裁决**（C4 折中三原则）；需仓库 admin 开分支保护 |
| 14 | **建 arc42 §11 等价的"风险与技术债台账"**：把 `CONFLICTED` 条目、覆盖率缺口、"因证据不足没做的事"沉淀成长期台账，而不是散落在对话报告里 | arc42 12 章（一手） | `analysis/reports/risks-and-debt.md`（长期维护） | OK |

### P2 — 需要外部工具或等 Phase 3

| # | 建议 | 对标来源（核实等级） | 涉及文件 | 约束 |
|---|---|---|---|---|
| 15 | **Vale（CI-only，单个 Go 二进制）**：`accept.txt` 放 6 个状态词 + 14 个 ID 前缀 + IBM i 标识符（靠 `Vale.Terms` 强制精确大写）；`reject.txt` 放禁用词/中英夹杂写法；`capitalization` + `match: $upper` 管 `PGM1100`/`PTSACCT`；`IgnoredScopes = code, text.frontmatter.<key>` | Vale 12 种 check + vocabularies（一手）；GitLab `.vale.ini` 先例（一手）；`.vale.ini` 全 GitHub 数千量级（实测，见 C2） | `.github/workflows/`、（可选）`.vale.ini` + vocabularies | **裁决**（C4） |
| 16 | **lychee 定时查外链**（scheduled，**不挂 PR**，避免外链抖动阻塞合并）；`check_links` 继续做 PR 内相对路径快查 | lychee 唯一声明 respect rate limits（一手） | `.github/workflows/` | **裁决**（C4） |
| 17 | **`requirements/`（Phase 3）抄 Kiro 三件套 + spec-kit 门禁词**：每个 `MT-####` 一个目录含 `requirements.md` / `design.md` / `tasks.md`；加一份一次性 `requirements/constitution.md`。把 spec-kit 的 `converged`、Kiro 的 `verified/partial/failed` 与 `go/needs-clarification/kill` **映射进现有六状态词**，不引入第二套词表 | spec-kit（140,640★，实测）；Kiro 官方 docs（一手） | `requirements/README.md`（Phase 3 时） | **裁决**：只抄目录约定 OK；安装 `specify-cli`（`uv tool install`）**违反零依赖，不建议** |
| 18 | **引入 `status × stage` 两维**（评审生命周期 × 知识成熟度），或至少在文档里说明"我们的 `status` 是两维合体" | KEP `ValidStatuses` × `ValidStages`（实测） | 全部模板 + `docs/knowledge-model.md` + `AGENTS.md` 状态词表 | **破坏性变更，需评审**；注意规则"不静默替换已确认内容" |
| 19 | **补调研 SKOS 与 PROV**（本轮未覆盖）：SKOS 的 `exactMatch`/`closeMatch`/`broader`/`narrower` 直接对应我们的 `aliases` 与实体关系；PROV 对应 `source_refs` 的溯源语义 | 未调研 | — | OK（只是调研） |

---

## 7. 建议动作

**可晋升到 `knowledge/`：无。** 本报告全部是外部对标，不含任何 Reward Plus 业务结论，也没有 `raw/` 材料支撑。**不要**把本报告的任何内容当作系统事实引用。

**需你裁决的 3 件事**

1. **C4：零依赖约束的边界**——CI-only 工具（workflow / Vale / lychee）算不算破例？若算破例，P1-13、P2-15/16 全部搁置，规则 #6 与 13 项校验就继续靠人自觉。
2. **P2-18：是否引入 `status × stage` 两维**——这是改状态词表的破坏性变更，且我们的六状态词是**独有优势**，改错会丢掉 `EVIDENCE_FOUND`/`INFERRED` 二分。
3. **P1-10：知识索引是手工还是加生成脚本**——涉及"不声明未实现的自动化能力"这条约束的解释。

**若只做 3 件事（推荐顺序）**

1. **P0-1 机密扫描**：安全真空，零依赖，改动只在 `scripts/validate_repo.py`。
2. **P0-2 + P0-3 嵌套 AGENTS.md + 按需加载表**：单条就能吃掉"Agent 文档治理"这块的大部分收益，零依赖、零重复。
3. **P1-7 + P1-8 补 `raw/_types/` 品类 + 材料请求清单**：这是**解锁真实材料进场的前置条件**——现在材料进不来，部分原因是我们没告诉对方要导什么。

**本报告自身的处置**：`analysis/reports/*` 默认被 `.gitignore` 忽略（只保留 README）。若要共享给 SME 或仓库管理员，用 `git add -f analysis/reports/2026-10-10-agent-docs-and-ibmi-benchmark.md`，并在 commit message 里说明原因。

**校验记录（自证的一条发现）**：本报告首次落盘后跑 `python3 scripts/validate_repo.py` 得到 **3 条警告**，全部来自正文里引用的**链接语法示例**（llms.txt 的格式说明、fragment 盲区的举例、知识索引的格式示例），并非真断链。原因是 `LINK_RE`（第 188 行）直接扫全文、不剥离代码块与行内代码。已把这 3 处示例改写为非链接写法，并把它登记为 §2.3 盲区 9 与 backlog P1-9 的第四个补强点。**修复后应为 0 警告。**

---

## 附录 A：来源清单与核实等级

**实测**（本次会话用 `gh api` / `curl` / 读源码直接核实）

| 来源 | URL | 关键数字/事实 |
|---|---|---|
| vale-cli/vale | https://github.com/vale-cli/vale | 6,223★，pushed 2026-10-06；`errata-ai/vale` 301 到此（**org 已改名**） |
| DavidAnson/markdownlint | https://github.com/DavidAnson/markdownlint | 6,374★，2026-10-10 |
| lycheeverse/lychee | https://github.com/lycheeverse/lychee | 3,998★，2026-10-05 |
| super-linter/super-linter | https://github.com/super-linter/super-linter | 10,617★，2026-10-09 |
| raviqqe/muffet | https://github.com/raviqqe/muffet | 2,614★ |
| anthropics/skills | https://github.com/anthropics/skills | 180,212★，2026-10-09；`spec/agent-skills-spec.md` 仅 3 行指针 |
| github/spec-kit | https://github.com/github/spec-kit | 140,640★，2026-10-10 |
| Aider-AI/aider | https://github.com/Aider-AI/aider | 49,446★，pushed 2026-05-22 |
| AnswerDotAI/llms-txt | https://github.com/AnswerDotAI/llms-txt | 2,655★ |
| evildmp/diataxis-documentation-framework | https://github.com/evildmp/diataxis-documentation-framework | 1,248★，2026-10-05 |
| adr/madr | https://github.com/adr/madr | 2,541★；模板 front matter 逐字核实 |
| joelparkerhenderson/architecture-decision-record | https://github.com/joelparkerhenderson/architecture-decision-record | 17,145★ |
| npryce/adr-tools | https://github.com/npryce/adr-tools | 5,728★，pushed **2024-04-25（停更）** |
| python/peps | https://github.com/python/peps | 5,025★；`check-peps.py:61-74` 状态枚举逐字核实 |
| kubernetes/enhancements | https://github.com/kubernetes/enhancements | 3,964★；`api/proposal.go:44-51,74-82` 逐字核实 |
| rust-lang/rfcs | https://github.com/rust-lang/rfcs | 6,612★ |
| google/eng-practices | https://github.com/google/eng-practices | 23,298★，**archived=true**（2024-09-19） |
| codefori/vscode-ibmi | https://github.com/codefori/vscode-ibmi | 424★，2026-10-09 |
| codefori/vscode-db2i | https://github.com/codefori/vscode-db2i | 77★，2026-10-09 |
| IBM/ibmi-mcp-server | https://github.com/IBM/ibmi-mcp-server | 85★，2026-10-07，Apache-2.0 |
| rpgleparser/rpgleparser | https://github.com/rpgleparser/rpgleparser | 61★，pushed **2025-07-12** |
| antlr/grammars-v4 | https://github.com/antlr/grammars-v4 | 11,060★；有 `cobol85/`，**无 `rpg/`** |
| agents.md 规范 | https://agents.md/ | "closest wins" / "required fields?" / nested 逐字核实 |
| Claude Code memory | https://code.claude.com/docs/en/memory | 200 行阈值 / imports 不省上下文 / 矛盾指令任选一条 / 子目录 AGENTS.md 加载时机，逐字核实 |
| Cursor Rules | https://cursor.com/docs/context/rules | `.mdc` 必需 / `alwaysApply` 语义，逐字片段核实 |
| Agent Skills 规范 | https://agentskills.io/specification | `description` ≤1024 / ~100 tokens / 5000 tokens / under 500 lines，逐字核实 |
| llms.txt 规范 | https://llmstxt.org/ | H1 唯一必需 / `## Optional` 约定，逐字核实 |
| GitHub code search | `gh api search/code` | AGENTS.md 1,097,728；CLAUDE.md 874,496；llms.txt 180,224；.cursorrules 34,688；`.vale.ini` 4,256（**口径见 C2**） |
| 本仓自证 | `scripts/validate_repo.py` | 第 255 / 679 / 681 / 693 行；零 secret 扫描；无 `.github/` |
| 404 否证 | `codefori/Code-for-i`、`rpgleparser/sonar-rpgle` | 均返回 HTTP 404（实测） |

**一手（子调研读到原文，本次未逐条复核）**：arc42 https://docs.arc42.org/ ・ c4model https://c4model.com/tooling ・ Structurizr https://docs.structurizr.com/ ・ GitHub CODEOWNERS 官方文档 ・ Vale vocabularies/12 种 check 文档 ・ GitLab `.vale.ini` 与 17 条自定义规则 ・ `github/docs` 与 `rust-lang/book` 与 `kubernetes/website` 的 `.github/workflows/` ・ pre-commit-hooks / check-jsonschema / cspell / textlint / alex / pytest-codeblocks / mdBook ・ IBM i Services 索引页与 `QSYS2.*` / `SYSTOOLS.*` 视图名 ・ `DSPPGMREF` / `ANZOBJCVN` / `DSPFFD` / `DSPMNUA` / `SAVCHGOBJ` 官方文档页 ・ Kiro https://kiro.dev/docs/specs/ 与 /docs/steering/ ・ IBM/ibmi-tobi（84★）・ IBM/ibmi-oss-examples（97★，archived）・ uwol/proleap-cobol-parser（209★）・ eclipse-che4z/che-che4z-lsp-for-cobol（119★）・ openmainframeproject/cobol-check（108★）

**厂商宣传（能力未核实）**：ARCAD Observer ・ Fresche X-Analysis / X-Analysis View ・ OpenText/Micro Focus Enterprise Analyzer ・ Rocket Lifecycle Manager (Aldon LM i) ・ CAST Imaging 案例 ・ IBM watsonx Code Assistant for Z ・ IBM i Merlin

## 附录 B：被否证的说法（**不得写进知识页**）

| 错误说法 | 事实 | 核实方式 |
|---|---|---|
| `codefori/Code-for-i` | **404**，真实仓库是 `codefori/vscode-ibmi`（产品名 Code for IBM i） | `gh api` 实测 |
| `rpgleparser/sonar-rpgle`（RPG 的 SonarQube 插件） | **404**；`sonar rpgle` / `sonarqube rpg` / `sonar ibmi` 搜索均 0 条 → 不存在开源 RPG Sonar 插件 | `gh api` + `gh search repos` 实测 |
| `QSYS2.OBJECT_DEPENDENCIES`、`QSYS2.SYSROUTINEDEP`、`QSYS2.SYSTOOLS` | IBM i 文档查不到；`*DEP`/`SYSROUTINEDEP` 属 **Db2 for LUW 的 SYSCAT**；schema 是 `SYSTOOLS`（不带 `QSYS2.` 前缀）。改用 `SYSTOOLS.RELATED_OBJECTS` 与 `DSPPGMREF` | 子调研查 IBM 文档 + 本次 WebSearch 独立复核（无官方命中） |
| Vale 在 `errata-ai` org 下 | org **已改名 `vale-cli`**，旧 URL 301 | `gh api` 实测 |
| `errata-ai/RedHat` style 包 | **404**；Red Hat 的配置在 `redhat-documentation/vale-at-red-hat` | 子调研核实 |
| "Adobe 用 Vale" | `org:adobe` 搜 `.vale.ini` **0 命中**；Microsoft 仅 PowerShell 文档仓部分使用；**GitLab 确实在用** | 子调研核实 |
| muffet 能查 Markdown 链接 | 不能：不读 Markdown、不支持相对 URL，是站点爬虫 | 一手对比表 |
| `vale-cli/IBM` style 包 = IBM i 技术标识符规范 | **不是**：它是 IBM Developer Editorial Style Guide（行文风格） | 一手核实 |
