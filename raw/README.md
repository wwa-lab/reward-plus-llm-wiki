# raw/ — 原始输入与批准的扫描输出

`raw/` 是档案层。放进来的是什么样，就一直是什么样。

## 组织方式：先按 project，再按类型

**一级目录按 project（`PRJ-####`）分，project 内按材料类型分。**

理由：材料在现实中就是按项目存在 LAN folder 里的，而**迁移也是按 project 走的**。按 project 归档，
一个迁移批次要用到的材料就在一处。

```text
raw/
├── README.md
├── _types/                     # 各类型材料的「规则说明」，不是材料本身
│   ├── README.md
│   ├── code-scan-results.md
│   ├── business-documents.md
│   ├── fe-menus.md
│   ├── test-cases.md
│   ├── test-results.md
│   ├── diagrams-and-images.md
│   ├── data-dictionary.md
│   └── control-files.md
├── _shared/                    # 跨 project 的材料（全量扫描、通用业务文档等）
│   ├── README.md
│   └── <类型>/                  # 实际用到时才建
└── PRJ-0001-<project-slug>/     # 一个 project 一批材料
    ├── _MANIFEST.md             # 这批材料是什么、谁给的、范围、LAN 来源
    ├── code-scan-results/       # 只建用到的类型子目录，不预建空的
    ├── business-documents/
    └── ...
```

**只建用到的类型子目录。** 一个 project 只有扫描输出，就只有一个 `code-scan-results/`。

## 材料在 LAN 上，仓库里放什么

原始材料**大部分留在 LAN folder**（那是权威位置）。本仓库只放**获批准进库的那部分**，
其余只在登记表里记录"在哪、是什么"。

| 情况 | 做法 |
|---|---|
| 材料可进库 | 复制到 `raw/PRJ-####/<类型>/`，登记 `SRC-####` |
| 材料不可进库（含源码、凭证、生产数据） | **不复制**。登记 `SRC-####`，在备注里写 LAN 路径，标"待评审" |
| 材料跨多个 project | 放 `raw/_shared/<类型>/` |
| 只想登记、不想进库 | 登记 `SRC-####` + LAN 路径即可，`raw/` 里不建目录 |

**登记表 [knowledge/registry/source-materials.md](../knowledge/registry/source-materials.md) 是材料位置的权威索引**，
记 `SRC-####` ↔ LAN 路径 ↔ 所属 `PRJ-####`。材料没进库时，这份登记就是唯一的线索。

## 与其他目录的关系

| 目录 | 关系 |
|---|---|
| `raw/` | 输入（只读） |
| `analysis/` | 基于 `raw/` 的中间分析，**可随意重写** |
| `knowledge/` | 基于 `raw/` 的已评审结论，**引用 `raw/` 而不复制它** |

知识页永远引用 `raw/` 的文件，不把内容抄过去。抄一份就多一处要维护、多一处会过时。

## 六条硬规则

1. **保留原始输入。** 原样存放，不为了"更好读"而改动。
2. **不静默修改原始材料。** 不改内容、不转编码、不重新排版、不改名。需要可读副本 → 放 `analysis/`。
3. **记录来源信息。** 提供方、日期、版本、适用范围、导出方式，知道多少记多少（写在 `_MANIFEST.md` 里）。
4. **先查数据处理政策，再放内部材料。** 不确定就不要放。
5. **不得提交**密钥、凭证、令牌、连接串、未经批准的源码、生產数据、個人资料。
6. **知识页引用回 `raw/`。** 每条结论都要能指回这里的一个具体位置。

## 材料类型

类型**决定材料的规则**（可读性、敏感性、引用格式），规则说明在 `_types/`：

| 类型 | 规则说明 |
|---|---|
| 代码扫描输出 | [`_types/code-scan-results.md`](_types/code-scan-results.md) |
| 前端菜单与导航材料 | [`_types/fe-menus.md`](_types/fe-menus.md) |
| 业务文档 | [`_types/business-documents.md`](_types/business-documents.md) |
| 原始测试用例 | [`_types/test-cases.md`](_types/test-cases.md) |
| 测试执行结果 | [`_types/test-results.md`](_types/test-results.md) |
| 图表与图像 | [`_types/diagrams-and-images.md`](_types/diagrams-and-images.md) |
| 数据字典（完整字段定义） | [`_types/data-dictionary.md`](_types/data-dictionary.md) |
| 配置快照 | [`_types/control-files.md`](_types/control-files.md) |

## 命名

稳定、可描述、保留原扩展名：

```text
program-inventory-2026-09.csv
points-data-dictionary-2026-10.csv
points-params-prod-2026-10-01.csv
call-graph-2026-09.json
points-spec-v3-2026-09.pdf
menu-export-2026-08.xlsx
run-2026-09-30.log
redemption-flow.png
```

**来了新版本 → 另存新文件**（例如 `program-inventory-2026-10.csv`），不要覆盖旧的。知识页里的行号只对被引用的那一个版本有效。

## Manifest

**每个 project 目录一份 `_MANIFEST.md`**，说明这批材料是什么。模板见 [templates/manifest-template.md](../templates/manifest-template.md)，复制到 `raw/PRJ-####/_MANIFEST.md` 后填写。

`_MANIFEST.md` 是 `raw/` 里唯一允许在初次交付之后新建的文件类型。

## 引用格式

```text
raw/PRJ-0001/code-scan-results/program-inventory-2026-09.csv，行 142
raw/_shared/business-documents/points-glossary-v2.pdf，第 7 页
```

## 读不了的文件

不要改它。不要编内容凑数。到 `analysis/reports/` 里记录：尝试了什么、失败原因、需要什么工具或授权。

## 敏感内容

发现材料含源码片段、凭证、個人资料或生產数据 → **不要提交**，保持未跟踪，标记"待评审"，在结论出来前不引用它。`.gitignore` 不是安全控制，不要指望它挡住已经 `git add` 的文件。

`control-files/` 类型在 `.gitignore` 里**默认忽略**（配置快照可能含生产值）。要提交已评审、已脱敏的快照，用 `git add -f <路径>`，并在 commit message 里写明评审人与脱敏范围。注意：被忽略的文件**不会**出现在 `git status` 里，所以"没看到"不等于"没进来"。
