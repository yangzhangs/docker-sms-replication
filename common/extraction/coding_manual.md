# Extraction and coding manual

This manual defines the codes used for all 92 primary studies. Metadata fields were
reconstructed from the published tables; RQ3 evidence was coded with the same rules.

## 1. Metadata and extraction fields

- `selection_channel`: initial search, update search, short-paper re-screening, or snowballing.
- `zotero_key`, `title`, `year`, `venue_type`, `venue_name`
- `concerns`: RQ1 SE concerns (multi-label).
- `objects`: RQ1 Docker objects (multi-label).
- `rep_package`, `dataset`, `approach`, `tool`, `taxonomy`, `insight`: RQ2 contribution types.
- `challenges`: RQ3 challenge categories and subcategories (multi-label).
- `limitations`: RQ3 limitation categories and subcategories (multi-label).
- `research_method`: one label from the scheme in Section 6.
- `*_A`, `*_B`: independent coders' labels for reliability checks.

## 2. SE concerns (RQ1, multi-label)

A label is assigned only when the concern is a primary claim in the paper's research
questions, abstract, or conclusions; background mentions are not coded.

| Code | Definition |
|---|---|
| Performance | Performance or resource efficiency of Docker artifacts, including image size, build time, startup, and runtime overhead. |
| Maintainability | Maintainability, including smells, refactoring, technical debt, configuration quality, and maintenance cost. |
| Reliability | Reliability and fault tolerance, including build failures, flakiness, repair, and recoverability. |
| Security | Security at the Docker-artifact level, including vulnerabilities, supply chain, poisoning, licensing, and information leakage. |
| Evolution | Change over time, including version updates, change patterns, technical lag, and longitudinal analysis. |
| Adoption | Adoption and use, including motivations, developer practices, and ecosystem surveys. |

## 3. Docker objects (RQ1, multi-label)

| Code | Definition |
|---|---|
| Specification | Configuration text such as Dockerfiles, Compose files, and build scripts. |
| Build | The build process or build system, including build-stage behavior, failures, and caching. |
| Image | Images and the image ecosystem, including layers, tags, registries, and image metadata. |
| Container | Running containers, including deployment and runtime behavior. This object is sparsely studied. |

## 4. Contribution types (RQ2, multi-label)

| Code | Definition |
|---|---|
| rep_package | A replication package is declared. A valid URL is `Y`; a declared but broken or missing link is `broken-link`. |
| dataset | A released or shared data collection. For new additions, the collection must be a Docker-artifact corpus; two shared build/issue collections are retained for continuity. |
| tool | An implemented tool, not merely a conceptual framework or proposed approach. |
| taxonomy | A structured classification of concepts, artifacts, problems, or practices. |
| approach | A method, technique, workflow, or analytical procedure. |
| insight | An empirical or explanatory finding. |

Artifact availability was checked at the time of extraction. A declaration without a
working link remains a declaration, but its link status is recorded as `broken-link`.

## 5. Challenge and limitation taxonomy (RQ3)

### 5.1 Major categories

- **C1**: Development of advanced tooling and methodologies.
- **C2**: Bridging data and knowledge gaps.
- **C3**: Understanding and supporting developer practices.
- **C4**: Addressing security and supply-chain threats.
- **L1**: Threats to validity from data and sample bias.
- **L2**: Subjectivity and imperfections in definitions and measurements.
- **L3**: Methodological and analytical constraints.

### 5.2 Subcategories

| Category | Code | Definition |
|---|---|---|
| C1 | C1a | Complex repair and refactoring automation: multi-step, semantics-aware repair is missing. |
| C1 | C1b | Multi-objective optimization and trade-off support, for example size, security, and maintainability. |
| C1 | C1c | Developer-workflow integration, including IDE or CI feedback and actionability. |
| C1 | C1d | Predictive analysis for build outcomes, duration, or vulnerability propagation. |
| C1 | C1e | Benchmarks and comparability: shared benchmarks or evaluation protocols are missing. |
| C2 | C2a | Insufficient scale or diversity of data. |
| C2 | C2b | Missing temporal dimension or longitudinal data. |
| C2 | C2c | Missing structured knowledge bases or curated resources. |
| C3 | C3a | Missing motivation and "why" studies of developer behavior. |
| C3 | C3b | Missing guidance for trade-off decisions. |
| C3 | C3c | Tool usability and adoption barriers. |
| C4 | C4a | Supply-chain and poisoning defense, including new attack surfaces introduced by generated artifacts. |
| C4 | C4b | Lag-aware update decisions combining technical lag, vulnerabilities, and breaking changes. |
| C4 | C4c | Exploitability and propagation of vulnerabilities. |
| L1 | L1a | Platform sampling-frame bias, such as convenience samples from GitHub or Docker Hub. |
| L1 | L1b | Popularity-filter bias, such as star or download thresholds. |
| L1 | L1c | Static-snapshot time validity. |
| L1 | L1d | Incomplete collection due to API limits or missing fields. |
| L2 | L2a | Subjective construct definitions, such as smells, refactorings, or technical debt. |
| L2 | L2b | Dependence on external rule sets, such as a linter's rules. |
| L2 | L2c | Imperfect proxy measures for the target construct. |
| L3 | L3a | Scenario simplification, such as excluding multi-stage builds or private registries. |
| L3 | L3b | Limited analysis granularity. |
| L3 | L3c | Dependence on external systems or data sources. |
| L3 | L3d | No causal inference from a cross-sectional design. |

A study may receive multiple challenge and limitation labels. Each subcategory
assignment is supported by a source excerpt in the extraction record.

## 6. Research method

One label per study: mining study, case study, experiment, tool development,
survey/interview, mixed methods, or conceptual.

## 7. Coding and reliability protocol

Two coders labeled the corpus independently. Coder A required explicit full-text
evidence for each label; Coder B could mark a reasonable inference as `weak`.
Disagreements were resolved by source evidence and, when needed, a third author.
Label-level one-vs-rest Cohen's Kappa is reported for SE concerns, Docker objects,
contribution types, challenges, and limitations. The extraction master retains both
coders' labels and the final adjudicated labels.

## 8. Special cases

- Scanned PDFs without a text layer were read from rendered page images.
- Page length was checked for records near the five-page boundary.
- A conference version superseded by an extended journal version was excluded.
- Ambiguous venue types and artifact links were resolved during extraction and
  recorded in the screening or corpus tables.
