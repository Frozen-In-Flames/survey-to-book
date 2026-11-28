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
        # Every sentence names its question, so stub pages never share
        # a full sentence with each other: the duplication guard must
        # see a well-behaved model as clean.
        body = (
            f"This is the stub page for question {qid}. The page for "
            f"{qid} was generated with full knowledge of the "
            f"established state and synopsis supplied in its prompt. "
            f"In the page "
            f"for {qid}, the narrative continues in the framework's "
            f"voice without contradicting any established fact. "
            f"Sentinels observed in the context for {qid}: {seen}. "
            f"The page for {qid} develops its answer's material "
            f"through the devices assigned to its own slot, rendering "
            f"a scene rather than summarizing one. Concrete details "
            f"carry the emotion on the page for {qid}, and its "
            f"closing line turns toward what comes next in the arc. "
            f"The page for {qid} ends here."
        )
        return body

    def continue_text(self, text: str, max_tokens: int = 64) -> str:
        """The stub cannot continue text: its pages are whole by
        construction, so a truncated page under the stub stays
        truncated and is measured as such."""
        return ""


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

    def continue_text(self, text: str, max_tokens: int = 64) -> str:
        """Continue raw text (no chat template): the page itself
        is the prompt, and the model writes on from its last
        token. Used only to finish a page whose token budget ran
        out mid-sentence. The result is returned unstripped: its
        leading characters carry the spacing the model itself
        emitted, so it joins the page exactly."""
        payload = {
            "prompt": text,
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
        return data["content"]
