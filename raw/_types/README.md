# raw/_types/ — 材料类型的规则说明

**这里放的是"规则"，不是"材料"。**

每种材料类型的处理规则写成一个文件。项目目录（`raw/PRJ-####/<类型>/`）和
`raw/_shared/<类型>/` 里的材料都遵守对应类型的规则。

## 为什么规则和材料分开

材料一级按 project 分（迁移视角），规则按类型写（合规视角）。两者分开，规则只写一遍，
新增 project 时不用重复复制规则。

## 类型清单

| 类型 | 规则文件 | 典型材料 |
|---|---|---|
| 代码扫描输出 | [code-scan-results.md](code-scan-results.md) | 程序清单、调用关系、数据访问摘要、规则抽取结果 |
| 前端菜单与导航材料 | [fe-menus.md](fe-menus.md) | 菜单导出、导航树、界面清单 |
| 业务文档 | [business-documents.md](business-documents.md) | PPT / PDF / Excel / Word / Visio 导出 |
| 原始测试用例 | [test-cases.md](test-cases.md) | 用例集、测试脚本、验收标准 |
| 测试执行结果 | [test-results.md](test-results.md) | 执行日志、对比报告、截图 |
| 图表与图像 | [diagrams-and-images.md](diagrams-and-images.md) | 架构图、流程图、界面截图 |
| 数据字典（完整字段定义） | [data-dictionary.md](data-dictionary.md) | 字段定义导出（CSV） |
| 配置快照 | [control-files.md](control-files.md) | 各环境的配置实际值 |

**要加一个新类型**：在这里加一行，建对应规则文件，并在 `raw/README.md` 的类型表里登记。
不要让材料"没有类型"——没有类型的材料无法施加合规规则。
