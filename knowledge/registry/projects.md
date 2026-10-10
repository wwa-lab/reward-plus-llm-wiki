# 登记表：项目 / 变更批次（PRJ）

**当前最大 ID：0**（尚未分配任何 ID）

规范见 [registry/README.md](README.md) 与 [../../CONTRIBUTING.md](../../CONTRIBUTING.md)。

**项目（PRJ）= 遗留系统的一次交付**：某年为了某个 feature，改动了若干功能。
它同时是三个东西：

* **迁移的工作单元**（迁移按 project 走，不是按 function 走）
* **材料的组织单元**（`raw/PRJ-####-<slug>/`）
* **功能的变更历史**（feature 逐年叠在 function 上）

> **`PRJ-` 是遗留事实，`MT-` 是目标态任务。** 前者说"这个 feature 什么时候、以什么范围加进去的"；
> 后者说"怎么把它迁过去"。两者多对多，前者在 `knowledge/`，后者在 `requirements/`。

| ID | 规范名 | 别名 | 年度 | 变更性质 | 涉及功能 | 仍在使用 | 状态 | 证据引用 |
|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — | — |

（暂无记录。上表首行仅为占位，正式登记时替换。）

**「变更性质」填 新增 / 修改 / 废弃；「仍在使用」填 是 / 否 / 未知 —— 这一列决定迁移时能不能砍。**
**「涉及功能」填 `FUNC-####`（可多个）。材料位置记在 `source-materials.md`，不堆在本表。**

## 如何追加一行

1. 检索"规范名"与"别名"，确认尚未登记。**同一个 project 被叫成多个名字 → 记别名，不新建 ID。**
2. 新 ID = 当前最大 ID + 1，例如 `PRJ-0001`。
3. 年度：交付年份。变更性质：新增 / 修改 / 废弃。
4. 涉及功能：填 `FUNC-####`。**不清楚就留空并标 `NEEDS_REVIEW`，不要猜。**
5. **「仍在使用」不要凭感觉填。** 有证据（业务确认、无调用、无菜单入口）才填"否"。
6. **更新文件头部的"当前最大 ID"**。
7. 用 [project-template](../../templates/project-template.md) 在 `knowledge/projects/` 建知识页，
   并在 `raw/` 下建同名目录放材料（**同一次提交完成**）。

## 与 raw/ 目录、LAN folder 的对应

| 项 | 说明 |
|---|---|
| 材料目录 | `raw/PRJ-####-<slug>/`，与本表 ID 一一对应 |
| 跨 project 材料 | `raw/_shared/`，**不占 PRJ-** |
| LAN 上的位置 | 记在 `source-materials.md` 的对应 `SRC-####` 行里 |
| 材料没进库 | 仍然建 `PRJ-` 行；`SRC-` 里写 LAN 路径并标"待评审" |

## 状态取值

`EVIDENCE_FOUND` · `INFERRED` · `NEEDS_REVIEW` · `SME_CONFIRMED`（需记录确认人与日期）· `CONFLICTED` · `SUPERSEDED`

## 注意

* **一个 project 会碰多个 function，一个 function 会被多个 project 碰。** 这是多对多，不要试图一对一。
* **不要按"年份 + 名字"当 ID。** 名字会变、会重名。PRJ- 是稳定 ID，名字进"规范名/别名"列。
* **老 project 的"仍在使用"是迁移里最值钱的判断。** 常年没人用、代码还在的 feature，是遗留系统的典型包袱。
* 登记表只管 ID 与关系；**业务意图、变更范围、迁移影响写在知识页里**。
