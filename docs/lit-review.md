# Literature Review (Seed)

## Scope
This review focuses on three pillars:
1. Human psychology of regret/counterfactual thinking
2. LLM socio-cognitive behavior (ToM, perspective-taking)
3. Anthropomorphism and emotional attribution to AI

---

## A. Human regret & counterfactuals

### Key references
- Roese, N. J., & Epstude, K. (2017). *The Functional Theory of Counterfactual Thinking*.
- Epstude, K., & Roese, N. J. (2008). *The Functional Theory of Counterfactual Thinking*.
- Byrne, R. M. J. (2016). *Understanding Counterfactuality* (review).
- Kahneman & Tversky work on regret and decision framing (classic foundation).

### Relevance
These establish that regret is often expressed through:
- Upward counterfactuals ("if only…")
- Self-blame/agency language
- Temporal revisiting of irreversible choices

---

## B. LLM social cognition and mental-state reasoning

### Key references
- Kosinski, M. (2024). *Evaluating large language models in theory of mind tasks*. PNAS.
- Strachan et al. (2024). *Testing theory of mind in large language models and humans*. Nature Human Behaviour.
- Ma et al. (2024). *Think Twice: Perspective-Taking Improves LLMs' ToM Capabilities*. ACL.
- Ullman (2023). *Large Language Models Fail on Trivial Alterations to Theory-of-Mind Tasks*.

### Relevance
These papers show that apparent mental-state competence in LLMs is sensitive to prompt format, task wording, and reasoning scaffolds. This supports our framing: behavior can appear human-like without implying internal feeling.

---

## C. Emotion and anthropomorphism around LLM/chatbots

### Selected references
- "Exploring Large Language Models’ Emotion Detection Abilities" (IEEE CAI 2023, DOI: 10.1109/CAI54212.2023.00110)
- "Real-time emotion generation in human-robot dialogue using large language models" (Frontiers in Robotics and AI, 2023, DOI: 10.3389/frobt.2023.1271610)
- "User perception and self-disclosure towards an AI psychotherapy chatbot according to anthropomorphism" (Telematics and Informatics, 2023, DOI: 10.1016/j.tele.2023.102052)

### Relevance
These studies motivate separating:
- **Model capability** (producing affective language)
- **User attribution** (perceiving emotion/mind in AI)

---

## Gap this project targets
Most existing work examines emotion recognition, empathy prompts, or ToM benchmarks. Fewer studies focus on **regret-like language about unattainable states/objects** as a structured behavioral phenomenon across LLMs.

Our project contributes by:
1. Building a dedicated prompt battery around "missing what one cannot have"
2. Comparing LLM outputs with human regret narratives under matched scenarios
3. Quantifying similarity via interpretable linguistic markers + human ratings

---

## Working bibliography file
See `refs/bibliography.bib` for machine-readable references (to expand continuously).
