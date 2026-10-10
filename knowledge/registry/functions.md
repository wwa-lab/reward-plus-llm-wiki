# 登记表：业务功能（FUNC）

**当前最大 ID：0**（尚未分配任何 ID）

规范见 [registry/README.md](README.md) 与 [../../CONTRIBUTING.md](../../CONTRIBUTING.md)。

| ID | 规范名 | 别名 | 触发方式 | 相关程序 | 相关规则 | 状态 | 证据引用 | 备注 |
|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — | — |

（暂无记录。上表首行仅为占位，正式登记时替换。）

## 如何追加一行

1. 检索本表的"规范名"与"别名"列，确认功能尚未登记。
2. 新 ID = 当前最大 ID + 1，例如 `FUNC-0001`。
3. 填写：规范名（业务侧最常用叫法）、全部别名、触发方式（在线 / 批量 / 接口 / 手动 / 未知）。
4. 填"证据引用"：`raw/` 下的路径 + 页码/行号/章节；无来源则状态只能为 `INFERRED` 或 `NEEDS_REVIEW`。
5. **更新文件头部的"当前最大 ID"**。
6. 用 [function-template](../../templates/function-template.md) 建知识页，**同一次提交完成**。

## 状态取值

`EVIDENCE_FOUND` · `INFERRED` · `NEEDS_REVIEW` · `SME_CONFIRMED`（需记录确认人与日期）· `CONFLICTED` · `SUPERSEDED`

## 重复与歧义

多个候选都像同一功能时**不要任选**：保留数字小的为规范 ID，其余行标 `SUPERSEDED` 并在备注指向规范 ID，整条标 `NEEDS_REVIEW`，点名需要哪位 SME 判定。
