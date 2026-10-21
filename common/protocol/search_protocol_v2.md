# 检索协议 v2（草案，供审核）

> 配套：《修改计划.md》WP0；执行日期预期：2026-10 中旬
> 状态：**已确认（2026-10-07 团队评审，决策记录见第 12 节）**

---

## 1. 变更摘要（v1 → v2）

| 项目 | v1（2025-12-20 执行） | v2（本次修订） |
|---|---|---|
| 时间窗 | 2014-01 – 2025-12 | 2014-01 – **2026-09-30** |
| 检索串 | ("Docker" OR "Dockerfile" OR "DockerHub" OR "docker-compose" OR "dockerized") | ("**Docker\***" OR "docker-compose" OR "docker compose")；无通配符库用显式枚举超集（见 §3） |
| 检索字段 | 未在论文中记录（R1-3a 指出） | title / abstract / keywords，逐库记录实际设置 |
| 验证 | 23 篇验证集 100% 召回 | 对 v2 检索串重放，确认仍 100% 召回 |
| 扩展检索 | Google Scholar 前 200 | Google Scholar **前 500** + 饱和曲线（R2-M1） |
| 滚雪球 | backward 0 / forward +1 | forward 对扩充后全量集合重跑；backward 对**新增论文**执行（老 56 篇不重跑，理由见 §7） |
| 敏感性 | 无 | 泛 container 词族扫描（§8，回应 R2-m5/R3-W1） |
| 语料版本 | 56 篇（Zotero「1最终文献-56」） | 语料 v2（Zotero「搜索结果-2026.09.30 → 1最终文献-v2」） |

**关键设计：v2 检索串是 v1 的严格超集。** `Docker*` 前缀匹配覆盖 Docker / Dockerfile / DockerHub / dockerized / dockerization；`docker compose`（分写）补 V2 官方拼写。因此 v1 的全部筛选结论在新协议下依然有效，只需处理"重跑产生的增量"。**增量大小本身就是 v1 词表充分性的实证**——若全窗口重跑的 delta 很小（预期如此，因为 token 检索下 "Docker Compose" 本就含 "Docker" 词条），即可在回复信中作为词表边界合理的证据。

## 2. 时间窗与口径

- 窗口：2014-01-01 – **2026-09-30**（完整月份）；实际检索执行日不早于 2026-10-05，两个日期都写入论文 III.C 与复现包。
- 起点理由不变：Docker 首个稳定版 1.0（2014-06）。
- **年份口径**：沿用 v1 抽取口径（venue 正式出版年）。ESE/TOSEM 等 "online 2025、issue 2026" 的论文按已抽取版本去重，同一工作不重复计入。
- 论文表述联动：摘要/引言 "2014 to 2025"→"2014 to 2026"；结论 "snapshot up to December 2025"→新日期；Fig 3(e) 增加 2026 柱并注明为不完整年份（9 个月）。

## 3. 逐库执行规格

| 库 | 检索入口 | 字段（记录实际所用） | 检索式模板 | 通配符 | 导出 |
|---|---|---|---|---|---|
| ACM DL | Advanced Search | Title / Abstract（+Keywords，以界面为准） | ("Docker*" OR "docker-compose" OR "docker compose") | 支持 * | BibTeX 或 RIS，分批导出 |
| IEEE Xplore | Advanced Search | v1 为 Title+Abstract；v2 实际执行为 **Title/Abstract/Keywords**（原决策为 All Metadata，执行时由作者按 T/A/K 完成——T/A/K 仍是 v1 的严格超集，超集逻辑不变） | 同上 | 支持 * | RIS/CSV，分批 |
| ScienceDirect | Advanced Search | "Title, abstract, keywords" | ("Docker" OR "Dockerfile" OR "Docker Hub" OR "DockerHub" OR "docker-compose" OR "docker compose" OR "dockerized") —— 显式枚举 | **不支持** | RIS，分批 |
| SpringerLink | Advanced Search | title/abstract（以界面为准） | ("Docker*" OR "docker-compose" OR "docker compose") | 支持 * | RIS/BibTeX，分批 |
| WILEY | Advanced Search | Title / Abstract / Keywords | 同上 | 支持 *（执行时确认） | RIS/BibTeX，分批 |
| Google Scholar | 标准检索 | 无字段控制 | ("Docker" OR "Dockerfile" OR "DockerHub" OR "docker-compose" OR "dockerized") —— 沿用 v1 串，取**相关性排序前 500** | — | 逐条浏览记录 |

执行纪律：每库检索后**当场**填写检索日志（§4），并截图保存检索设置（进复现包）；年份过滤 2014–2026 在库内完成；结果导出后统一导入 Zotero 对应子分类。

**字段决策（2026-10-07 执行后更正）**：v1 五库均为 Title+Abstract；v2 实际执行字段——ACM=Title/Abstract（分跑取并集）、SpringerLink=Title、ScienceDirect=Title/abstract/keywords、WILEY=Title/Abstract、IEEE=Title/Abstract/Keywords。IEEE 原决策为 All Metadata、实际按 T/A/K 执行（T/A/K ⊇ v1 的 T+A，超集逻辑不变）。各库字段与检索式逐库记录于复现包 search_log.csv；字段语义的逐库对照写入论文 III.C（正面回应 R1-3a/R2-M1）。

## 4. 检索日志表（复现包必备）

| 列 | 说明 |
|---|---|
| library | 库名 |
| query_exact | 逐字符记录实际提交的检索式 |
| fields_used | 实际字段设置 |
| filters | 年份、学科过滤等 |
| run_date | 执行日期 |
| hits | 命中总数 |
| export_format / export_count | 导出格式 / 实际导出条数 |
| operator / notes | 执行人 / 备注（界面截图文件名） |

## 5. 去重与增量筛选

1. **v2 全窗口重跑**（2014–2026），而非只搜 2026：老候选与 Zotero 既有库存（ACM 1014 / IEEE 1788 / SD 441 / Springer 258 / WILEY 147 = 3,648 条）按 **DOI 优先、无 DOI 用 normalized title+year** 匹配去重。
2. 去重后的**增量 = 2026 新文献 + 老窗口新词命中**（后者预期极少）；增量候选进入「筛选结果（未去重）」。
3. 双人独立筛选，采用**修订版标准：8 页门槛改为 5 页下限**（≥5 页，仅排除海报/演示/扩展摘要等非存档格式；R3-W2 expand 选项，团队 2026-10-08 定稿）；Kappa 校准流程沿用。
4. 筛选决定写入 Zotero 标签：**沿用 🔴（排除）二值标记**，并为每条排除记录一个主导原因标签（`ex-①`…`ex-⑦`，对应论文方法节标准编号），使本轮起逐条原因可自动统计。
5. ⚠ 迁移时核对：Zotero IEEE 子分类 1,788 条 vs 论文漏斗 1,790 条，差 2 条（可能与 Fig 3(e) 的 2 条幽灵期刊论文同源）。

### 5.1 v1 标注体系现状（2026-10-07 已查明）

| 库 | 条目 | 🔴 排除 | 未标记 |
|---|---|---|---|
| ACM（标注完毕） | 1,014 | 977 | 37 |
| IEEE（标注完毕） | 1,788 | 1,723 | 65 |
| ScienceDirect（标注完毕） | 441 | 436 | 5 |
| Springer（标注完毕） | 258 | 244 | 14 |
| WILEY | 147 | **0（未标注）** | 147 |
| 合计 | 3,648 | 3,380 | 268 |

- `🔴` 为**二值排除标记，不带原因编号**（排除原因对应论文方法节的排除标准①–⑦）；另有 `⛅️短文`（83 条，可佐证排除标准①）、`预印本`（4 条）等辅助标签。
- **与论文漏斗的账目差异（WP2.1 必须逐项审计）**：
  ① IEEE 1,788 vs 论文 1,790；
  ② 🔴 合计 3,380 vs 漏斗总排除 3,587（初筛 637 + 详筛 2,950）；
  ③ 未标记存留 268 vs 漏斗口径（进入详筛 3,013 / 详筛后入选 63）；
  ④ Zotero 工作流 77→69→66→56 vs 漏斗 63→55→56（注：「1最终文献集-66」中有 10 条带 🔴，66−10=56 吻合，说明 🔴 曾随筛选推进更新）。
- **逐条排除计数重建方案**：
  (a) 对详筛阶段被排除集合（~2,950 篇）做"主导排除标准"重标注（题目/摘要快判，双人独立 + 分歧仲裁 + 10% 抽样复核一致性；预计 2–3 人日）；
  (b) 页数标准已修订为 5 页下限（2026-10-08）：被原 8 页标准排除的条目按"≥5 页"重新判定（⛅️短文 54 作品已逐条核验，纳入 20 条）；
  (c) WILEY 未标注：用其 55 篇「标记完毕」子集回溯核对，缺口部分补标；
  (d) 重建方法在论文 III.C 与复现包中如实写明（post-hoc reconstructed exclusion counts），不得表述为"检索当时已逐条记录"。

**工具就绪（2026-10-07）**：底表已生成 `zotero_export/v1_relabel_worksheet.csv`（3,648 条；预填分布：ex-① 1,762 / ex-⑤ 64 / ex-⑥ 40 / ex-④ 18 / 留空 1,764；代码簿同目录 codebook.txt）。增量去重：各库重检索结果导出 RIS/BibTeX 后运行 `zotero_tools/dedup_match.py`（DOI > 规范化标题 > 模糊≥0.93 三级匹配，自动拆分"已存在/新候选"）。

## 6. 扩展检索与饱和曲线

- Google Scholar 沿用 v1 检索串（避免泛词），按相关性排序人工浏览**前 500** 条，v2 时间窗。
- 饱和曲线记录：每浏览 50 条记录一次"累计新入选数"；预期曲线在 200 附近已长期为 0，以此回应 R2-M1 的 "0.3%" 质疑。
- 结果放入「GoogleScholar扩展检索-Top500」子分类。

## 7. 滚雪球 v2

- **Forward**：对扩充后的最终集（56 + 新增）在 GS 上重跑 "cited by"，v2 窗口；预期可捕获 2026 年新引用。
- **Backward**：仅对**新增论文**核对参考文献（老 56 篇 v1 已全量核对、结果 0，且参考文献集合未变，正文说明即可）。
- 两者的筛选同 §5 口径，产出写入「筛选结果（去重后）」。

## 8. 敏感性扫描（泛 container 词族，不进语料）

- 查询：("containerization" OR "container image*" OR "container registry" OR "Podman" OR "LXC" OR "containerd" OR "Open Container Initiative")，同 5 库、同字段、2014–2026。
- 流程：统计候选量级 → 双人快筛题目/摘要（仅判 SE 相关性 + 是否 Docker 工件研究）→ 报告三类数字：总量、SE 相关量、其中"非 Docker 容器化 SE 研究"量 + 代表作 3–5 篇。
- 写入 Threats：范围边界的实证依据；若发现集中的非 Docker 研究方向，明确列为 scope limitation（属于 [32][33] 泛容器综述范围）。
- 结果放入「敏感性扫描-泛container词族」子分类。

**定位（已确认，回答团队提问）**：敏感性扫描**仅作为敏感性分析，不作为论文主结果**——不新增 RQ、不新增主表；呈现位置为 III.C 一句话说明设计 + V.B Threats 一段结果 + 完整数字进复现包与回复信。判断依据：扫描服务于"范围合理性"的论证（R2-m5 / R3-W1），其数字改变的是 threats 讨论的置信度，不影响 RQ1–RQ3 的任何统计。唯一例外触发条件：若发现 ≥20 篇方向集中的"非 Docker 容器化 SE 研究"，则升级为 scope limitation 专门讨论（预期不会发生）。

## 9. Zotero 组织（新建分类树）

结构（已准备一键创建脚本 `zotero_tools/zotero_v2_collections.js`）：

```
Docker_review/
└── 搜索结果-2026.09.30/                 ← v2 根分类
    ├── ACM搜索结果            ← 1014 篇（v1 迁入）
    ├── IEEE搜索结果           ← 1788 篇（v1 迁入，⚠核对 1790 差异）
    ├── ScienceDirect搜索结果  ←  441 篇（v1 迁入）
    ├── SpringerLink搜索结果   ←  258 篇（v1 迁入）
    ├── WILEY搜索结果          ←  147 篇（v1 迁入）
    ├── GoogleScholar扩展检索-Top500   （空，待 WP0.3）
    ├── 敏感性扫描-泛container词族     （空，待 WP0.8）
    ├── 筛选结果（未去重）     ←   77 篇（v1 迁入，后续追加）
    ├── 筛选结果（去重后）     ←   69 篇（v1 迁入，后续追加）
    └── 1最终文献-v2           ←   56 篇（v1 迁入，冻结时 = v2 全量）
```

- 迁移是"条目加入新分类"，不复制不移动条目，v1 分类原样保留（审计痕迹）。
- WILEY 的 55 篇「标记完毕」子分类不迁移（已确认为已标注子集，留作 §5.1(c) 回溯核对材料）；Scopus 不启用（已确认）。
- 执行步骤：Zotero → 工具 → 开发者 → Run JavaScript → 勾选 "Run as async function" → 粘贴 `zotero_v2_collections.js` 全文 → Run（约 1–3 分钟，输出迁移报告）。
- 执行后运行 `python zotero_tools/zotero_export.py refresh && python zotero_tools/zotero_export.py tree --root Docker_review` 验证。

## 10. 新论文抽取与工件核查

- 新入选论文按 Table I schema 抽取（含 Table IV/V 的工件可用性核查，口径与 v1 一致：链接可达性 + 是否含所声称工件）。
- 抽取结果合入抽取表 v2；P 编号沿用字母序规则（新增论文将改变 P 编号，**所有 [Px] 引用由脚本统一重排**，禁止手改）。

## 11. 验证与冻结判据

- [ ] 23 篇验证集对 v2 检索串 100% 召回
- [ ] 逐库检索日志齐全（含截图），GS 前 500 饱和曲线数据完整
- [ ] 增量筛选双人有 Kappa/一致率记录，逐条排除计数可产出
- [ ] 全部图表与正文统计由脚本重算（数字台账），人工抽查 10 处
- [ ] 「1最终文献-v2」定版并在复现包中打 tag（语料 v2 冻结），之后 WP5 编码才开工

## 12. 决策记录（2026-10-07 团队确认）

| # | 事项 | 决定 |
|---|---|---|
| 1 | 终点日期 | **2026-09-30**；重检索执行日 ≥2026-10 上旬，两个日期写入论文 |
| 2 | 检索字段 | v1 实际为 **Title+Abstract**；v2 实际执行字段：ACM=Title/Abstract（并集）、SpringerLink=Title、ScienceDirect/WILEY=Title+Abstract（±keywords）、IEEE=**Title/Abstract/Keywords**（原决策 All Metadata，执行时更正；仍为 v1 超集）；逐库明细见 §3 与 search_log.csv |
| 3 | WILEY 子分类 | 55 篇「标记完毕」= 已标注子集；v2 只迁 147 篇主集合 ✓（脚本已按此实现），55 篇子集留作 §5.1(c) 回溯核对材料 |
| 4 | v1 标注体系 | 🔴 = 排除标记（二值，无原因编号）；排除原因以论文方法节标准①–⑦为准，按 §5.1 方案重建逐条计数 |
| 5 | Scopus | 不启用 |
| 6 | 敏感性词表 | §8 词表维持不变；扫描仅作敏感性分析，不作主结果（见 §8 定位说明） |
| 7 | 分类命名 | 按 §9 执行 |
