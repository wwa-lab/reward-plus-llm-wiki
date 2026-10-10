# scripts/ — 维护与校验脚本

只放**真的有用**的轻量脚本。规则：

* **Python 标准库 only**，不引入第三方依赖（本仓库不装依赖）。
* 默认**只读**，不改仓库内容。
* 不访问网络，不读凭证，不写 `raw/`。
* 新增脚本要在本文件登记。

## validate_repo.py

```bash
python3 scripts/validate_repo.py
```

提交前跑。检查项：

1. **结构**：必需的目录与文件是否存在（含每个目录的 README、`raw/_types/` 下各类型的规则文件）。
2. **`raw/` 布局**：`raw/` 下只允许 `README.md`、`_types/`、`_shared/` 和 `PRJ-####[-slug]/`。
   project 目录内只允许已知材料类型子目录 + `_MANIFEST.md`（缺 manifest → WARNING，未知类型 → ERROR）。
   **材料类型目录直接放在 `raw/` 根下 → ERROR**，因为那会丢掉"这批材料属于哪次交付"这个维度。
3. **登记表**：14 张登记表是否齐全、能否解析出"当前最大 ID"、**首列（ID 列）**的前缀是否匹配本表。
   （其余列是关系引用，允许指向其他实体类型，不做前缀检查。）
4. **ID**：知识页文件名是否符合 `<前缀>-####[-slug].md`；front matter 的 `id` 是否与文件名一致；是否已登记在对应登记表里；跨表有无重复 ID。
5. **front matter**：必填字段是否齐全；`status` 是否属于六个合法状态；`confidence` 是否合法；
   `EVIDENCE_FOUND` 是否有 `source_refs`；`SME_CONFIRMED` 是否有 `reviewed_by` / `reviewed_at`。
6. **内部链接**：Markdown 相对链接是否指向存在的文件。
7. **重复**：同一 ID 是否被两个文件占用。

退出码：`0` = 无 ERROR；`1` = 有 ERROR。WARNING 与 INFO 不阻断，但要看一下。

示例输出：

```text
校验目标：/path/to/reward-plus-llm-wiki

INFO (14)
  - knowledge/registry/functions.md: 表内无记录（当前最大 ID = 0）—— 初始状态，正常
  - knowledge/registry/programs.md: 表内无记录（当前最大 ID = 0）—— 初始状态，正常
  ...（其余登记表同理）

结果：通过（0 条警告，14 条提示）
```

## 没有实现的脚本（不装样子）

以下都**没有**实现，也不要宣称有：

* 自动摄取与解析
* 代码扫描 Skill 集成
* 程序/功能关系自动抽取
* 覆盖率与冲突自动报告
* 变更影响分析自动化

这些属于规划能力（见根目录 README 7.6）。等对应的手动流程跑顺了，再考虑是否值得写成脚本。
