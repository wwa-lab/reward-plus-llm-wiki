# templates/ — 知识页模板

新建知识页时从这里复制对应模板。**不要随手改模板结构**——段落一致是为了让不同页面的同一信息出现在同一位置，方便人和 Agent 对照。

## 模板清单

| 模板 | 用途 | ID 前缀 | 知识页位置 |
|---|---|---|---|
| [function-template.md](function-template.md) | 业务功能 | `FUNC-####` | `knowledge/functions/` |
| [program-template.md](program-template.md) | 程序 | `PROG-####` | `knowledge/programs/` |
| [business-rule-template.md](business-rule-template.md) | 业务规则 | `RULE-####` | `knowledge/business-rules/` |
| [data-entity-template.md](data-entity-template.md) | 数据实体 | `DATA-####` | `knowledge/data-and-interfaces/` |
| [interface-template.md](interface-template.md) | 接口 | `IF-####` | `knowledge/data-and-interfaces/` |
| [menu-entry-template.md](menu-entry-template.md) | 菜单项 | `MENU-####` | `knowledge/menus-and-navigation/` |
| [test-case-template.md](test-case-template.md) | 测试用例 / 验证规格 | `TEST-####` | `tests/validation/` |
| [source-record-template.md](source-record-template.md) | 来源材料记录 | `SRC-####` | 登记在 `knowledge/registry/source-materials.md` |
| [system-template.md](system-template.md) | 外部系统（对端） | `SYS-####` | `knowledge/external-systems/` |
| [concept-template.md](concept-template.md) | 领域概念 | `CONCEPT-####` | `knowledge/domain/concepts/` |
| [control-param-template.md](control-param-template.md) | 控制参数（可调配置） | `CFG-####` | `knowledge/configuration/` |
| [batch-job-template.md](batch-job-template.md) | 批量作业 | `JOB-####` | `knowledge/batch-and-jobs/` |
| [project-template.md](project-template.md) | 迁移项目（遗留交付） | `PRJ-####` | `knowledge/projects/` |
| [business-requirement-template.md](business-requirement-template.md) | 业务需求（Phase 3 用） | `REQ-####` | `requirements/` |
| [function-spec-template.md](function-spec-template.md) | 功能规格（Phase 3 用） | `FS-####` | `requirements/` |

最后两个（业务需求、功能规格）是**规划阶段**用的，Phase 1 不会用到；提前准备是为了 Phase 3 不用临时设计格式。

**模板清单与 `knowledge/` 子目录、`knowledge/registry/` 登记表三者必须一一对应**，缺一个就会出现"有模板没地方放"或"有登记表没模板"。
（`batch-job-template.md` 原本约定"等首个 `JOB-` 建立时补建"；2026-10-10 的合成数据演练跑到了 W6 批量作业梳理，
证明这个缺口会当场卡住流程，因此提前补建。）

## 使用方式

1. 在 `knowledge/registry/` 对应登记表里分配 ID。
2. 复制模板到目标目录，改名为 `<ID>-<slug>.md`。
3. 填 front matter：`id`、`title`、`artifact_type`、`status`、`created_at`、`updated_at`。
4. 逐段填写。**没有内容就写"未知"或"不适用"，不要删除段落。**
5. 末尾"证据与来源引用"段落必须填；没有来源的段落不能出现结论。

## front matter 字段

**必填**：`id`、`title`、`artifact_type`、`status`、`created_at`、`updated_at`

**选填**（有信息才填）：`aliases`、`confidence`、`source_refs`、`related_functions`、`related_programs`、
`related_rules`、`related_projects`、`reviewed_by`、`reviewed_at`、`superseded_by`、`open_questions`、`coverage_note`

`related_projects` 填 `PRJ-####`，表示**哪几次遗留交付改动过这个实体**（不是迁移任务，迁移任务用 `MT-`）。
它是"这个实体有多热"的唯一线索：被多个 `PRJ-` 改过 = 迁移风险高。

`status` 只能取：`EVIDENCE_FOUND` / `INFERRED` / `NEEDS_REVIEW` / `SME_CONFIRMED` / `CONFLICTED` / `SUPERSEDED`

## 模板里的示例

模板中的所有示例值都用 `<尖括号>` 或明确标注"（示例，非真实）"。
**绝不允许**把真实 Reward Plus 的程序名、规则、接口、内部路径写进模板示例。

## SME 辅助模板（非知识页）

以下两份文件给业务 SME 和 AS400 SME 使用，**不对应任何知识页目录，也不带 ID**，校验脚本不检查它们的 front matter。

| 文件 | 用途 |
|---|---|
| [sme-quick-guide.md](sme-quick-guide.md) | 速查卡：SME 要判断什么、怎么看依据、哪些不能提交 |
| [sme-review-sheet.md](sme-review-sheet.md) | 审阅表：Agent 结论 + 原文依据 + 判断列，供 SME 填写，协调人据此更新状态 |
