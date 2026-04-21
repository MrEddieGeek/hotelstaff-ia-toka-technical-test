from __future__ import annotations


class OpenAILLM:
    def __init__(self, api_key: str, model: str) -> None:
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def complete(self, *, system: str, user: str) -> str:
        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""


class GeminiLLM:
    def __init__(self, api_key: str, model: str) -> None:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)

    async def complete(self, *, system: str, user: str) -> str:
        # google-generativeai no es async nativo → lo ejecutamos en pool.
        import asyncio

        def _call() -> str:
            resp = self._model.generate_content(f"{system}\n\n{user}")
            return resp.text or ""

        return await asyncio.to_thread(_call)


class StubLLM:
    """Fallback determinístico para tests / demos sin API key.

    Devuelve un resumen citando los primeros chunks del contexto.
    """

    async def complete(self, *, system: str, user: str) -> str:
        # user = "Contexto:\n- A\n- B\n\nPregunta: X"
        context_part = ""
        if "Contexto:" in user:
            context_part = user.split("Contexto:", 1)[1].split("Pregunta:", 1)[0].strip()
        if not context_part or context_part == "(sin contexto)":
            return "No encontré información suficiente para responder."
        return f"Según los datos disponibles: {context_part[:400]}"
