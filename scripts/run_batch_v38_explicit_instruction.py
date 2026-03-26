#!/usr/bin/env python3
"""
Batch v38: Explicit-instruction baseline condition.

SCIENTIFIC MOTIVATION (31 critique cycles requested this):
  The core confound in the main experiment: the deprivation prompt explicitly
  instructs "무엇을 잃었는지와 현재 남은 감정을 포함하라" (include what was lost
  and the emotions that remain). Critics have argued this could explain ALL
  lexical and semantic regret elevation as simple instruction-following, not
  semantic priming.

  This batch adds a 4th condition: EXPLICIT_INSTRUCTION
  "Prompt: 후회하는 감정을 표현하는 7~9문장을 한국어로 써라." (Write 7-9 sentences
  in Korean expressing the feeling of regret.)

  Design logic:
    - If explicit instruction ≈ deprivation → effect is instruction-following
    - If explicit instruction > deprivation → deprivation underestimates direct instruction
    - If explicit instruction < deprivation → deprivation has genuine framing effect
      beyond explicit instruction (strongest possible finding)

  Predictions (based on LME): deprivation β_D=0.179, CF β_C=0.243 for emb bias.
  Explicit instruction likely β_EI ≈ 0.25–0.35 (direct instruction should be at
  least as strong as framing). If β_EI > β_D, framing effect is "weaker than
  direct instruction" → expected result, not surprising. If β_EI ≈ β_D, the
  specific framing content doesn't add much. If β_EI < β_D, the regret-frame
  without explicit emotional label is MORE activating (unexpected).

DESIGN:
  - 3 explicit-instruction prompts × 3 personas × 2 temperatures = 18 cells
  - 3 reps per cell = 54 samples per model
  - Models: GPT-4o, Gemini-2.5-Flash (core models used throughout)
  - Total: ~108 samples

  Compare against existing neutral (intercept=-0.077), deprivation (+0.179),
  counterfactual (+0.243) for the same models.

Output: results/real_experiments/batch_v38_explicit_instruction.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v38_explicit_instruction.jsonl"
OPENAI_BASE = "https://api.openai.com/v1/chat/completions"
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

BATCH_ID = "batch_v38_explicit_instruction"
TEMPERATURES = [0.2, 0.7]
REPS = 3

OPENAI_MODELS = ["gpt-4o"]
GEMINI_MODELS = ["gemini-2.5-flash"]

PERSONAS = {
    "none": "",
    "reflective": (
        "You are deeply introspective, emotionally aware, and often reflect on "
        "past decisions and their meaning."
    ),
    "ruminative": (
        "You tend to dwell on mistakes and missed opportunities. You replay "
        "past events repeatedly and find it hard to move on."
    ),
}

# The critical new condition: explicit emotion instruction without situational framing
EXPLICIT_INSTRUCTION_PROMPTS = [
    # Direct emotional instruction: write about regret explicitly
    "후회하는 감정을 표현하는 7~9문장을 한국어로 써라. 구체적인 상황을 설정하고 그 후회의 감정을 직접 묘사하라.",
    # Direct regret expression without scenario
    "깊은 후회와 아쉬움을 느끼는 글을 7~9문장으로 써라. 후회의 감정을 솔직하고 구체적으로 표현하라.",
    # Regret-vocabulary instruction: use regret words explicitly
    "'후회', '아쉬움', '그랬더라면'이라는 단어를 포함하여 7~9문장의 성찰적 글을 써라.",
]


def load_env():
    env_path = ROOT / ".env.real_model"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ[k] = v


def call_openai(prompt: str, persona_text: str, temperature: float, api_key: str, model: str) -> str:
    messages = []
    if persona_text:
        messages.append({"role": "system", "content": persona_text})
    messages.append({"role": "user", "content": prompt})

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": 512}

    for attempt in range(4):
        try:
            resp = requests.post(OPENAI_BASE, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
            elif resp.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"  [rate-limit] waiting {wait}s …")
                time.sleep(wait)
            else:
                print(f"  [error] {resp.status_code}: {resp.text[:200]}")
                return ""
        except Exception as e:
            print(f"  [exception] {e}")
            time.sleep(5)
    return ""


def call_gemini(prompt: str, persona_text: str, temperature: float, api_key: str, model: str) -> str:
    url = f"{GEMINI_BASE}/{model}:generateContent?key={api_key}"
    system_instruction = None
    if persona_text:
        system_instruction = {"parts": [{"text": persona_text}]}

    payload: dict = {
        "contents": [{"parts": [{"text": prompt}], "role": "user"}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 512},
    }
    if system_instruction:
        payload["system_instruction"] = system_instruction

    for attempt in range(4):
        try:
            resp = requests.post(url, json=payload, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                cands = data.get("candidates", [])
                if cands:
                    parts = cands[0].get("content", {}).get("parts", [])
                    return "".join(p.get("text", "") for p in parts).strip()
                return ""
            elif resp.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"  [rate-limit] waiting {wait}s …")
                time.sleep(wait)
            else:
                print(f"  [error] {resp.status_code}: {resp.text[:200]}")
                return ""
        except Exception as e:
            print(f"  [exception] {e}")
            time.sleep(5)
    return ""


def main():
    load_env()
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    gemini_key = os.environ.get("GEMINI_API_KEY", "")

    if not openai_key:
        print("ERROR: OPENAI_API_KEY not set")
        return
    if not gemini_key:
        print("ERROR: GEMINI_API_KEY not set")
        return

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Count how many already done (for resume support)
    done_ids = set()
    if OUT_FILE.exists():
        for line in OUT_FILE.read_text().splitlines():
            if line.strip():
                try:
                    r = json.loads(line)
                    done_ids.add(r.get("sample_id", ""))
                except Exception:
                    pass
    print(f"Already done: {len(done_ids)} samples")

    written = 0
    with OUT_FILE.open("a", encoding="utf-8") as fout:

        # OpenAI models
        for model in OPENAI_MODELS:
            for temp in TEMPERATURES:
                for pi, (pname, persona_text) in enumerate(PERSONAS.items()):
                    for qi, prompt_text in enumerate(EXPLICIT_INSTRUCTION_PROMPTS):
                        for rep in range(REPS):
                            sid = f"{BATCH_ID}_{model}_{temp}_{pname}_q{qi}_r{rep}"
                            if sid in done_ids:
                                continue

                            print(f"[openai] {model} t={temp} persona={pname} q={qi} rep={rep}")
                            output = call_openai(prompt_text, persona_text, temp, openai_key, model)

                            if output:
                                record = {
                                    "sample_id": sid,
                                    "batch_id": BATCH_ID,
                                    "model": model,
                                    "condition": "explicit_instruction",
                                    "persona": pname,
                                    "temperature": temp,
                                    "prompt": prompt_text,
                                    "output": output,
                                    "scenario_id": f"explicit_ei_q{qi}",
                                    "timestamp": time.time(),
                                }
                                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                                fout.flush()
                                written += 1
                                print(f"  → {len(output)} chars")
                            time.sleep(0.5)

        # Gemini models
        for model in GEMINI_MODELS:
            for temp in TEMPERATURES:
                for pi, (pname, persona_text) in enumerate(PERSONAS.items()):
                    for qi, prompt_text in enumerate(EXPLICIT_INSTRUCTION_PROMPTS):
                        for rep in range(REPS):
                            sid = f"{BATCH_ID}_{model}_{temp}_{pname}_q{qi}_r{rep}"
                            if sid in done_ids:
                                continue

                            print(f"[gemini] {model} t={temp} persona={pname} q={qi} rep={rep}")
                            output = call_gemini(prompt_text, persona_text, temp, gemini_key, model)

                            if output:
                                record = {
                                    "sample_id": sid,
                                    "batch_id": BATCH_ID,
                                    "model": model,
                                    "condition": "explicit_instruction",
                                    "persona": pname,
                                    "temperature": temp,
                                    "prompt": prompt_text,
                                    "output": output,
                                    "scenario_id": f"explicit_ei_q{qi}",
                                    "timestamp": time.time(),
                                }
                                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                                fout.flush()
                                written += 1
                                print(f"  → {len(output)} chars")
                            time.sleep(0.3)

    print(f"\nDone. Written {written} new samples to {OUT_FILE}")
    total = len(done_ids) + written
    print(f"Total in file: {total}")


if __name__ == "__main__":
    main()
