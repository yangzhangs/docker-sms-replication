# Inclusion/Exclusion Criteria 审查（结合审稿意见，供团队判断）

> 依据：论文 III.C 现行标准（v1，2025-12-20 检索时点）× R1/R2/R3 意见 × v2 增量筛选（731 条待筛）适用性
> 状态：**待团队逐条拍板**（决策清单见第六节）

---

## 一、现行标准（论文 III.C 原文，v1）

**Inclusion Criteria**
- ① The study is written in English.
- ② The study belongs to the "Computer Science" subject area (only for Springer Link, ScienceDirect, and Wiley Online Library).
- ③ The study is published between 2014 and 2025.
- ④ The study is published in a journal or in a conference (or symposium) proceeding.
- ⑤ The study has accessible full text.
- ⑥ The study is published in a recognized SE venue, or its context is SE activities, artifacts, or processes.

**Exclusion Criteria**
- ① The study has less than 8 pages.
- ② The study does not have its full text available online.
- ③ The old version of the paper that has been extended from conference to journal.
- ④ The study that is a review, survey, or short paper.
- ⑤ The study uses Docker only for implementation, comparative analyses, or infrastructure-centric operations without explicit SE implications.
- ⑥ The study focuses not on SE but about other contexts.
- ⑦ The study replicates work in previous publications.

**两阶段执行**：初筛（题目/摘要，仅书目信息）应用 Inclusion ①–④ → 3,013 篇；详筛（页数/题目/摘要，不足时读全文）应用 Inclusion ⑤–⑥ + Exclusion ①–⑦ → 63 篇。

---

## 二、逐条审查：标准 ↔ 审稿意见 ↔ 处理建议

### Inclusion ①（英文）— 无审稿意见涉及
**结论：维持原文。**

### Inclusion ②（CS 学科，仅 Springer/SD/Wiley）— 关联 R3-W1（范围）、R2-m5（检索边界）
**现状与 v2 实况：**
- Springer：v2 已通过 `facet-discipline="Computer Science"` 执行 ✓（与 v1 同法）
- **SD / WILEY：v2 未加学科过滤**——SD 高级检索无学科面（Elsevier 检索以 CS 期刊为主，天然集中）；WILEY 结果页有学科过滤但未使用
- GS 扩展检索通道本条无对应（GS 无学科限定），由 Inclusion ⑥ 把关

**⚠ 决策点 1**：二选一——
- **A（推荐）**：接受 SD/WILEY 的偏差，在协议中如实写明"SD/WILEY 的 Docker 词族 T/A/K 检索天然集中于 CS 文献，未再叠加学科过滤；噪声由 Inclusion ⑥ 把关"，并在 v1↔v2 对照中说明（**v1 当时是否真的在 SD/Wiley 加了学科过滤，建议你回忆确认**——若 v1 也没加，则此条 v1↔v2 完全一致，无偏差）；
- B：对 SD/WILEY 增量结果页补加学科过滤重导（工程量：两库结果页人工过滤+重抓，约半天，且有漏抓风险）。

### Inclusion ③（2014–2025）— **必须修订**（R2/AE 时效性质疑的直接落点）
**v2 修订措辞（建议）：**
> The study is published between **1 January 2014 and 30 September 2026** (the revision search window).

**配套执行规则（写入协议，筛选时执行）：**
1. 年粒度过滤的库（ACM/SD/Springer：2025–2026）会放进**终点之后**的条目 → WP0 已用 Crossref 精确日期剔除 14 条（2026-10~12 出版）；剩余 42 条仅知 2026 年、无月份的 `date-verify` 条目 → **决策点 2**：筛前统一复核（推荐，一次性 15 分钟）vs 筛中逐条处理。
2. 起点**之前**的晚索引文献（2025 年内出版但 2025-12-20 时未被索引、故不在 v1 库中的）：**保留**（它们是 v1 的漏检，属增量应有之义）——建议在协议里明确这一条，避免审稿人问"为什么有 2025 年初的论文出现在增量里"。
3. IEEE 天粒度窗口 / WILEY 月粒度窗口的边界元数据交错（5 条与 v1 重叠）已由去重消解，无需规则。

### Inclusion ④（期刊或会议论文集）— 关联 R3-W2（短文价值）
**结论：维持，但补一句显式说明**（v2 增量中 IEEE 有 BOOK 14 / CHAP 5 / STD 2，直接据此排除）：
> Standards documents, books and book chapters, theses, preprints, and web resources do not satisfy this criterion.

### Inclusion ⑤（可获取全文）与 Exclusion ②（无在线全文）——**同义反复**
**建议**：保留两处原文以保证与 v1 漏斗可比（不删条款），但在修订版中加注：
> (Exclusion ② operationalizes Inclusion ⑤ at the full-text screening stage.)

### Inclusion ⑥（recognized SE venue 或 SE context）— **R2-M1 点名的判断依赖性核心**
R2 原文只点了 Exclusion ⑤，但 ⑤⑥⑥ 是同一族"含义模糊、最能移动最终计数"的标准。**必须操作化**（见第五节决策树）。修订措辞（建议）：
> The study is published in a recognized SE venue (**CORE-ranked SE conferences/journals or established SE journals**), or its context concerns **SE activities, artifacts, or processes (e.g., source code, builds, configurations, developer practices and tooling)**.

### Exclusion ①（<8 页）— **R3-W2 的直接靶子 → 已决策：采纳方案 B（纳入短文）**

**2026-10-07 团队决策：采纳 R3-W2 的 "expand" 选项——移除页数门槛，纳入强相关短文。**

**新规则（替代原 Exclusion ①）：**
> The study is a poster, demo, extended abstract, or other **non-archival short-format contribution**, **or the study is shorter than 5 pages**.

即：**删除 8 页门槛，改设 5 页下限（2026-10-08 团队定稿）**；海报/演示/扩展摘要等非存档格式排除；≥5 页的会议正式 short paper（data paper、short track 等）**纳入**。

**连带执行（B 的成本所在）：**
1. **v1 排除集复筛**：v1 当年被页数标准排除的 ~1,762 条（工作底表 suggest_code=ex-①）+ 83 条 ⛅️短文标记，需按其余标准重新筛选 → 新增底表 `zotero_export/v1_shortpaper_rescreen.csv`（已生成），双人 ~1.5–2 人日；
2. Exclusion ④ 同步修订：**"short paper" 从排除项移除**，改为只排除 review/survey（及上面的非存档格式）；
3. 漏斗与全部统计按新规则重算（v2 语料本就要重建，时机正好）；
4. 论文披露：原检索应用了 8 页门槛，修订中移除并复筛——这正面落实 R3-W2 的 "expand" 选项；
5. 预期收益：回应 AE"11 年只有 56 篇太少"的观感——短文层预计新增入选 20–50 篇。

### Exclusion ③（会议→期刊扩展版的旧版本）
**结论：维持，措辞微调以明确处理规则**（v1 正文已有"保留最完整版本"的实践）：
> When a conference paper has been extended into a journal article, only the most complete version is retained; the earlier version is excluded.

### Exclusion ④（综述/短文）
**结论：维持。建议澄清**："short paper" = 会议显式设置的 short/demo/poster 格式（通常 ≤4 页），与 Exclusion ① 的机械页数线互补；综述类含 survey/SLR/mapping study。

### Exclusion ⑤（仅实现/对比/基础设施、无 SE 含义）— **R2-M1 点名："highly judgment-dependent"**
这是 R2 的关键质疑点：该标准最能移动最终计数，却没有操作定义。**必须给出决策规则 + 示例判断集**（见第五节）。修订措辞（建议）：
> The study uses Docker merely as an implementation vehicle, a subject of performance comparison (e.g., container vs. VM), or an infrastructure-centric operation (e.g., scheduling, networking, resource management), **without contributing SE knowledge, methods, or tools concerning Docker artifacts or practices**.

### Exclusion ⑥（非 SE 主题）
**结论：维持。与 ⑤ 的分工写清**：⑤ = 以 Docker 为中心但**缺少 SE 研究问题**；⑥ = 有研究问题但**属于其他领域**（生物信息学用 Docker 打包、网络能耗测量等）。示例见第五节。

### Exclusion ⑦（重复发表）— **R1-3b 明确要求澄清**
R1 问：是否只排除"纯复制"（replication+其他贡献的保留）？
**修订措辞（建议）：**
> The study replicates work in previous publications **without adding new research contributions** (pure replications); replication studies that extend prior work with new artifacts, analyses, or findings are retained.

---

## 三、v2 需要新增的条款/规则

| # | 新规则 | 依据 | 状态 |
|---|---|---|---|
| N1 | 多库重复：跨库命中合并为单一候选，标注全部来源 | 漏斗一致性 | ✅ 已执行（1 条） |
| N2 | GS 扩展检索通道：凡通过 ①–⑦ 的合格研究**一律纳入**，无论排名深浅 | 饱和度论证的诚实性 | 待确认（决策点 6） |
| N3 | `date-verify` 42 条：导入时带标签，筛前逐条核对出版月份 | 窗口刚性 | 决策点 2 |
| N4 | 起点规则：晚索引的 v1 漏检（2025 年内出版但检索时未被索引）保留 | 增量语义完整 | 建议采纳 |
| N5 | 双人独立筛选 + Kappa（与 v1 同法）+ 主导原因标签（🔴 体系沿用） | R2-M2 | ✅ 已在协议 |

---

## 四、建议的修订版措辞（英文草稿，可直接进论文 III.C）

> **Inclusion criteria.** We consider the following inclusion criteria: (1) the study is written in English; (2) the study belongs to the "Computer Science" subject area (applied to Springer Link, ScienceDirect, and Wiley Online Library, where such filtering is supported); (3) the study is published between **1 January 2014 and 30 September 2026**; (4) the study is published in a journal or a conference (or symposium) proceeding — standards documents, books and book chapters, theses, preprints, and web resources do not satisfy this criterion; (5) the study has accessible full text; and (6) the study is published in a recognized SE venue (CORE-ranked SE conferences and journals), or its context concerns SE activities, artifacts, or processes (e.g., source code, builds, configurations, and developer practices and tooling).
>
> **Exclusion criteria.** We exclude a study if: (1) it is a poster, demo, extended abstract, or other non-archival short-format contribution (typically ≤2–3 pages) without full technical content; (2) it does not have its full text available online (operationalizing Inclusion 5); (3) it is the earlier version of a study extended from a conference to a journal (the most complete version is retained); (4) it is a review or survey (including SLRs and mapping studies); (5) it uses Docker merely as an implementation vehicle, as a subject of pure performance comparison (e.g., container vs. VM), or for infrastructure-centric operations (e.g., scheduling, networking, resource management), without contributing SE knowledge, methods, or tools concerning Docker artifacts or practices; (6) it focuses on a domain other than software engineering; or (7) it replicates previous publications without adding new research contributions. **Note:** in the initial search (December 2025) we additionally excluded studies shorter than 8 pages; during the revision this threshold was replaced by a 5-page floor, and all previously excluded records were re-screened under the revised criteria (Section IV-A reports the re-screening outcome).
>
> Criteria are applied in two stages as before: Stage 1 (bibliographic, Inclusion 1–4) on titles and abstracts of all retrieved records; Stage 2 (Inclusion 5–6 and Exclusion 1–7) on page count, titles, and abstracts, consulting full text when insufficient. Two authors independently apply all criteria to all records; disagreements are resolved by discussion, and the dominant exclusion reason of every excluded record is recorded to support the per-criterion funnel (Section IV-A).

---

## 五、筛选操作手册要点（回应 R2-M1"判断依赖性"）

**决策树（Stage 2，逐题三问）：**

```
Q1. 是否以 Docker 工件/实践为研究对象？
    ├─ 否 → Q3
    └─ 是 → Q2. 是否产出 SE 知识/方法/工具？
              ├─ 是（smell/构建/演化/质量/开发者研究/SE 工具）→ 纳入
              └─ 否（仅部署载体/纯性能对比/基础设施运维）→ ex-⑤
Q3. 是否有 SE 之外领域的研究问题？
    ├─ 是（生物信息、网络能耗、教育环境搭建等）→ ex-⑥
    └─ 否 → 检查机械标准（页数/类型/重复/全文）→ ex-①②③④⑦
```

**边界示例判断集**（写进 codebook，编码员人手一份）：

| 例子 | 判定 | 理由 |
|---|---|---|
| LLM 自动生成 Dockerfile 的质量研究 | 纳入 | Docker 工件 + SE 方法贡献 |
| SoftwareX 论文"我们用 Docker 打包了 XX 工具" | ex-⑤ | Docker 仅为实现载体 |
| 容器 vs 虚拟机性能对比（无 SE 教训） | ex-⑤ | 纯对比分析 |
| 边缘计算平台的 Docker 部署优化 | ex-⑤/⑥ | 基础设施运维 |
| Docker Hub 镜像漏洞传播实证 | 纳入 | SE 安全 + Docker 工件 |
| 用 Docker 配置生物信息学流水线 | ex-⑥ | 其他领域 |
| 4 页 MSR 短文提出 Docker 构建失败分类 | ex-①（进敏感性清单） | 页数标准，R3-W2 关注点 |
| 2026 年 10 月出版的 IEEE 会议论文 | 排除（窗口外） | 已在 WP0 核验剔除 |

---

## 六、待你拍板的决策清单

| # | 决策 | 选项 | 建议 |
|---|---|---|---|
| 1 | SD/WILEY 未加 CS 学科过滤 | A. 接受并记录；B. 补过滤重导 | **A**（先确认 v1 当时是否加过；T/A/K Docker 查询天然 CS 集中） |
| 2 | 42 条 date-verify 处理 | A. 筛前统一复核；B. 筛中逐条 | **A**（15 分钟一次做完，筛选时无悬念） |
| 3 | 8 页敏感性清单 | 规模与位置 | **10 篇左右，正文一句话 + 清单进复现包** |
| 4 | Exclusion ⑤ 操作化文本 + 示例集 | 认可/修改 | 推荐文本与示例集如上，请过目 |
| 5 | Exclusion ⑦ 澄清（纯复制才排除） | 认可/修改 | 推荐措辞如上，请过目 |
| 6 | GS 命中合格即纳入（N2） | 确认 | 确认即可（预计 0–3 条） |
| 7 | Inclusion ⑥ "recognized SE venue" 的锚定 | CORE 列表 / 自定清单 | 建议 CORE SE 段 + ESE/TOSEM/TSE 等，写进 protocol |
