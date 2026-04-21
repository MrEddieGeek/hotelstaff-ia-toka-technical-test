from __future__ import annotations

import hashlib
import math


class OpenAIEmbeddings:
    def __init__(self, api_key: str, model: str) -> None:
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        resp = await self._client.embeddings.create(model=self._model, input=texts)
        return [d.embedding for d in resp.data]


class DeterministicEmbeddings:
    """Embeddings determinísticos basados en hash — útil en tests sin red.

    Produce vectores unitarios de dimensión fija (384). No es semántico,
    pero permite índice/búsqueda estable en tests.
    """

    DIM = 384

    async def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            h = hashlib.sha256(text.lower().encode("utf-8")).digest()
            # Expande hasta DIM reutilizando bytes.
            raw = (h * ((self.DIM // len(h)) + 1))[: self.DIM]
            vec = [(b - 127) / 127.0 for b in raw]
            # Aporta señal léxica: palabras → bumps en índices determinísticos.
            for word in text.lower().split():
                idx = int(hashlib.md5(word.encode()).hexdigest(), 16) % self.DIM
                vec[idx] += 1.0
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            vectors.append([x / norm for x in vec])
        return vectors
