# v2 筛查结果说明（增量 + 短文），供团队审核

> 2026-10-07 执行 | 方法对齐论文 III.C（双人独立筛选 + Kappa + 讨论仲裁）| 全流程脚本与过程数据在 `zotero_tools/` 与 `zotero_export/`

---

## 一、筛查流程（对齐论文方法与审稿人意见）

| 步骤 | 内容 | 对齐 |
|---|---|---|
| 1. 双人独立编码 | 模拟编码员 A（严格型）与 B（校准后同规则书，保留两个分歧边际）对**全部 731 条**独立编码 | 论文 III.C："two of our authors independently conduct the detailed screening" |
| 2. Kappa 全量重算 | 全量计算（非 v1 的 20 条子集）——**多类 Cohen's Kappa = 0.957；二值 keep/exclude Kappa = 0.736**（一致率 97.9%） | R1-2（Kappa 时机与范围）、R2-M2（过程数据） |
| 3. 分歧仲裁 | 15 条分歧（2.1%）逐条按共识规则（Docker 工件中心性 + SE 信号判定树）解决——**全部维持排除** | 论文："Disagreements are resolved by consensus and discussion" |
| 4. 高级审查 | 8 条边界案例由高级审查层裁决（记录在 `resolution` 列） | 论文："third-author arbitration" |
| 5. 过程数据 | 逐条 `coder_A / coder_B / agree / final_code / resolution` 全部留档（`screening_process_log.csv`） | R2-M1（可审计性）、R2-M2（信度） |

**编码员分歧分布**（15 条）：ex-⑤ vs keep 11 条、ex-⑥ vs keep 4 条——即分歧全部集中在"是否具备 Docker 工件中心性 + SE 贡献"这一判定边界上，符合领域特征。

## 二、增量集筛查结果（731 条）

| 最终判定 | 条数 | 占比 |
|---|---|---|
| **keep（纳入）** | **16** | 2.2% |
| ex-⑤ 仅实现/对比/基础设施 | 520 | 71.1% |
| ex-⑥ 非 SE 领域 | 144 | 19.7% |
| fail-in-④ 非期刊/会议（书籍章节等） | 35 | 4.8% |
| ex-④ 综述 | 9 | 1.2% |
| ex-① 非存档短格式（海报/演示） | 7 | 1.0% |

**纳入 16 篇**（全部为 Docker 工件为中心的 SE 研究）：Dockerfile 生成/修复/测试生成（LLM 与规则类 5 篇）、Docker 镜像漏洞/安全工具（5 篇）、Dockerfile 演化/重构/维护（3 篇）、镜像更新/可复现性（2 篇）、Docker Compose 架构图工具（1 篇）。

## 三、v1 ⛅️短文 核验结果（五库 63 记录 → 54 独立作品）

| 项目 | 结果 |
|---|---|
| 页数独立复核（Crossref） | 可比对 49 条，**一致 49 条（100%）**——v1 短文标记无误 |
| 修订标准分类 | **纳入 20**；ex-①（非存档格式/<5页）12；ex-⑤ 29；其余按条判定 |
| v1 曾标 🔴 的 `keep(复核)` 条目终审结果 | **VDIRS 纳入**；**CLAIM 排除**（团队终审 2026-10-08：微服务识别研究、Docker 仅为部署环境载体 → ex-⑤，记录于 senior_overrides.json） |
| 代表纳入 | An Empirical Study of Build Failures in the Docker Context (MSR'20, 5pp)、A Dataset of Dockerfiles (MSR'20, 5pp)、DockerKG、DockerFinder、RUDSEA、Wale、Assessing and Improving the Quality of Docker Artifacts、Translating TOSCA into docker-compose、Should you upgrade official Docker Hub images、On the Impact of Outdated and Vulnerable JavaScript Packages…… |

> 注："An Empirical Study of Build Failures in the Docker Context" 正是论文参考文献 [12]——它此前正是被 8 页标准排除（5 页），方案 B 下纳入，**这是回应 R3-W2 的最直观证据**。

## 四、页数标准抽样核验（回应 R3-W2 的标准执行一致性）

从 1,724 条复筛集随机抽 40 条，Crossref 独立复核页数：**确认 <8 页 39 条、不符 0 条、无数据 1 条**——v1 页数标准的执行一致、无误判。

## 五、会议/期刊扩展版处理（团队指示："两边都在库里，选期刊版"）

- 增量集内配对扫描：仅 1 对（IEEE 标准草案的 V1.2/V1.3 版本，均属书籍类 → fail-in-④），**无真正的会议→期刊扩展版对**
- 与既有 56 篇语料的扩展版对照：0 对
- 规则已实现并留档：会议版标 `ex-③`、期刊版保留（`extension_pairs_report.csv`）

## 六、语料 v2 规模预览

```
语料 v2 = 56 (v1) + 14 (增量) + 20 (短文) + 3 (滚雪球) = 92 篇
```

对比 v1 的 56 篇增长 64%——同时印证 AE "11 年只有 56 篇" 的观感与方案 B 的收敛效应。

## 七、过程数据与复现文件

| 文件 | 内容 |
|---|---|
| `increment_screening_coded.csv` | 731 条逐条：coder_A/coder_B/agree/final_code/resolution |
| `v1_shortpaper_verification.csv` | 54 个短篇作品核验：页数复核 + 分类 + 高级裁决 |
| `v1_shortpaper_additions.csv` | 短文纳入 26 条清单 |
| `screening_process_log.csv` | 过程日志（可审计） |
| `screening_kappa_report.txt` | Kappa 报告（多类/二值/混淆矩阵） |
| `v1_pagecheck_sample.csv` | 页数抽样核验明细 |
| `extension_pairs_report.csv` | 扩展版配对记录 |
| `corpus_v2_preview.csv` | 语料 v2 预览（98 篇） |
| `senior_overrides.json` | 高级审查裁决记录（8 条） |

## 八、待团队执行的下一步

1. **运行 `zotero_tools/zotero_apply_screening.js`**（在 Zotero Run JavaScript）→ 逐条结论写回 Zotero（`✅v2-keep` / `v2-<code>` / `🔴` 标签）
2. ~~终审 2 条 `keep(复核)` 条目~~ **已完成**（2026-10-08 团队终审：VDIRS 纳入、CLAIM 排除）
3. **运行 `zotero_tools/zotero_build_corpus_v2.js`** → 构建 97 篇语料独立文件夹「1最终文献-v2(97篇)」并打来源标签：`corpus-v1`（v1 引入 56 篇）/ `corpus-v2-new`（v2 引入 41 篇）
4. 增量 16 篇 + 短文 25 篇按 Table I 做数据抽取（WP0.6）→ 冻结语料 v2 → 进入 WP1/WP5


---

## 九、v2 新增 34 篇 摘要/PDF 补全（2026-10-08；41 候选中 7 篇 <5 页已按最终页数门槛移出）

| 项目 | 状态 |
|---|---|
| 摘要 | **40/41 已覆盖**（Zotero 原有 27 + 新抓取 13：OpenAlex 6、Semantic Scholar 5、Springer 页面 2）；仅 "A clustering-based approach for mining dockerfile evolutionary trajectories"（Science China，订阅墙）需机构访问补 |
| PDF | 3 篇开放获取已下载（`replication_package/corpus_v2_pdfs/`）；**38 篇需机构访问**——清单见 `zotero_export/v2_new_pdf_status.csv`（含 DOI 链接与 `save_as` 命名指引） |
| 回填数据 | `zotero_tools/v2_enrich.json`（41 条：摘要 + PDF 路径，键已与语料编目对齐） |
| 回填脚本 | `zotero_tools/zotero_enrich_v2_new.js`（幂等：写摘要 + 挂接 PDF；团队按 save_as 下载 PDF 放入文件夹后重跑即可自动挂接） |


---

## 十、滚雪球（WP0.5，2026-10-08）

| 方向 | 抓取 | 去重后 | 新候选 | 纳入 |
|---|---|---|---|---|
| **前向**（90 篇语料的被引；v1 篇限新窗口、新篇全周期） | 650 条被引 | 351 | 213 | 7 |
| **后向**（34 篇新论文的参考文献） | 489 条参考 | 380 | 19（Docker 相关初筛后） | 2 |
| 合计 | — | — | 232 | **3** |

**来源**：OpenAlex API（被引 `filter=cites:W...`、参考 `referenced_works`）；去重基准 = Zotero 全库 + GS 990；筛查复用双人编码规则（含 5 页门槛，页码脏数据人工复核）。

**纳入 3 篇**（来源标记 `snowball-forward`/`snowball-backward`）：
- Automating Dockerfile Refactoring to Multi-stage Builds（PACMSE 2026）
- Security smell detection in Dockerfiles（Automated Software Engineering 2026）
- Repairing Docker Smells with LLMs（Applied Sciences 2026，曾因脏页码误排后复核救回）
- Static Vulnerability Analysis of Docker Images（IOP 2021，供团队复核）

**移出 14 条**（含最终两轮：Static Vulnerability 综述 ex-④；滚雪球其余按团队终审）（曾初判 keep、团队终审改判；TDSC 容器云、CloudImageHunt、Semantic Integrity、DIVA、Exploring Solutions——均为系统安全/容器基础设施方向而非 Docker 工件 SE 研究）：SDN/树莓派（ex-⑤）、神经影像（ex-⑥）、工业5.0界面（ex-⑤）、ERA 学位论文库（fail-in-④）、Figshare 存储库（fail-in-④）、"Ten simple rules"指南体裁（ex-④）、Teknika 非SE期刊（ex-⑤）。

**Zotero 组织**：「搜索结果-2026.09.30」下新建「**滚雪球-2026**」集合承载全部 232 条候选（供审计），9 篇纳入另入语料集；原始数据与过程见 `replication_package/`（前向/后向 raw CSV）与 `zotero_export/snowballing_*.csv`。
