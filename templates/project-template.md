---
id: PRJ-0000
title: "<项目名称>"
artifact_type: project
status: NEEDS_REVIEW
confidence: unknown
aliases: []
year: YYYY
change_type: "unknown"        # 新增 / 修改 / 废弃
in_use: "unknown"             # 是 / 否 / 未知 —— 决定迁移时能不能砍
lan_source: "unknown"         # LAN 上的位置；未进库时这是唯一线索
related_functions: []         # FUNC-####
related_programs: []          # PROG-####
related_rules: []             # RULE-####
related_data: []              # DATA-####
related_config: []            # CFG-####
related_interfaces: []        # IF-####
related_projects: []          # PRJ-#### —— 相关的其他交付（依赖 / 被依赖 / 同一迁移批次）
source_refs: []
created_at: YYYY-MM-DD
updated_at: YYYY-MM-DD
reviewed_by: ""
reviewed_at: ""
---

# <项目名称>

> 本项目页记录的是**遗留系统的一次交付**：某年为了某个 feature 改了什么。
> 材料在 `raw/PRJ-####/`。
>
> **不要把"怎么迁移"写在这里。** 那是 `MT-####`（`requirements/`，Phase 3）。本页只记遗留事实。

## 标识

| 项 | 值 |
|---|---|
| 规范名 |  |
| 别名 / 其他叫法 |  |
| 年度 |  |
| 交付时间 |  |
| 变更性质 | 新增 / 修改 / 废弃 |
| **是否仍在使用** | 是 / 否 / 未知 |
| 判断依据 | 例如：无菜单入口、业务确认已停用、仍有交易量 |
| 材料目录 | `raw/PRJ-####/` |
| LAN 来源 |  |

## 业务意图

**为什么加这个 feature。** 业务想解决什么问题。这是本页最重要的内容——
没有它，后来的人无法判断这个行为能不能砍。

来源必须是业务文档或 SME；自己推出来的标 `INFERRED`。

## 变更范围

**分三类记**：新增 / 修改 / 废弃。**不要只列"涉及了什么"，要说清"改成了什么"。**

| 对象 | ID | 变更性质 | 变更说明 |
|---|---|---|---|
| 功能 | `FUNC-####` | 新增 / 修改 / 废弃 |  |
| 程序 | `PROG-####` |  |  |
| 规则 | `RULE-####` |  |  |
| 数据 | `DATA-####` |  |  |
| 控制参数 | `CFG-####` |  |  |
| 接口 | `IF-####` |  |  |

## 材料

| 项 | 内容 |
|---|---|
| 本 project 材料目录 | `raw/PRJ-####/` |
| 已登记来源 | `SRC-####` |
| 未进库的材料 | LAN 路径 + 为什么没进库 |
| 是否含敏感内容 | 是 / 否 / 未知 |

## 影响与依赖

| 项 | 内容 |
|---|---|
| 依赖的其他 project | `PRJ-####` |
| 被哪些 project 修改过 | `PRJ-####` |
| 影响的外部系统 | `SYS-####` |

## 迁移影响

**只写判断，不写方案。** 方案属于 `requirements/`。

| 项 | 内容 | 状态 |
|---|---|---|
| 建议去留 | 迁移 / 废弃 / 待确认 |  |
| 去留依据 |  |  |
| 迁移批次归属 | 与哪些 `PRJ-` 合并成一个批次 | 待确认 |
| 迁移风险 | 例如：被多个 project 反复改过、无测试覆盖 |  |
| 需要的 SME 确认 |  |  |

## 证据与来源引用

- 来源：`raw/PRJ-####/business-documents/<文件>`，第 N 页 —— <说明>
- 来源：`raw/PRJ-####/code-scan-results/<文件>`，行 N —— <说明>
- 来源：SME <姓名 / 角色>，YYYY-MM-DD —— <说明>

## 已知冲突

| 来源 A | 来源 B | 差异 | 谁能裁决 |
|---|---|---|---|
|  |  |  |  |

## 待解问题

- <问题> —— 需要 <什么证据 / 哪位 SME>
- （或写：暂无）

## 评审记录

| 日期 | 评审人 | 结论 |
|---|---|---|
|  |  |  |
