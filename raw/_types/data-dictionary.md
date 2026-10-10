# 类型：数据字典（完整字段定义）

存放**完整的、机械的**字段级定义导出：文件 / 表 / 字段 / 类型 / 长度 / 小数位 / 键 / 描述。

## 为什么放在 raw/ 而不是 knowledge/

**完整数据字典不进知识层。** 原因：

1. **它是原始输入，不是结论。** 权威源是 DDS / DDL / 系统导出，不是我们转述的 Markdown。
2. **抄进 knowledge/ 必然漂移。** 两边一旦不同步，Agent 不知道该信谁。
3. **量级不可维护。** 一个遗留系统几千到几万字段，Markdown 页面既写不完也更新不动。
4. **对 Agent 是噪音。** 有用的不是"这个字段是 CHAR(10)"，而是"它驱动了什么行为、有什么陷阱"。

因此：**完整定义留在本目录（CSV），知识层只保留精选字段的语义 + 引用。**

## 放什么

* 系统导出的字段定义（例如 `DSPFFD` / `SYSTABLES` / `SYSCOLUMNS` 查询结果）
* 人工维护的数据字典 Excel 导出（若以 CSV 交付）
* 记录级 / 文件级的键与索引定义

## 不放什么

* 生产数据样例（**禁止**）
* 含凭证、连接串、账号的配置
* 字段的业务语义解释（→ `knowledge/data-and-interfaces/`）

## 格式与命名

* **CSV 优先**（表格数据用 CSV 比 Markdown 更方便机器处理，也符合"必要时才用表格格式"的原则）。
* 文件名带版本或日期：`<范围>-data-dictionary-YYYY-MM.csv`。
* 一个批次一个文件；多文件交付时在 `_MANIFEST.md` 写清范围。

## 登记与引用

1. 每批字典在 `knowledge/registry/source-materials.md` 登记一行 `SRC-####`。
2. 知识层的 `DATA-####` 页通过 `dictionary_ref` 字段指向本目录的文件与位置，例如：
   `raw/PRJ-####/data-dictionary/points-data-dictionary-2026-10.csv#PTSMAST`
3. `DATA-####` 页**只写驱动行为的字段**，其余字段以引用代替，不复制。

## 提交前检查

* 是否含生产数据、凭证、个人资料？**含则不得提交**，保持未跟踪并标记待评审。
* 是否有公司数据处理政策要求的审批？
* 是否已在 `knowledge/registry/source-materials.md` 登记？

详见 [../README.md](../README.md) 与仓库根目录 [README.md](../../README.md) 的数据保护说明。
