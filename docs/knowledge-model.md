---
title: 知识模型
artifact_type: documentation
status: NEEDS_REVIEW
confidence: high
created_at: 2026-10-09
updated_at: 2026-10-09
source_refs:
  - path: README.md
  - path: CONTRIBUTING.md
  - path: AGENTS.md
---

# 知识模型

定义：有哪些知识实体、ID 怎么分配、登记表怎么用、实体的生命周期怎么走。

## 1. 实体类型

| 实体 | ID 前缀 | 知识页位置 | 登记表 |
|---|---|---|---|
| 业务功能 | `FUNC-0001` | `knowledge/functions/` | `registry/functions.md` |
| 程序 | `PROG-0001` | `knowledge/programs/` | `registry/programs.md` |
| 业务规则 | `RULE-0001` | `knowledge/business-rules/` | `registry/business-rules.md` |
| 数据实体 | `DATA-0001` | `knowledge/data-and-interfaces/` | `registry/data-entities.md` |
| 接口 | `IF-0001` | `knowledge/data-and-interfaces/` | `registry/interfaces.md` |
| 外部系统（对端） | `SYS-0001` | `knowledge/external-systems/` | `registry/systems.md` |
| 业务术语 | `TERM-0001` | 不单独建页（**行即记录**） | `registry/terms.md` |
| 领域概念 | `CONCEPT-0001` | `knowledge/domain/concepts/` | `registry/concepts.md` |
| 控制参数（可调配置） | `CFG-0001` | `knowledge/configuration/` | `registry/control-params.md` |
| 菜单项 | `MENU-0001` | `knowledge/menus-and-navigation/` | `registry/menu-entries.md` |
| 批量作业 | `JOB-0001` | `knowledge/batch-and-jobs/` | `registry/batch-jobs.md` |
| 测试用例 / 验证规格 | `TEST-0001` | `tests/validation/` | `registry/test-cases.md` |
| 来源材料 | `SRC-0001` | 不单独建页 | `registry/source-materials.md` |
| 迁移项目（遗留交付） | `PRJ-0001` | `knowledge/projects/` | `registry/projects.md` |

说明：

* **数据实体与接口同在 `data-and-interfaces/`**，但 ID 前缀分开（`DATA-` / `IF-`），保持"物理数据结构"与"对外契约"可区分。
* **外部系统 `SYS-` 是接口的另一头**。接口页的"对端系统"字段引用 `SYS-####`，系统本身的职责/协议/负责人写在 `external-systems/`。
  只有"跟外部系统交换"才建 `IF-`；**内部程序之间的调用记在 `PROG-` 页，不建 `IF-`**。
* **批量作业** `JOB-` 是按同一命名模式补充的前缀（初始清单未列），用于作业流层面的知识；批量**程序**仍然登记为 `PROG-`。
* **来源材料**不建独立知识页，只在登记表里记录一行 + 指向 `raw/` 的路径，避免与 `raw/` 重复。
* **业务术语 `TERM-` 同样"行即记录"**：一句话定义足够消歧，拆成两处只会造成不一致。需要展开的概念才建 `CONCEPT-` 页。
* **领域概念 `CONCEPT-` 回答"是什么"，业务规则 `RULE-` 回答"什么条件下怎样"**，两者不重叠。
* **完整数据字典不进知识层**：作为原始输入放 `raw/PRJ-####/data-dictionary/`（登记 `SRC-`），
  `DATA-####` 页用 `dictionary_ref` 引用，只写驱动行为的字段。
* **控制参数 `CFG-` 单独成类**：控制文件是业务规则的隐形载体。物理结构仍按 `DATA-` 记，
  参数语义与"改它影响谁"按 `CFG-` 记。**生产环境的具体值不进知识层**（→ `raw/PRJ-####/control-files/`，敏感）。
  由业务定期维护的业务数据表（如费率表）**不建 `CFG-`**，走 `DATA-`。
* **迁移项目 `PRJ-` 是时间轴，其他前缀是结构轴。** 功能、程序、规则、数据描述系统的**静态结构**；
  `PRJ-` 描述**哪一次交付改动了什么**。一个实体可以在多个 `PRJ-` 里被改动，一次交付也可以横跨多个实体。
  `PRJ-` 同时是 `raw/` 材料目录的一级维度（`raw/PRJ-####/<类型>/`，目录名不带 slug），两边用同一个 `PRJ-####` 对应、靠 ID 而不是名字对照。
  **`PRJ-` 记的是遗留系统里已经发生过的交付，不是迁移任务**——迁移任务用 Phase 3 的 `MT-`，与 `PRJ-` 是多对多。

## 2. ID 规则

* 格式：`<前缀>-<4 位数字>`。
* 从对应登记表的"当前最大 ID" + 1 分配。
* **永不复用、永不重排、永不按含义排序。**
* **ID 里不编码业务含义。** 含义放名称、别名、关系里；编码进去的语义会腐烂。
* 字段级引用：`DATA-0007.EXPIRY_DATE`。
* 文件名：`<ID>-<小写slug>.md`，slug 只是方便人肉查找，可以随时改，ID 不能改。

## 3. 登记表设计

`knowledge/registry/` 下每种实体一个 Markdown 表，只用表格 + 简短说明，不引入框架。

每个登记表文件包含：

* 表头注释：当前最大 ID（分配步骤与冲突处理见 `registry/README.md`）
* 一张表：ID / 规范名 / 别名 / 状态 / 证据引用 / 备注
* "如何追加一行"的说明

**登记表是 ID 与关系的权威来源。** 知识页里的关系字段（如功能页列出的程序 ID）如果与登记表不一致，以登记表为准，改知识页。

### 分配一个新 ID 的步骤

1. 在该类型的登记表里，检索规范名和别名列，确认是否已存在。
2. 不存在 → 新 ID = 当前最大 ID + 1。
3. 追加一行，并更新表头"当前最大 ID"。
4. 用模板创建知识页。
5. **第 3、4 步在同一次提交里完成**，否则会出现"页面有 ID、表里没有"的不一致。

### 重复与歧义怎么解

| 情况 | 处理 |
|---|---|
| ID 精确命中 | 直接用 |
| 别名命中 | 用别名指向的那个 ID |
| 多个候选都像 | **不选**。保留一个候选，其余列为相关项，状态标 `NEEDS_REVIEW`，点名需要哪位 SME 判定 |
| 完全没有 | 分配新 ID，把观察到的所有叫法都记为别名；若只有命名层面的证据，`confidence` 标 `low` |
| 事后发现合并 | 保留数字小的为规范 ID，另一个标 `SUPERSEDED` 并指向规范 ID，更新全部引用，**不删除** |

**Agent 做的分类不是权威结论。** 它只是状态为 `INFERRED` 或 `NEEDS_REVIEW` 的提案。

## 4. 元数据字段

知识页（`knowledge/`、`tests/validation/`）的 front matter：

**必填**

| 字段 | 说明 |
|---|---|
| `id` | 已登记的 ID |
| `title` | 简短标题 |
| `artifact_type` | function / program / business-rule / data-entity / interface / external-system / concept / control-param / menu-entry / batch-job / project / test-case / source-record / business-requirement / function-spec / documentation |
| `status` | 六个状态之一，见 §5 |
| `created_at` / `updated_at` | `YYYY-MM-DD` |

**选填（有信息才填）**

`aliases`、`confidence`、`source_refs`、`related_functions`、`related_programs`、`related_rules`、
`related_projects`、`reviewed_by`、`reviewed_at`、`superseded_by`、`open_questions`、`coverage_note`

`related_projects` 填 `PRJ-####`（哪几次遗留交付改动过本实体），是"这个实体有多热"的唯一线索。
注意区分：`related_projects` 是**遗留交付**，`superseded_by` 是**同一实体的新版本**，两者不是一回事。

不要为了填满而填空字段。空字段是噪音，缺失的字段本身就是信息。

## 5. 状态与生命周期

| 状态 | 含义 |
|---|---|
| `EVIDENCE_FOUND` | 有直接证据支持 |
| `INFERRED` | 推理结论，未直接验证 |
| `NEEDS_REVIEW` | 证据不足，或需专家评审 |
| `SME_CONFIRMED` | 专家明确确认（**必须**同时记录确认人与日期） |
| `CONFLICTED` | 来源互相矛盾 |
| `SUPERSEDED` | 已被更权威的版本取代 |

典型流转：

```text
INFERRED ──▶ EVIDENCE_FOUND ──▶ NEEDS_REVIEW ──▶ SME_CONFIRMED
    │              │                  │
    └──────────────┴──────────────────┴────────▶ SUPERSEDED（+ superseded_by）
                    │
                    └──▶ CONFLICTED（保留冲突，说明裁决方式）
```

要点：

* 任何状态都可以转为 `CONFLICTED` 或 `SUPERSEDED`。
* 只有人能标 `SME_CONFIRMED`，Agent 永远不行。
* 进入 `SUPERSEDED` 时不删除内容，保留"我们曾经相信什么"这条追溯链。
* 已确认的内容发现有误 → 新建条目 + 标记旧的 `SUPERSEDED`，**不静默改写**。

## 6. 关系怎么记

关系记在**两处**：登记表的对应列 + 知识页的 front matter 与正文表格。两边都记是为了双向可导航，但权威来源是登记表。

常见关系：

```text
FUNC-0001 ──实现于──▶ PROG-0003 ──读写──▶ DATA-0007
   │                     │
   ├──受约束于──▶ RULE-0012
   ├──入口──▶ MENU-0004                └──实现──▶ RULE-0012 ──证据──▶ raw/PRJ-####/code-scan-results/...
   └──涉及──▶ IF-0002 ──对端──▶ SYS-0005（外部系统）
                  └──下游──▶ JOB-0006

TERM-0001（业务词） ──消歧并指向──▶ DATA-0007 / RULE-0012 / FUNC-0001
CONCEPT-0002（领域概念） ──展开──▶ TERM-0001

FUNC-0001 / PROG-0003 / DATA-0007 / CFG-0008 ──被改动于──▶ PRJ-0009 ──材料──▶ raw/PRJ-0009/...
```

注意：
* 菜单项与程序**不是**一对一。一个菜单可能触发一串程序，一个程序也可能被多个菜单调用。映射必须有证据，否则标 `INFERRED`。
* **接口的另一头是 `SYS-`。** `IF-` 只在与外部系统交换时建立；内部程序之间的调用记在 `PROG-` 页，不建 `IF-`。
* **`PRJ-` 与实体是多对多。** 行密度高的功能说明它被反复改动（迁移风险高）；一列 `PRJ-` 里的实体集合就是那次交付的改动范围，也是按 project 分批迁移的天然边界。
