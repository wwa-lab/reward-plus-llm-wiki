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
2. **`raw/` 布局**：`raw/` 下只允许 `README.md`、`_types/`、`_shared/` 和 `PRJ-####/`（不带 slug）。
   project 目录内只允许已知材料类型子目录 + `_MANIFEST.md`（缺 manifest → WARNING，未知类型 → ERROR）。
   **材料类型目录直接放在 `raw/` 根下 → ERROR**，因为那会丢掉"这批材料属于哪次交付"这个维度。
3. **登记表**：14 张登记表是否齐全、能否解析出"当前最大 ID"、**首列（ID 列）**的前缀是否匹配本表。
   同一表内 ID 重复 → ERROR，并列出重复位置。
   （其余列是关系引用，允许指向其他实体类型，不做前缀检查。）
4. **ID**：知识页文件名是否符合 `<前缀>-####[-slug].md`（**slug 只允许小写**）；front matter 的 `id` 是否与文件名一致；
   是否已登记在对应登记表里；跨表有无重复 ID；**带 ID 的文件是否放进了登记目录**（放进 `knowledge/architecture/` 这类目录 → ERROR）。
5. **front matter**：必填字段是否齐全；`status` 是否属于六个合法状态；`confidence` 是否合法；
   `EVIDENCE_FOUND` 的 `source_refs` 必须包含至少一个非空路径（缺失或空列表 → ERROR）；
   `SME_CONFIRMED` 是否有 `reviewed_by` / `reviewed_at`。
6. **证据引用**：知识页 `source_refs` 只支持路径字符串列表（行内列表或逐行 `- 路径`）。
   空路径、对象形式（如 `- path: ...`）、嵌套结构、重复声明和其他不支持的格式 → ERROR，避免静默跳过。
   路径可加单/双引号；行内列表中的逗号若属于路径本身，必须加引号。双引号的转义按 JSON 字符串解析。
   这不是通用 YAML 解析器；`docs/` 的来源元数据不属于知识页证据检查范围。
   `source_refs` 里的仓库内路径是否真的存在（不存在 → WARNING）。
   落在 `raw/*/control-files/` 的引用按约定豁免（那些材料默认不提交，见 `.gitignore`），只记 INFO。
7. **关系引用**：front matter 的关系字段（`related_programs` 等）与**登记表非 ID 列**里出现的 ID，
   是否都已在对应登记表里登记（悬空引用 → WARNING）。
8. **登记表 ↔ 知识页**：登记了但没有知识页（→ WARNING，`TERM-` / `SRC-` 这类"行即记录"的前缀除外）；
   知识页 `status` 与登记表 `status` 不一致（→ WARNING，登记表是权威来源）。
9. **`raw/` 孤儿目录**：`raw/PRJ-####/` 没有对应的 `PRJ-` 登记行 → WARNING。
   （反向不检查：材料可以留在 LAN 上，登记行仍然有效。）
10. **内部链接**：Markdown 相对链接是否指向存在的文件。
11. **重复**：同一 ID 是否被两个文件占用。

退出码：`0` = 无 ERROR；`1` = 有 ERROR。WARNING 与 INFO 不阻断，但要看一下。

> **为什么要查证据和关系？** 2026-10-10 的合成数据端到端演练发现：原先只查"markdown 链接"和"ID 是否登记"，
> 于是 `source_refs` 路径写错、`related_programs` 指向不存在的 ID、登记表里出现悬空引用、
> 登记行与知识页状态打架——这些**都会静默通过**。而"证据可追溯"正是本仓库存在的理由，所以第 6-9 项是补上的。
> 同时修掉了 front matter 解析的一个 bug：值里含 ` # `（如 `title: "积分 # 改版"`）会被当成注释截断。

示例输出：

```text
校验目标：/path/to/reward-plus-llm-wiki

INFO (14)
  - knowledge/registry/functions.md: 表内无记录（当前最大 ID = 0）—— 初始状态，正常
  - knowledge/registry/programs.md: 表内无记录（当前最大 ID = 0）—— 初始状态，正常
  ...（其余登记表同理）

结果：通过（0 条警告，14 条提示）
```

## test_validate_repo.py

校验器的回归测试，使用 Python 标准库 `unittest`。只在临时目录生成合成仓库，
不读取业务材料，不修改当前仓库或其中的 `raw/`。

```bash
python3 -B -m unittest discover -s scripts -p 'test_*.py' -v
```

覆盖同表重复 ID、缺失/空证据、不支持的证据格式以及命令行退出码；
同时验证正常列表、带标点的路径、LAN 路径、配置快照豁免和待评审页空列表仍可使用。
这些是校验工具测试，不是 `tests/validation/` 中的 Reward Plus 业务验证规格，不分配 `TEST-` ID。

## 没有实现的脚本（不装样子）

以下都**没有**实现，也不要宣称有：

* 自动摄取与解析
* 代码扫描 Skill 集成
* 程序/功能关系自动抽取
* 覆盖率与冲突自动报告
* 变更影响分析自动化

这些属于规划能力（见根目录 README 7.6）。等对应的手动流程跑顺了，再考虑是否值得写成脚本。
