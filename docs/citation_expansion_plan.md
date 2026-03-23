# Citation Expansion Plan (Target: 50–100 references)

- Source pool: `/Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion/refs/openalex_results.jsonl`
- Candidate set generated: **77** (include/review only, score=citations+priority+recency)
- Current `paper/references.bib` entries: **15**
- Immediate target: **phase-1 +35 entries** (to 50), phase-2 +30~50 entries (to 80~100).

## Top candidates (first 30)

| # | Year | Label | Cited | Title | DOI/URL |
|---|---:|---|---:|---|---|
| 1 | 2023 | review | 2742 | Large language models encode clinical knowledge | https://doi.org/10.1038/s41586-023-06291-2 |
| 2 | 2023 | review | 2558 | ChatGPT Utility in Healthcare Education, Research, and Practice: Systematic Review on the Promising Perspectives and Valid Concerns | https://doi.org/10.3390/healthcare11060887 |
| 3 | 2023 | review | 1930 | How Does ChatGPT Perform on the United States Medical Licensing Examination (USMLE)? The Implications of Large Language Models for Medical Education and Knowledge Assessment | https://doi.org/10.2196/45312 |
| 4 | 2023 | review | 1585 | ChatGPT: Bullshit spewer or the end of traditional assessments in higher education? | https://doi.org/10.37074/jalt.2023.6.1.9 |
| 5 | 2023 | review | 1526 | Sparks of Artificial General Intelligence: Early experiments with GPT-4 | https://doi.org/10.48550/arxiv.2303.12712 |
| 6 | 2024 | review | 892 | A survey on large language model based autonomous agents | https://doi.org/10.1007/s11704-024-40231-1 |
| 7 | 2023 | review | 842 | The imperative for regulatory oversight of large language models (or generative AI) in healthcare | https://doi.org/10.1038/s41746-023-00873-0 |
| 8 | 2023 | review | 509 | Self-Instruct: Aligning Language Models with Self-Generated Instructions | https://doi.org/10.18653/v1/2023.acl-long.754 |
| 9 | 2023 | review | 497 | Capabilities of GPT-4 on Medical Challenge Problems | https://doi.org/10.48550/arxiv.2303.13375 |
| 10 | 2024 | review | 476 | Explainability for Large Language Models: A Survey | https://doi.org/10.1145/3639372 |
| 11 | 2025 | review | 458 | Can Open Large Language Models Catch Vulnerabilities? | https://doi.org/10.4230/oasics.icpec.2025.4 |
| 12 | 2023 | review | 416 | Using cognitive psychology to understand GPT-3 | https://doi.org/10.1073/pnas.2218523120 |
| 13 | 2023 | review | 385 | Can Large Language Models Transform Computational Social Science? | https://doi.org/10.1162/coli_a_00502 |
| 14 | 2023 | review | 336 | A Survey on Large Language Models: Applications, Challenges, Limitations, and Practical Usage | https://doi.org/10.36227/techrxiv.23589741.v1 |
| 15 | 2023 | review | 289 | The Robots Are Here: Navigating the Generative AI Revolution in Computing Education | https://doi.org/10.1145/3623762.3633499 |
| 16 | 2023 | review | 269 | The debate over understanding in AI’s large language models | https://doi.org/10.1073/pnas.2215907120 |
| 17 | 2023 | review | 246 | The Rise and Potential of Large Language Model Based Agents: A Survey | https://doi.org/10.48550/arxiv.2309.07864 |
| 18 | 2024 | review | 186 | Testing theory of mind in large language models and humans | https://doi.org/10.1038/s41562-024-01882-z |
| 19 | 2023 | review | 180 | The now and future of <scp>ChatGPT</scp> and <scp>GPT</scp> in psychiatry | https://doi.org/10.1111/pcn.13588 |
| 20 | 2024 | review | 136 | Evaluating large language models in theory of mind tasks | https://doi.org/10.1073/pnas.2405460121 |
| 21 | 2023 | review | 132 | Evaluating Large Language Models in Theory of Mind Tasks | https://doi.org/10.48550/arxiv.2302.02083 |
| 22 | 2023 | review | 79 | Large Language Models Fail on Trivial Alterations to Theory-of-Mind Tasks | https://doi.org/10.48550/arxiv.2302.08399 |
| 23 | 2023 | review | 73 | An exploratory survey about using ChatGPT in education, healthcare, and research | https://doi.org/10.1101/2023.03.31.23287979 |
| 24 | 2024 | review | 70 | Generative artificial intelligence in mental health care: potential benefits and current challenges | https://doi.org/10.1002/wps.21148 |
| 25 | 2024 | review | 69 | GPT-4 enhanced multimodal grounding for autonomous driving: Leveraging cross-modal attention with large language models | https://doi.org/10.1016/j.commtr.2023.100116 |
| 26 | 2024 | review | 69 | "I'm Not Sure, But...": Examining the Impact of Large Language Models' Uncertainty Expression on User Reliance and Trust | https://doi.org/10.1145/3630106.3658941 |
| 27 | 2024 | review | 65 | On Generative Agents in Recommendation | https://doi.org/10.1145/3626772.3657844 |
| 28 | 2024 | review | 62 | Mathemyths: Leveraging Large Language Models to Teach Mathematical Language through Child-AI Co-Creative Storytelling | https://doi.org/10.1145/3613904.3642647 |
| 29 | 2025 | review | 59 | DeepSeek versus ChatGPT: Multimodal artificial intelligence revolutionizing scientific discovery. From language editing to autonomous content generation—Redefining innovation in research and practice | https://doi.org/10.1002/ksa.12628 |
| 30 | 2023 | review | 53 | Theory of Mind for Multi-Agent Collaboration via Large Language Models | https://doi.org/10.18653/v1/2023.emnlp-main.13 |

## Curation protocol
1. Keep only papers directly supporting one of 5 claims: counterfactual/regret, social cognition, anthropomorphism caution, benchmarking/reliability, reproducibility/automation.
2. For each accepted citation, map to exactly one claim in Related Work table (avoid redundant stacking).
3. Prefer survey/meta-analysis + seminal methods + recent replication reports.
4. Exclude weakly related app papers even if cited high.

## Next action
- Convert top 35 candidates into BibTeX and inject into `paper/references.bib`, then update in-text citations in Related Work and Methods.
