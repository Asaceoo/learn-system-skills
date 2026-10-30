# learn-system · 体系学习控制器

把「学完一个领域」做成可追踪的工程：**前置依赖大纲 + 单点课 + 概念级掌握度 + 复习队列**，四件套同时在线，走到 M05 才算闭环。

## 安装

已落地在 `~/.workbuddy/skills/learn-system/`。重启会话后生效（或直接用 `/learn-system`）。

## 快速开始

```
我想系统学 <领域>
```

依次发生：

1. 问你三件事（为什么学 / 什么算成功 / 每周几小时）
2. 建 `study/<topic>/`，只建 5 个文件；找 3 条主源写进 `syllabus.yaml` 的来源区
3. 出大纲（推荐 5-12 模块，每条前置都带「缺了它会卡在 ___」），等你确认
4. 每轮只出一课 `lessons/0001-*.html`，出完停下
5. 每课结束刷新 `mastery.md` 顶部三行 + `review.md`
6. 下次说「继续」出下一课，说「复习」走到期队列

## 四个命令词

| 说 | 做什么 |
|---|---|
| 系统学 X / 入门 X | 开课（A） |
| 继续 / 下一课 | 出一课（B） |
| 复习 / 该复习什么 | 到期队列（C），进入时先报「今天到期 N 条」 |
| 考考我 / 我学到哪了 | 掌握度测评（D） |

## 文件地图

```
learn-system/
├── SKILL.md                      # 入口：铁律 18 条、状态模型、主流程、路由表
├── references/
│   ├── 01-system-design.md       # 教材目录做覆盖基准、差集、前置 DAG + 依据、M01 复审
│   ├── 02-teaching.md            # 流畅度 vs 存储强度、ZPD、难度分配、五视角
│   ├── 03-assessment.md          # 零提示出题、难度配比、薄弱点复练
│   ├── 04-mastery.md             # 掌握档 L1-L5、证据表（含判定方）、前置门槛
│   ├── 05-review.md              # 复习档 0-5、到期队列、日期命令、异常处理
│   └── 06-sources.md             # 来源 6 级优先、教材锚定、深度调研协议、覆盖度验收
├── templates/
│   ├── syllabus.template.yaml    # 含 resources 来源区，替代独立 resources.md
│   ├── mission.template.md
│   ├── mastery.template.md       # 含顶部三行恢复入口 + 待建文件区块
│   ├── review.template.md
│   ├── mistakes.template.md      # 按需创建
│   ├── learning-record.template.md  # 按需创建
│   ├── lesson.template.html      # 自包含可打印；小节来源锚点 + 断言三级 + 易过期区 + 30 秒可查证三条
│   └── reference.template.html
└── README.md
```

## 一个领域只有 5 个起步文件

```
study/<topic>/
├── MISSION.md
├── syllabus.yaml       # 来源写在末尾 resources 区
├── mastery.md          # 顶部三行 = 唯一恢复入口
├── review.md
└── lessons/NNNN-*.html
```

`reference/` 第 2-3 课起按需；`mistakes.md` 同一概念累计 2 次错才建；`learning-records/` 只在目标或大纲变更时建。

## 知识正确性怎么保证

不承诺正确，承诺三件事：**限制错误类型、让错误可被发现、让代价大的错误少发生**。

| 关 | 时机 | 硬规则 |
|---|---|---|
| 来源关 | 写课前 | 先定知识基准（稳定学科用教材目录 + 课标，快变领域用官方文档，强监管领域用现行标准）；主源不足 3 条可开链接不得出课 |
| 断言关 | 写课中 | 每句事实性陈述分三级：事实（带小节级来源锚点）/ 建议 / 推断（带可推翻条件）；单源必须标「单源」 |
| 覆盖关 | 出课后 | 教材目录与大纲做差集，教材有而没讲的写进 `not_covered`；每个 `concepts` 必须出现在某课 |
| 抽查关 | 交付时 | 课末固定「30 秒内你能自己查证的三条」，任一条对不上，本课按失效处理 |

另外：会过期的内容（标准编号、版本、API、价格）统一进课末「易过期」区，半年后一次性复查。

完整规则见 `references/06-sources.md`。

## 融合来源

| 来源 | 拿的是哪一块 |
|---|---|
| `mattpocock/skills` → teach（307K★） | 分层工作区、流畅度 vs 存储强度、ZPD 靠记录算、不信任参数记忆、HTML 课形态、选择题反作弊 |
| `bevibing/tutor-skills`（1.4K★） | 概念级状态表、四色档位、薄弱点禁止重问、零提示出题、难度配比 |
| `read2017/learn-anything-with-AI`（203★） | 掌握度五档、证据类型组合、来源三级优先、事实与建议分离 |
| `adamaiken89/learn-something` | `syllabus.yaml` 模块 DAG + 前置校验、累积测验、间隔调度思路 |
| `Li-Evan/Bloom`（294★） | 一次只产出一课的硬约束、五个学习视角 |
| `dontbesilent2025/dbskill` → dbs-learning（11K★） | 目录优先级与泛目录黑名单、文件命名硬约束 |
| `GarethManning/education-agent-skills`（930★） | learning progression / spaced practice / retrieval practice 的方法论口径 |
| 本机 `html-generator`、`visual-knowledge-tutor`、`knowledge-handbook-builder`、`teachany` | 建议切换对象，不承诺自动调用 |

## 与既有 skill 的边界

- 只讲一个概念要可视化 → `visual-knowledge-tutor` / `visual-learning-partner`
- 要一份完整领域手册 → `knowledge-handbook-builder`
- 要交互课件 / 知识图谱 → `teachany`
- 给了源文件说「做成课程」 → `course-generator`
- 只要连续课程、不要掌握度 → `teach` / `matt-teach`

跨 skill 委派不可靠（依赖名字触发经常静默失败），所以本 skill 自带纯文字兜底，并在降级表里写明。

## 设计取舍

| 决定 | 理由 | 代价 |
|---|---|---|
| 不实现 FSRS，用 6 档离散间隔 | FSRS 需精确数学，模型易算错；离散档可手算可核对 | 长期调度精度不如真 FSRS |
| 一次只出一课 | 批量生成会让掌握度表全空，等于没学 | 慢，用户可能不耐烦 |
| 掌握档卡 L3 作前置门槛 | 低于 L3 进下个模块，后面全塌 | 会卡住，需补前置 |
| 只留标准 / 备考两模式 | 「快学」与「走到 M05」的判据互斥，会诱发跳步 | 想快速过一遍时没有对应模式 |
| 起步只建 5 个文件 | 9 个文件第 3 天就开始跳过一半 | 需要按需生长，前期结构不完整 |
| 日期必须用命令取 | 手算已实测 6 条错 2 条 | 每写一个到期日多一次命令调用 |
| 跨 skill 委派只做建议 | 声明式调用经常静默失败 | 需要用户手动切，或接受文字兜底 |
| 停更 6 周即归档 | 没有死亡条件就会变成第 14 个吃灰 skill | 可能过早放弃 |
| 用教材目录做覆盖基准 | 教材是领域覆盖面的事实标准，比自己列清单可靠 | 教材滞后于前沿；快变领域改用官方文档目录 |
| 课末放「30 秒可查证三条」 | 让用户能低成本判断这一课可不可信，比模型自我声明更有效 | 每课多写三条，且必须真的可查 |

## 已知局限

- 掌握度仍依赖用户诚实；已用「单一证据封顶 L2」「自评写不出具体描述按 L2 封顶」压制，但不能消除
- HTML 课单文件不联网，交互止于选择题与折叠答案；要动画请切 `visual-knowledge-tutor`
- 复习队列是文本表，无推送；只能用「进入时先报到期数」补偿
- DAG 由模型生成，仍需用户确认；已用 `why_prereq` 让用户可审计
- 成功判据是「一个领域走到 M05」，尚未有真人走完一轮的实测
