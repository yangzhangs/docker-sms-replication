# Search protocol

## Scope

- Search window: January 2014 through 30 September 2026.
- Subject: software engineering research on Docker artifacts.
- Digital libraries: ACM Digital Library, IEEE Xplore, SpringerLink, ScienceDirect, and WILEY Online Library, complemented by Google Scholar screening and snowballing.

## Query

The core query is:

`("Docker" OR "Dockerfile" OR "DockerHub" OR "docker-compose" OR "dockerized")`

Hyphenation-insensitive and wildcard variants (for example, `Docker*` and `docker compose`) were applied according to each library's syntax. The exact per-run queries, fields, date filters, and hit counts are recorded in `common/search/search_log.csv`.

## Fields

- ACM Digital Library: title and abstract.
- WILEY Online Library: title and abstract.
- SpringerLink: title.
- IEEE Xplore: title, abstract, and keywords.
- ScienceDirect: title, abstract, and author-specified keywords.
- Google Scholar: no field restriction; the top 500 records by relevance were screened.

## Validation and selection

The query was validated against 23 known relevant papers from seven SE venues; all 23 were retrieved. The five-library searches returned 4,382 records. After consolidating three identical exports, the automatic bibliographic filter removed 652 non-archival records, leaving 3,727 records for detailed dual-author screening.

Snowballing examined 489 referenced works and 650 citing records, yielding 232 unique candidates; three additional primary studies were included. The Google Scholar extension screened the top 500 records and added no primary studies.
