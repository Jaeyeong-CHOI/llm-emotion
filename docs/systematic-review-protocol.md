# Systematic Prior-Work Protocol (PRISMA-lite)

## Objective
Maintain a high-quality prior-work set relevant to:
1. Human regret and counterfactual psychology
2. LLM social-cognitive behavior
3. LLM emotion-like language and anthropomorphism
4. Human-evaluation and benchmark methods that can inform our experiment design

## Sources
- OpenAlex (primary programmatic source)
- Crossref or arXiv API as fallback/manual supplementation
- Manual curation for must-cite landmark papers

## Search strategy
- Query groups live in `queries/search_queries.json`
- Retrieval defaults to top 25 per query, then DOI/title de-duplication
- The current query set includes a dedicated methods lane: `llm_human_eval_methods`

## Screening levels
1. Title/abstract screening with alias-aware scoring
2. Method relevance screening using `screening_priority`
3. Evidence-table coding

## Inclusion criteria
- Relevant to at least one conceptual pillar
- Offers empirical, methodological, or theoretical value
- Includes enough metadata to audit the decision
- English or Korean during the automated pass

## Exclusion criteria
- Off-topic keyword collisions
- Missing bibliographic essentials
- Duplicates and near-duplicates

## Quality guardrails
- Keep claims at the behavioral-similarity level
- Avoid machine phenomenology framing
- Track method-rich review candidates even when they are not direct `include` items
