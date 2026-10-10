# knowledge/ — 已评审的知识

这是全仓库唯一的**权威层**。放进来的是：有 ID、有证据、经过评审的结论。

## 与其他目录的关系

```text
raw/（输入） ──▶ analysis/（中间结论） ──▶ knowledge/（权威） ──▶ requirements/（未来设计）
```

* `raw/` 是材料，`knowledge/` 是结论。
* `analysis/` 可以随便推翻重写，`knowledge/` 的变更要评审。
* 知识页**引用** `raw/`，不复制它。
* `raw/` 里的材料按 project 分目录（`raw/PRJ-####/<类型>/`），与 `knowledge/projects/` 的 `PRJ-####` 一一对应。

## 规则

1. **没有证据不进来。** 每条实质结论都要有来源引用（路径 + 页码/行号/用例号）。
2. **一个实体一份页面。** 同一程序、同一规则只允许存在一页。发现重复 → 保留数字小的 ID，另一个标 `SUPERSEDED`。
3. **先登记 ID，再建页面**，两者同一次提交完成。
4. **Agent 可以建草稿，但不能定权威。** 它能标 `EVIDENCE_FOUND`（附来源）、`INFERRED`、`NEEDS_REVIEW`、`CONFLICTED`；`SME_CONFIRMED` 只能由人标记并记录确认人与日期。
5. **不静默改写已确认内容。** 发现错误 → 新建条目 + 旧条目标 `SUPERSEDED`，保留"我们曾经相信什么"这条追溯链。
6. **用模板。** 从 `templates/` 复制，保留所有段落；没内容就写"未知"。

## 子目录

| 子目录 | ID | 放什么 |
|---|---|---|
| `registry/` | — | 稳定 ID、规范名、别名、关系的登记表（权威来源） |
| `functions/` | `FUNC-####` | 业务功能：业务语言描述的能力 |
| `programs/` | `PROG-####` | 程序：职责、调用关系、数据访问（**不拷源码**） |
| `business-rules/` | `RULE-####` | 可独立识别的业务规则 |
| `data-and-interfaces/` | `DATA-####` / `IF-####` | 数据实体、文件结构、字段、API、外部接口 |
| `external-systems/` | `SYS-####` | 外部对端系统：职责、协议、接口清单、SLA |
| `domain/` | `CONCEPT-####` | 领域概念：定义、边界、口径、生命周期（术语在 `registry/terms.md`） |
| `configuration/` | `CFG-####` | 控制参数：参数项、取值域、反向映射、迁移影响 |
| `menus-and-navigation/` | `MENU-####` | 菜单项与导航路径到功能/程序的映射 |
| `batch-and-jobs/` | `JOB-####` | 批量作业、调度、依赖、执行顺序 |
| `projects/` | `PRJ-####` | 时间轴：每次交付的业务意图、改动清单、影响面（**不写迁移方案**） |
| `architecture/` | — | 系统级架构、组件、集成关系、环境约束 |

**扁平文件，不为每个功能建子目录。** 只有当某个主题真的积累了多个文件才建目录。

## 文件命名

```text
FUNC-0001-<功能slug>.md
PROG-0003-<程序名>.md
RULE-0012-<规则slug>.md
DATA-0007-<实体名>.md
IF-0002-<接口slug>.md
SYS-0003-<系统slug>.md
CONCEPT-0004-<概念slug>.md
CFG-0005-<控制文件slug>.md
MENU-0004-<菜单slug>.md
JOB-0006-<作业slug>.md
PRJ-0009-<交付slug>.md
```

（以上仅为命名**格式**示例，不是真实记录。请勿使用臆造的程序名或表名。）

## 阅读顺序

**先读 `registry/`** —— 它告诉你已经识别了什么、ID 是什么、如何关联。然后按 ID 跳到具体页面。

遇到不认识的**业务词**，先查 [`registry/terms.md`](registry/terms.md)（消歧层）；需要展开的概念看 [`domain/`](domain/)。
