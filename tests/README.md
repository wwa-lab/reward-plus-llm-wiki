# tests/ — 验证规格

本目录包含两类用途：下述 `validation/` 是 Reward Plus 业务验证规格；
[agent-evals/](agent-evals/README.md) 是 Agent 产物核验的合成演练，不分配业务 `TEST-` ID。
合成演练记录留在 `analysis/reports/`，不能作为遗留系统测试通过或 SME 确认的证据。

> 说明：`tests/` 不在初始结构清单里，是为"测试知识页"保留的小扩展。
> 原始材料在 `raw/`，**派生出来的可复用规格**放 `tests/validation/`。

## 三处分工

| 内容 | 位置 | 说明 |
|---|---|---|
| 原始测试定义 | `raw/PRJ-####/test-cases/` | 业务/QA 给的用例，原样保存 |
| 执行结果 | `raw/PRJ-####/test-results/` | 日志、输出、对比报告，原样保存 |
| 规范化验证规格 | `tests/validation/` | 本仓库维护的 `TEST-####` 页面，引用前两者 |

知识页**引用** `raw/`，不复制内容。

## 放什么

`TEST-####-<slug>.md`，从 [templates/test-case-template.md](../templates/test-case-template.md) 复制：

* 业务场景、前置条件、输入（合成数据）、步骤、预期结果
* 关联的 `FUNC-` / `PROG-` / `RULE-`
* 执行记录（引用 `raw/PRJ-####/test-results/`）
* 遗留 / 新系统对比
* 已知限制

## 规则

1. **规格尽量技术中立**，同一份用例才能在遗留系统和 Java 新系统上各跑一遍。可比性是它最大的价值。
2. **没有 `raw/PRJ-####/test-results/` 引用就不能写"通过"。** 未执行就写"未执行"。
3. **禁止真实卡号、真实客户信息**——合成或掩码数据。
4. **失败是发现，不是要修的红灯。** 失败可能推翻已确认知识：报告它，不要改期望值让它变绿。
5. ID 从 `knowledge/registry/test-cases.md` 分配。

## 生命周期

```text
FUNC-#### / RULE-####  →  TEST-####（规格）  →  执行  →  raw/PRJ-####/test-results/……  →  TEST-####（结果）
```

Phase 4 时在两侧环境跑同一批 `TEST-####`，把对比结果记回用例页——那就是迁移的安全网。

## 现在该做什么

业务验证等到 `knowledge/` 里至少有一个功能规格或一条规则值得验证时再开始。
没有业务验证对象就先不写 `TEST-` 用例；Agent 合成演练可独立运行。
