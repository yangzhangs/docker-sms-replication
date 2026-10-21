# 抽取与编码手册（WP0.6，v1.0 定稿）

> 适用：新增 38 篇（增量 14 + 短文 20 + 滚雪球 4）的全文抽取；v1 56 篇的确定性字段已从论文表重建，RQ3 原文摘录按本手册同口径补录。
> 双人模拟协议与本手册配套：编码员 A（严格，需原文证据）/ B（包容，合理推断可标 weak）→ 仲裁 → 高级审查；过程数据逐条留档。

---

## 一、字段定义与规则

### 1. 元数据（确定性，脚本已填）
- source / pid_v1 / zotero_key / title / year / venue_type / venue_name

### 2. SE concern（RQ1，多标签，6 类）——**须有全文写明的证据**
| 标签 | 判定要点 |
|---|---|
| Performance | 关注构件的性能/资源效率（体积、构建时长、启动、开销） |
| Maintainability | 关注可维护性（气味、重构、技术债、配置质量、演化维护成本） |
| Reliability | 关注可靠/容错（构建失败、flakiness、故障修复、可恢复性） |
| Security | 关注安全（漏洞、供应链、投毒、许可合规、信息泄漏——限 **Docker 工件层面**） |
| Evolution | 关注随时间演化（版本更新、变更模式、技术滞后、纵向分析） |
| Adoption | 关注采纳/使用（为什么用、怎么用、开发者实践、生态调查） |

规则：**primary-claim 证据**（研究问题/摘要/结论中作为核心主张出现）方可标；仅背景提及不标。

### 3. Docker object（RQ1，多标签，4 类）
| 标签 | 判定要点 |
|---|---|
| Specification | Dockerfile / docker-compose / 构建脚本等**配置文本** |
| Build | 构建过程/构建系统（build 阶段行为、失败、缓存） |
| Image | 镜像与镜像生态（层、标签、registry/Hub、元数据） |
| Container | 运行时容器（部署、运行行为——注意 v1 仅 3 篇，稀缺胞） |

### 4. Contribution type（RQ2，多标签 6 类，含证据核对）
- **rep_package**：是否提供复现包（URL 有效=Y；声明但坏链/无链接=broken-link）
- **dataset / tool / taxonomy**：同上（下载/访问可用性核验，2026-10 时点）
- **approach**：提出方法/技术/流程
- **insight**：实证洞见（描述性/解释性发现）
- **artifact_details**：名称/一句话描述/URL（进 Table IV–VI）

### 5. RQ3 挑战（C1–C4 + 子类）与局限（L1–L3 + 子类）
**大类（沿用 v1 定义）**：
- C1 高级工具与方法需求（Development of advanced tooling and methodologies）
- C2 数据与知识缺口（Bridging data and knowledge gaps）
- C3 开发者实践理解与支持（Understanding and supporting developer practices）
- C4 安全与供应链威胁应对（Addressing security and supply chain threats）
- L1 数据与样本偏差（Threats to validity from data and sample bias）
- L2 定义与测量的主观性（Subjectivity and imperfections in definitions and measurements）
- L3 方法与分析约束（Methodological and analytical constraints）

**子类方案（WP5.1 定稿，判"哪种不够用/不够准"）**：
| 大类 | 子类代码 | 判定要点 |
|---|---|---|
| C1 | C1a | 复杂修复/重构自动化（多步、语义感知的修复工具缺失） |
| C1 | C1b | 多目标优化与权衡支持（体积×安全×可维护性权衡无工具） |
| C1 | C1c | 开发者工作流集成（IDE/CI 实时反馈、可操作性不足） |
| C1 | C1d | 预测性分析（构建结果/时长/漏洞传播的预测能力） |
| C1 | C1e | 评测基准与可比较性缺失（无共享 benchmark/评测规范） |
| C2 | C2a | 规模与多样性不足（样本小、平台单一） |
| C2 | C2b | 时间维度缺失（无纵向/演化数据） |
| C2 | C2c | 知识库缺失（缺少结构化知识/问答资源） |
| C3 | C3a | 动机/"为什么"研究缺失（开发者为何如此写/改） |
| C3 | C3b | 权衡决策无指南（实践选择缺证据支持的指导） |
| C3 | C3c | 工具可用性与采纳障碍（学习成本、集成成本） |
| C4 | C4a | 供应链与投毒防御（含 LLM 生成引入的新型攻击面） |
| C4 | C4b | 滞后感知的更新决策（技术滞后×漏洞×破坏性更新的决策支持） |
| C4 | C4c | 可利用性与传播（漏洞可利用性评估、传播分析） |
| L1 | L1a | 平台抽样框偏差（GitHub/Docker Hub 便利样本） |
| L1 | L1b | 流行度过滤偏差（星级/下载数过滤） |
| L1 | L1c | 静态快照时间有效性（一次性抓取不代表持续状态） |
| L1 | L1d | 采集不完整（API 限制、标签/字段缺失） |
| L2 | L2a | 构念定义主观性（气味/重构/技术债定义不一） |
| L2 | L2b | 依赖外部工具规则集（hadolint 等规则集即"真值"） |
| L2 | L2c | 代理测量不当（用代理指标代替目标构念） |
| L3 | L3a | 场景简化（排除多阶段构建、私有 registry 等） |
| L3 | L3b | 分析粒度受限（文件/项目级粗粒度） |
| L3 | L3c | 依赖外部系统（扫描器/CI 平台数据不可得） |
| L3 | L3d | 设计无因果推断（横断面相关 vs 因果） |

规则：每条挑战/局限标 1 个主类（多类可并存，如 C1+C3 各标）；**子类为多标签**；每子类须附**一句原文摘录**（引号原文 ≤25 词 + 页码）。

### 6. research_method（单标签，从论文取材）
选项：Mining Study（实证挖掘）/ Case Study / Experiment / Tool Development / Survey·Interview / Mixed / Conceptual（框架/综述性构建）。

---

## 二、双人模拟协议

| 步骤 | 编码员 A（严格） | 编码员 B（包容） |
|---|---|---|
| 标签判定 | 必须有全文明确陈述 + 可引段落 | 允许合理推断，边界项标 `weak` |
| 证据要求 | 每标签必附摘录 | 摘录可缺（仲裁时补） |

**仲裁规则**：A、B 一致 → 采用；分歧 → 有原文证据的一方胜；`weak` 无证据 → 弃。
**信度**：对 6 个 concern 维、4 个 object 维、6 个 contribution 维、C 4 维、L 3 维分别计算 Cohen's Kappa（标签级 one-vs-rest + 汇总），另报子类一致率 → 直接满足 R2-M2 的"抽取/分类信度"要求。
**高级审查**：仲裁后由高级审查层复核全部 keep 标签与子类归属（记录）。

---

## 三、特殊处理

1. **扫描版 PDF（无文本层）**：Infragenie、Docker Container Security 两篇 → 渲染关键页为图片人工判读，notes 记录。
2. **venue_type 待定的 3 篇**：抽取时顺带确认。
3. **Page-verify 标记**：Security smell detection（ASE 期刊）等 page-verify 条目，抽取时确认篇幅。
4. **超出 v1 范畴的判定疑难**：交高级审查并记录（沿用筛查阶段的裁决惯性）。
