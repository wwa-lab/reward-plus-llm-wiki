# requirements/ — 未来的需求与设计

> **本目录当前只有说明，没有内容。以下全部是"规划中"，尚未实现。**

## 定位

`requirements/` 描述系统**应该**做什么；`knowledge/` 描述系统**现在**做什么。两者互不覆盖。

| 问题 | 归属 | 前缀 |
|---|---|---|
| 遗留系统现在怎么做？ | `knowledge/` | `FUNC-` `PROG-` `RULE-` `DATA-` `IF-` `MENU-` `JOB-` |
| 业务需要什么？ | 本目录 | `REQ-####` |
| 必须实现什么行为（技术中立）？ | 本目录 | `FS-####` |
| Java 怎么实现？ | 本目录 | `TD-####` |
| 交付工作怎么拆？ | 本目录 | `MT-####` |

## 规划中的子结构

Phase 3 开始前不建空目录。届时按需要创建：

| 子目录 | 内容 | 前缀 |
|---|---|---|
| `business-requirements/` | 业务需求：业务意图与验收标准 | `REQ-####` |
| `function-specs/` | 功能规格：技术中立的可测行为 | `FS-####` |
| `target-design/` | Java 技术设计与 API/数据契约 | `TD-####` |
| `migration-tasks/` | 迁移任务、依赖与验收 | `MT-####` |

对应模板已提前备好：[business-requirement-template.md](../templates/business-requirement-template.md)、
[function-spec-template.md](../templates/function-spec-template.md)。`TD-` / `MT-` 模板在需要时补建。

## 将来要在这里装的内容

* 业务需求
* 功能规格
* **现状 vs 目标行为对比**
* Java 技术设计
* API 与数据契约
* 迁移工作分解结构
* 迁移任务与依赖关系
* 测试计划与验收标准
* 新旧系统验证

## 铁律（将来也必须遵守）

1. **遗留行为不等于需求。** 代码里发现的未文档化行为只是候选，人批准后才成为需求。
2. **保留 vs 变更必须写明**：每个规格逐条说明是沿用、变更还是废弃，变更要记录批准人。
3. **`REQ` 与 `FS` 必须技术中立**：不出现程序名，不出现 Spring/Java 之类的实现词。
4. **目标设计不得覆盖遗留知识。** 若新证据显示遗留行为理解有误 → 改 `knowledge/`（新增 + `SUPERSEDED`），再回来修订设计。
5. **每一环都要能追溯**：`REQ` → `FS` → `TD` → `MT` → `TEST`，断环就是待解问题。

## 现在该做什么

什么都不用做。先把 `knowledge/` 里的一两个功能摸透，Phase 3 才有东西可写。
