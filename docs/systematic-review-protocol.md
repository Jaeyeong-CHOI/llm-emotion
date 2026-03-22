# Systematic Prior-Work Protocol (PRISMA-lite)

## Objective
Identify and maintain high-quality prior work relevant to:
1. Human regret/counterfactual psychology
2. LLM social-cognitive behavior (ToM, perspective-taking)
3. LLM emotion-like language and anthropomorphism

## Databases / Sources
- OpenAlex (primary programmatic source)
- Crossref (optional fallback)
- arXiv API (supplementary preprints)
- Manual curation for must-cite landmark papers

## Search strategy
- Query groups are stored in `queries/search_queries.json`
- Each group has 3+ query strings
- Default retrieval: top 25 per query, then de-dup by DOI/title

## Inclusion criteria
- Peer-reviewed papers or high-impact preprints
- Direct relevance to one of the 3 pillars
- Contains empirical, methodological, or theoretical contribution
- English (initially)

## Exclusion criteria
- Off-topic keyword collisions (e.g., unrelated robotics emotions)
- No metadata / inaccessible bibliographic fields
- Duplicates and near-duplicates

## Screening levels
1. **Title/abstract screening**
2. **Method relevance screening**
3. **Evidence-table coding**

## Evidence-table fields
- Title, year, venue, DOI/URL
- Pillar (psych / ToM / anthropomorphism)
- Method type (experiment, benchmark, survey, theory)
- Main finding (1-2 lines)
- Use in our study (motivation / metric / threat / framing)

## Update cadence
- Weekly automated pull (script + GitHub Action)
- Monthly manual curation pass
- Milestone review before major experiment runs

## Quality guardrails
- Keep framing as **behavioral similarity** (as-if psychology)
- Avoid claims of machine phenomenology/conscious emotion
- Record threats to validity in each update cycle
