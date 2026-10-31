# 与既有 skill 的分工（完整版）

本 skill 只做「跨多轮 + 要知道学到哪」。其余场景建议切换，**不承诺自动调用**。

## 两档处理：切走 vs 借力（别混）

| | 切走 | 借力 |
|---|---|---|
| 什么情况 | 用户其实想要**别的东西**（单概念讲透、整域手册、交互大屏） | 用户仍在推进**这门课**，只是需要一份**附加材料** |
| 本 skill 怎么办 | 退出，交给对方主导；切不成就用文字兜底做完并告知 | **继续主导**，只借一个能力产出附加文件，回收进 `reference/` 并登记 |
| 状态归属 | 不接管对方状态，也不让对方接管自己的 | 掌握度/复习队列**只由本 skill 写** |
| 详细规则 | 本文件下表 | `references/10-composition.md`（产物矩阵 8 类 + 四条铁律 + 接口契约） |

判据一句话：**「这门课还继续吗？」** 继续 → 借力；不继续 → 切走。

> 为什么不承诺：按名字点名另一个 skill，并不保证它会被加载（跨 skill 委派会静默失败）。所以每条都配了「切不成的兜底」——切不成时本 skill 自己用文字做完，并明确告知用户未切换成功。

## 分工表

| 用户其实想要 | 建议切到 | 切不成的兜底 |
|---|---|---|
| 讲透一个概念，要图 / 动画 | `visual-knowledge-tutor` | 用 ASCII 图 + 文字讲透，并告知「动画版需切到前者」 |
| 一整套领域 HTML 手册 | `knowledge-handbook-builder` | 用 `reference/` 出一份速查件替代 |
| 交互课件 / 可视化大屏 | `teachany` | 不接活，明确告知这是另一条产线。**注意区分**：本 skill 流程 A 第 4 步出的是**依赖图谱**（概念的前置/相关），是自己产出的，不外包 |
| 已有文件转课程 | `course-generator` | 先转成文字大纲，再回到本 skill 建 DAG |
| 只要连续课程、不要掌握度 | `teach` / `matt-teach` | 允许，但本 skill 不接管其状态 |

判断顺序：**有没有「跨多轮 + 要知道学到哪」的需求**。有 → 本 skill。

## 与 teach 的物理隔离

teach 的产物在当前目录（`./lessons/` + `MISSION.md`），本 skill 在 `study/<topic>/`。两套目录不允许混用。

检测到疑似 teach 进度时（见 SKILL.md「接管已有进度」），只问一句，不展开解释。

## 本机已有的其他学习类 skill（不重复造）

`general-knowledge-tutor`、`github-project-tutor`、`concept-anim-explainer`、`knowledge-animation`、`whiteboard-explainer`、`explainer-animation` 等属于「讲解 / 可视化」产线，与「跨多轮推进」不冲突，需要时按上表建议切换即可。
