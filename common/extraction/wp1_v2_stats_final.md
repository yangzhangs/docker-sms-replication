# WP1 阶段二：v2 数字台账终版（92 篇，数据源 extraction_master_94.csv + wp1_v2_ledger.csv）

## 0. 语料构成（PRISMA）
- 总样本：92 篇 = v1 保留 55 + 增量检索 14 + 短文重筛 20 + 滚雪球 3
- 注：v1 56 篇中 P43 因期刊扩展版替换会议版被剔除（ex-③），v1 实计 55 篇；新增 2026 在线发表 11 篇。

## 1. 出版商 (Publisher)
- IEEE: 49 (53.3%)
- ACM: 23 (25.0%)
- Springer: 15 (16.3%)
- Elsevier: 2 (2.2%)
- Wiley: 1 (1.1%)
- IEICE: 1 (1.1%)
- MDPI: 1 (1.1%)

## 2. 作者类型 (Author type)
- Academia: 84 (91.3%)
- Both: 7 (7.6%)
- Industry: 1 (1.1%)

## 3. 场馆类型 (Venue type)
- Conference: 68 (73.9%)
- Journal: 24 (26.1%)

## 4. 国家 (首作者单位, 共 18 国)
- China: 29
- United States: 19
- Italy: 9
- Canada: 7
- Japan: 6
- Belgium: 3
- Germany: 3
- Australia: 3
- India: 3
- Portugal: 2
- France: 1
- Netherlands: 1
- Morocco: 1
- Saudi Arabia: 1
- Thailand: 1
- Switzerland: 1
- South Korea: 1
- United Kingdom: 1
- 前四国合计：64 (69.6%)

## 5. 年份 × 场馆类型
- 2017: 3 （会 3 / 刊 0）
- 2018: 6 （会 5 / 刊 1）
- 2019: 8 （会 6 / 刊 2）
- 2020: 12 （会 10 / 刊 2）
- 2021: 9 （会 5 / 刊 4）
- 2022: 8 （会 6 / 刊 2）
- 2023: 8 （会 5 / 刊 3）
- 2024: 9 （会 7 / 刊 2）
- 2025: 17 （会 13 / 刊 4）
- 2026: 12 （会 8 / 刊 4）

## 6. 场馆 Top-15
- ESE: 7
- MSR: 7
- ICSME: 5
- FSE: 5
- ICSE: 5
- SANER: 5
- IEEE Access: 4
- COMPSAC: 4
- SCAM: 3
- TSE: 3
- TOSEM: 2
- ASE: 2
- SPE: 1
- IEICE Trans. Inf. Syst.: 1
- ICSSP: 1
- Top-12 合计：52 (56.5%)

## 7. CORE 等级
- A*: 39 (42.4%)
- A: 17 (18.5%)
- not-ranked: 17 (18.5%)
- B: 15 (16.3%)
- C: 4 (4.3%)


## 8. 图 3 全套重绘（数字驱动，2026-10-07）
- 生成脚本：`zotero_tools/make_v2_figs.py`（PyMuPDF 矢量直绘；本机 Python 3.14.0a1 与 numpy ABI 不兼容、matplotlib 不可用）
- 输出：`overleaf_repo/plot/{plots0..plots6, temporal_heatmap, overview_unified}.pdf` —— 与 review.tex 引用路径一致，直接重编译即生效
- 内容对应：
  - plots0：首作者国家条形图（前四国 + Others，配色对齐 v1）
  - plots1：出版商（7 类）；plots2：作者类型（91.3% / 7.6% / 1.1%）
  - plots3：≥2 篇的场馆 12 个（v1 恰为 10 个；v2 共 12 个 ≥2 场馆，合计 52 篇 = 56.5%）
  - plots4：场馆类型（会 73.9% / 刊 26.1%）；plots5：年份×场馆类型堆叠（2017-2026）
  - plots6：CORE（A* 39 / A 17 / B 15 / C 4 / not-ranked 17）
- 预览图：`figs_work/preview/*.png`（170dpi）；自检已完成（对齐/裁剪/颜色逐像素核验通过）

## 9. 数据勘误记录与团队复核清单
1. **I3F27YWX 附件 PDF 张冠李戴**：条目本身是 ICSE 2020 "Learning from, Understanding, and Supporting DevOps Artifacts for Docker"（Henkel/Bird/Lahiri/Reps, UW-Madison+MSR），但 Zotero 附件实为 JCST'19 SemiTagRec 论文 PDF。台账已按正确论文修正（国家→United States、作者类型→Both）。**待团队：重新下载正确 PDF（DOI 10.1145/3377811.3380406）替换附件。**
2. W63WUQ47 国家修正为 Switzerland（University of Basel；原 Canada 系误）。
3. CORE 全部按 CORE2023 重核（共 19 处修正）：SCAM=C（升级B申请未通过）、ECSA=A、ICSSP=A、IC2E=B、SoSyM=B、JCST=B、IEICE Trans.=C、IEEE Access=B、ICSOC=A、ICPADS=B；ICIC/ICT4SD/ICEBE(2020起移出名录)/JCC/Internetware/SOSE 不在名录 → not-ranked。**已在论文结果段注明会议用 CORE2023、期刊用 CORE2020，并在 Threats 说明期刊列表停更带来的限制（R1-4 闭环）。**
4. PACMSE 三篇按 Crossref issue 还原会议：EUH9SFDQ=ISSTA'25、S9TNQ9LV=FSE'25、2YMKPNNB=FSE'26（venue_type 均为 conference）。
5. 年份补全：ZQIAID39=EASE'25(2025)、EHVN7V6N=ICSE'26(2026)；venue 80 字符截断串已修复（SANER/ICSE 等 7 处）。
6. **多国合作比例**：v2 未报具体比例（需全作者国家编码）；论文使用定性表述“minority of studies”，不给出未经验证的数字。
7. Table III 的 Specification 列已按 CSV 重新核对（53 篇，0 处不匹配）；旧 v1 的 31-vs-30 记录不再适用。
8. **review.tex 已同步**：正文、Table III–IX、摘要、结论和回复信均以本台账及最终 artifact 口径为准（2026-10-21 复核）。


## 10. 最终 artifact 口径（2026-10-21）

- **Datasets：24**（26.1% of 92）：公开共享的数据集合，包括 Docker artifact 语料以及两项 v1 原始记录（Shipwright 构建记录、Docker Build Faults 问题/帖子记录）；v2 新增仅计公开、可复用的 Docker-artifact 数据集（Dockerfiles、images、Compose 等），问卷、讨论帖、构建记录、开发者测试等评估数据不计入新增 dataset。
  - GitHub 20、Docker 8、hybrid 4；23 个提供访问链接，1 个无链接、3 个 broken/empty。
  - 数据集 P 列表见 `artifact_tables/table_v_datasets.csv`。
- **Tools：38 个工具，来自 36 篇研究**（39.1%）：30 primary、8 supporting。
  - 仅计论文实际实现的 tool；纯 framework/approach 不计入。
  - 工具 P 列表见 `artifact_tables/table_vi_tools.csv`。
- **Taxonomies：10**（10.9%）：见 `artifact_tables/table_vii_taxonomies.csv`。
- Table IV 的最终贡献矩阵见 `contribution_matrix_92.csv`；Table VIII 的 7 类/25 子类见 `artifact_tables/table_viii_categories.csv`。
- 贡献类型 Kappa（0.969）来自原始双人编码；最终 artifact-type 口径（公开共享 dataset / implemented tool，含两项 v1 原始记录）是在一致性计算之后完成的归一化，二者用途不同。
