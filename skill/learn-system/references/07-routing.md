# 与既有 skill 的分工（完整版）

本 skill 只做「跨多轮 + 要知道学到哪」。其余场景建议切换，**不承诺自动调用**。

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
