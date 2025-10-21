# tools/llm.py
from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI


class LLM:
    """
    Minimal wrapper around OpenAI Chat Completions.
    Reads defaults from environment, but allows explicit overrides.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> None:
        load_dotenv()  # load .env before reading any env vars

        self.client = OpenAI()

        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.temperature = float(
            os.getenv("TEMPERATURE", "0.2") if temperature is None else temperature
        )
        self.max_tokens = int(
            os.getenv("MAX_TOKENS", "2000") if max_tokens is None else max_tokens
        )

    def chat(self, system: str, user: str) -> str: 
        resp = self.client.chat.completions.create(
             model=self.model, 
             temperature=self.temperature, 
             max_tokens=self.max_tokens,
               messages=[ 
                   {"role": "system", "content": system}, 
                   {"role": "user", "content": user},
                     ],
                ) 
        return (resp.choices[0].message.content or "").strip()