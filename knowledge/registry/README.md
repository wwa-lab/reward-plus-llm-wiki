# knowledge/registry/ — 登记表

稳定 ID、规范名、别名、实体关系的**权威来源**。

用轻量 Markdown 表实现，不引入框架、不引入数据库。当登记表大到手工难维护时，那才是引入工具的信号——不是现在。

## 文件清单

| 文件 | 实体 | ID 前缀 | 当前最大 ID |
|---|---|---|---|
| [functions.md](functions.md) | 业务功能 | `FUNC-####` | 0 |
| [programs.md](programs.md) | 程序 | `PROG-####` | 0 |
| [business-rules.md](business-rules.md) | 业务规则 | `RULE-####` | 0 |
| [data-entities.md](data-entities.md) | 数据实体 | `DATA-####` | 0 |
| [interfaces.md](interfaces.md) | 接口 | `IF-####` | 0 |
| [menu-entries.md](menu-entries.md) | 菜单项 | `MENU-####` | 0 |
| [batch-jobs.md](batch-jobs.md) | 批量作业 | `JOB-####` | 0 |
| [test-cases.md](test-cases.md) | 测试用例 / 验证规格 | `TEST-####` | 0 |
| [source-materials.md](source-materials.md) | 来源材料 | `SRC-####` | 0 |
| [systems.md](systems.md) | 外部系统（对端） | `SYS-####` | 0 |
| [terms.md](terms.md) | 业务术语（消歧层） | `TERM-####` | 0 |
| [concepts.md](concepts.md) | 领域概念 | `CONCEPT-####` | 0 |
| [control-params.md](control-params.md) | 控制参数（可调配置） | `CFG-####` | 0 |
| [projects.md](projects.md) | 迁移项目（遗留交付） | `PRJ-####` | 0 |

**全部为空。「当前最大 ID = 0」表示尚未分配任何 ID。** 不要为了让表好看而编造记录——编出来的 ID 会污染整条证据链。

**`projects.md` 与 `source-materials.md` 是两张索引表，不是实体表。** `projects.md` 记交付（时间轴：
`PRJ-` ↔ 名称 ↔ 年份 ↔ 改动类型 ↔ `raw/` 目录）；`source-materials.md` 记材料位置（`SRC-` ↔ LAN 路径 ↔ `PRJ-`）。
两者合起来回答"这批材料是哪次交付的、在哪、进库了没有"——**材料留在 LAN 上没进库时，这是唯一的线索。**

## 如何登记一个新实体

1. 打开对应类型的登记表。
2. 检索"规范名"和"别名"两列，确认是否已存在。
3. 不存在 → 新 ID = 当前最大 ID + 1（4 位数字，例如 `0012`）。
4. 追加一行，至少填：ID、规范名、别名、状态、证据引用。
5. **更新文件头部的"当前最大 ID"**。
6. 用模板创建知识页，**与第 4、5 步在同一次提交里完成**。

## 如何避免 ID 冲突

* 一个 ID **只在一张表里出现一次**；跨类型也不能撞。
* 分配前先全表搜索规范名与别名，再决定是新建还是复用。
* 不确定是否为同一实体 → **不新建**。先标 `NEEDS_REVIEW`，点名需要哪位 SME 判定。
* 事后发现重复 → 保留数字小的为规范 ID，另一个标 `SUPERSEDED` 并指向规范 ID，更新所有引用，**不删除**。
* 批量作业时注意：批量**程序**用 `PROG-`，作业**流**用 `JOB-`。

## 命名不一致怎么办

同一个实体被叫成多个名字是常态（业务叫法、报表叫法、程序名、缩写）。处理方式：

* 选一个规范名（业务侧最常用的叫法）。
* 其他全部记进"别名"列。
* 多个名字都指向同一个 ID，**不建多个页面**。
* 在"备注"里写明命名不一致的发现（"业务称 A，程序称 B"），这本身就是有价值的缺口信息。

## Agent 的使用约束

* Agent **可以**追加状态为 `EVIDENCE_FOUND` / `INFERRED` / `NEEDS_REVIEW` / `CONFLICTED` 的行。
* Agent **不可以**标 `SME_CONFIRMED`。
* Agent **不可以**删除或改写已有行；发现错误就新增一行并标 `SUPERSEDED`。
* Agent 的分类结论不是权威，未定项的处置方式见各表文件内的说明。
