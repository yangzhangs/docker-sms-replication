# Screening criteria and process

## Inclusion criteria

1. The study is written in English.
2. The study belongs to the Computer Science subject area (applied to SpringerLink, ScienceDirect, and WILEY).
3. The study was published between 2014 and 30 September 2026.
4. The study was published in a journal or a conference/symposium proceedings.
5. The full text is accessible.
6. The study was published in a recognized SE venue, or its context is SE activities, artifacts, or processes.

## Exclusion criteria

1. The study is a non-archival short format (for example, a poster or extended abstract) or contains fewer than five pages.
2. The full text is not available online.
3. The study is an old conference version superseded by an extended journal version.
4. The study is a review or survey.
5. The study uses Docker only for implementation, comparative analysis, or infrastructure-centric operations without an explicit SE contribution.
6. The study focuses on a non-SE domain.
7. The study is a pure replication without new contributions. Replications that extend prior work with new data, analyses, or contexts are retained.

## Process

Both authors independently labeled every record. Agreement was computed after both coders completed the full preliminary-screening corpus (N = 3,727): 91.7% agreement, multi-class Cohen's Kappa 0.872, binary keep-or-exclude Kappa 0.707, and 311 disagreements (8.3%). Disagreements were resolved by consensus with all authors. The automatic bibliographic filter and the per-record screening data are in `common/screening/`.

The page-count criterion was re-applied to records excluded under the earlier threshold. The re-screening data and the 40-record verification sample are in `common/screening/`.
