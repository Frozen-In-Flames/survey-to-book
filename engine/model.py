"""Model clients.

Generation is fully offline. Two clients implement the same interface:

* ``StubModel`` -- deterministic, dependency-free; used by the test
  suite and for dry runs. It echoes structural markers from the prompt
  so tests can verify exactly what context each page was conditioned on.
* ``LlamaServerModel`` -- talks to a local llama.cpp server
  (``llama-server``) over loopback HTTP. No network access beyond
  localhost is involved at any point.
"""

from __future__ import annotations

import json
import re
import urllib.request


class StubModel:
    """Deterministic stand-in that reflects prompt structure."""

    name = "stub-model (deterministic test double)"

    def complete(self, prompt: str, max_tokens: int = 512) -> str:
        qid_match = re.search(r"QUESTION_ID:\s*(\S+)", prompt)
        if "TASK: SUMMARIZE_CHAPTER" in prompt:
            chapter = re.search(r"CHAPTER_ID:\s*(\S+)", prompt)
            return (f"Stub synopsis of chapter "
                    f"{chapter.group(1) if chapter else '?'}. "
                    f"Events proceed in order and the narrator's "
                    f"circumstances change in ways the bible records.")
        qid = qid_match.group(1) if qid_match else "unknown"
        # Echo a sentinel proving which bible/synopsis state was present.
        sentinels = re.findall(r"SENTINEL_[A-Z0-9_]+", prompt)
        seen = ", ".join(sorted(set(sentinels))) or "none"
        body = (
            f"This is the stub page for question {qid}. It was generated "
            f"with full knowledge of the story bible and synopsis supplied "
            f"in its prompt, and it continues the narrative in the "
            f"framework's voice without contradicting any established "
            f"fact. Sentinels observed in context: {seen}. The page holds "
            f"to roughly the target length by developing the answer's "
            f"material through the devices assigned to this slot: a scene "
            f"is rendered rather than summarized, concrete details carry "
            f"the emotion, and the closing line turns the page toward "
            f"what comes next in the arc of the book as a whole."
        )
        return body


class LlamaServerModel:
    """Client for a local llama.cpp server (offline, loopback only)."""

    def __init__(self, base_url: str = "http://127.0.0.1:8080",
                 model_label: str = "local-llama.cpp",
                 temperature: float = 0.8, top_p: float = 0.95,
                 repeat_penalty: float = 1.1) -> None:
        self.base_url = base_url.rstrip("/")
        self.name = model_label
        self.temperature = temperature
        self.top_p = top_p
        self.repeat_penalty = repeat_penalty

    def complete(self, prompt: str, max_tokens: int = 512) -> str:
        payload = {
            "prompt": prompt,
            "n_predict": max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "repeat_penalty": self.repeat_penalty,
            "stop": ["</s>", "\nQUESTION_ID:", "\nTASK:"],
            "cache_prompt": True,
        }
        req = urllib.request.Request(
            f"{self.base_url}/completion",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=1800) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data["content"].strip()
