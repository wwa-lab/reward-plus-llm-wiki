# knowledge/domain/concepts/ — 领域概念

需要展开说明的领域概念，一个概念一页，ID 前缀 `CONCEPT-####`。

一行能说清的词**不要**建页，登记到 [registry/terms.md](../../registry/terms.md) 即可。
只有当概念有**边界、口径、生命周期或易混淆点**需要讲清楚时才建页。
ID 登记在 [registry/concepts.md](../../registry/concepts.md)，**先登记再建页，同一次提交完成**。

## 放什么

* 业务概念的定义、范围与边界
* 关键口径（例如某个指标怎么算、按什么时间口径）
* 生命周期与状态流转
* 与 `DATA-` / `RULE-` / `FUNC-` / `IF-` 的对应关系

## 不放什么

* 一句话就能说清的术语（→ `registry/terms.md`）
* 物理字段与类型（→ `data-and-interfaces/`）
* 业务规则的条件与后果（→ `business-rules/`）

## 关系维护

* 概念页列出相关的 `TERM-####`、`DATA-####`、`RULE-####`、`FUNC-####`。
* 术语表的"相关实体"列可以指向 `CONCEPT-####`。
* 双向维护：规则页 / 实体页也说明自己属于哪个领域概念。

## 命名

```text
CONCEPT-0001-<概念slug>.md
```

（以上仅为命名**格式**示例，不是真实记录。）
