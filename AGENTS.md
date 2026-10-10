# AGENTS.md — Agent 硬性规则

在 Cursor / Codex / 其他 Agent 里打开本仓库时，先读这个文件。
完整规则与工作流见 [agents/README.md](agents/README.md)，细则见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 这是什么仓库

`reward-plus-llm-wiki`：Reward Plus 信用卡积分系统（IBM i / AS400）的**知识仓库**，服务于未来的 Java 迁移。
源码不在这里。这里只有经批准的代码扫描输出、业务文档、菜单导出、测试用例，以及由它们整理出来的知识页。

## 十条硬规则

| # | 规则 |
|---|---|
| 1 | **先查再建。** 创建知识页前必须检索 `knowledge/registry/` 和已有知识页。同一实体就更新旧页面，不新建。 |
| 2 | **证据可追溯。** 尽量给出 `raw/PRJ-####/<类型>/` 路径 + 页码/行号/程序名/用例号，并说明这是哪次交付（`PRJ-`）引入的。**绝不编造**来源、行号、程序关系、测试结果。 |
| 3 | **事实与推断分开。** 用 `EVIDENCE_FOUND` / `INFERRED` 明确区分，无依据的假设要点名。 |
| 4 | **保留冲突。** 文档、扫描结果、测试结果互相矛盾时记录冲突并说明需要评审什么，**不静默选边**。 |
| 5 | **保护原始材料。** 不改写、不搬动 `raw/` 下任何文件；不确定归属的材料放 `raw/_shared/` 并报告，**不要随便塞进一个 project**。规范化结果写进 `analysis/` 或 `knowledge/`。 |
| 6 | **不得假称 SME 确认。** 只有在记录了确认人和日期时才用 `SME_CONFIRMED`。默认标 `NEEDS_REVIEW`。 |
| 7 | **小步增量。** 改最小的文件集。不要基于不完整证据批量生成大量低价值页面。 |
| 8 | **评审后才进权威层。** 证据有歧义或冲突时，先放 `analysis/reports/`，以"提议变更"形式给出。 |
| 9 | **如实说明覆盖范围。** 只分析了一部分就写明"覆盖了 X 个中的 Y 个"，**不得暗示已有完整系统清单**。 |
| 10 | **不泄露敏感信息。** 凭证、令牌、生產数据、個人资料、未经批准的源码，一律不写入文档、示例、报告或 Git 历史。 |

## 状态词表（只能用这六个）

`EVIDENCE_FOUND`（有直接证据）· `INFERRED`（推理未验证）· `NEEDS_REVIEW`（需更多证据或专家评审）·
`SME_CONFIRMED`（专家明确确认，**只能人标**）· `CONFLICTED`（来源矛盾）· `SUPERSEDED`（已被取代）

可选补充字段 `confidence`：`high` / `medium` / `low` / `unknown`。

## ID 规范

`FUNC-0001` 功能 · `PROG-0001` 程序 · `RULE-0001` 规则 · `DATA-0001` 数据实体 · `IF-0001` 接口 · `SYS-0001` 外部系统 ·
`TERM-0001` 业务术语 · `CONCEPT-0001` 领域概念 · `CFG-0001` 控制参数 ·
`MENU-0001` 菜单项 · `JOB-0001` 批量作业 · `PRJ-0001` 迁移项目（遗留交付）· `TEST-0001` 测试用例 · `SRC-0001` 来源材料

4 位数字，从登记表当前最大值 +1 分配；永不复用、永不重排；作废标 `SUPERSEDED` 并指向新 ID。

**`PRJ-` 是时间轴，其余是结构轴。** 它记"哪一次交付改动了什么"，是 `raw/` 的一级目录维度；
它是遗留系统里**已经发生**的交付，不是迁移任务（迁移任务用 Phase 3 的 `MT-`）。

## 目录归属

| 内容 | 目录 |
|---|---|
| 原始材料、批准的代码扫描输出 | `raw/PRJ-####/<类型>/`（只读）；跨 project 的放 `raw/_shared/<类型>/` |
| 材料类型的处理规则 | `raw/_types/`（规则说明，不是材料） |
| 完整数据字典（字段定义） | `raw/PRJ-####/data-dictionary/`（**不复制进 `knowledge/`**，只引用） |
| 控制参数的实际值（配置快照） | `raw/PRJ-####/control-files/`（**敏感，默认不提交**；语义在 `knowledge/configuration/`） |
| 中间分析、候选映射、冲突/覆盖率报告 | `analysis/reports/` |
| 已评审的知识页 | `knowledge/<类别>/` |
| 业务术语与领域概念 | `knowledge/registry/terms.md`（术语）、`knowledge/domain/concepts/`（概念） |
| 控制参数语义与反向映射 | `knowledge/configuration/`（`CFG-####`；**不写生产值**） |
| 交付改动范围与影响面 | `knowledge/projects/`（`PRJ-####`；**不写迁移方案**） |
| ID 与关系登记表 | `knowledge/registry/` |
| 可复用验证规格 | `tests/validation/` |
| 未来的需求与设计 | `requirements/`（规划中） |

判断不了放 `analysis/` 还是 `knowledge/` → 放 `analysis/`。

## 禁止事项

* 不执行 `git commit` / `git push` / 任何发布操作。
* 不修改、移动、删除 `raw/` 下任何文件。
* 不静默替换已确认或 `SME_CONFIRMED` 的内容（用新增 + `SUPERSEDED`）。
* 不引入第三方依赖、数据库、向量库、图库、Web 应用。
* 不声明未实现的自动化能力（没有摄取流水线、没有扫描 Skill 集成、没有 RAG）。
* 不批量打印 `raw/` 的完整内容。

## 完成时要报告

1. 新增/修改了哪些文件（完整路径）
2. 登记了哪些 ID
3. 哪些结论是 `INFERRED` / `NEEDS_REVIEW`
4. 发现了哪些冲突，谁来裁决
5. 覆盖范围（分析了多少、总共多少）
6. 哪些事因为证据不足而**没有做**
7. 建议的下一步最小动作
