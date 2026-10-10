# 登记表：领域概念（CONCEPT）

**当前最大 ID：0**（尚未分配任何 ID）

规范见 [registry/README.md](README.md) 与 [../../CONTRIBUTING.md](../../CONTRIBUTING.md)。

领域概念 = 需要**展开说明**的业务概念（有边界、口径、生命周期或易混淆点）。
一句话能说清的词**不要**登记在这里，去 [terms.md](terms.md) 登记 `TERM-####`。

| ID | 规范名 | 别名 | 领域域 | 相关术语 | 相关实体 | 状态 | 证据引用 |
|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — |

（暂无记录。上表首行仅为占位，正式登记时替换。）

**「相关术语」填 `TERM-####`，「相关实体」填 `DATA-####` / `RULE-####` / `FUNC-####` / `IF-####`。**

## 如何追加一行

1. 先查 [terms.md](terms.md)：**一行能说清就登记术语，不建概念页。**
2. 检索"规范名"与"别名"，确认尚未登记。
3. 新 ID = 当前最大 ID + 1，例如 `CONCEPT-0001`。
4. 领域域：例如 积分 / 账户 / 交易 / 客户 / 结算 / 未知。
5. 证据引用：业务文档位置，或 SME 确认记录。
6. **更新文件头部的"当前最大 ID"**。
7. 用 [concept-template](../../templates/concept-template.md) 在 `knowledge/domain/concepts/` 建知识页，
   **同一次提交完成**。

## 状态取值

`EVIDENCE_FOUND` · `INFERRED` · `NEEDS_REVIEW` · `SME_CONFIRMED`（需记录确认人与日期）· `CONFLICTED` · `SUPERSEDED`

## 注意

* **概念说"是什么"，规则说"什么条件下怎样"。** 不要把条件与后果写进概念页（→ `RULE-####`）。
* 概念页必须列出对应的代码事实（`DATA-` / `RULE-` / `FUNC-`），否则 Agent 用不上。
* 同一个词在不同来源含义不同 → 标 `CONFLICTED` 并写明谁能裁决，**不要合并成一个概念**。
