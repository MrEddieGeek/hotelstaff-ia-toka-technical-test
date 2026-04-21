from __future__ import annotations

from ..domain.entities import AgentAnswer, StaffDocument
from .dto import AskRequest, IndexDocumentRequest
from .ports import EmbeddingProvider, LLMProvider, VectorStore

SYSTEM_PROMPT = (
    "Eres un asistente experto en recursos humanos de un hotel. "
    "Responde de forma concisa y en español usando sólo la información del contexto. "
    "Si la información no está en el contexto, responde: "
    '"No encontré información suficiente para responder."'
)


class AgentService:
    def __init__(
        self,
        embeddings: EmbeddingProvider,
        store: VectorStore,
        llm: LLMProvider,
    ) -> None:
        self._embeddings = embeddings
        self._store = store
        self._llm = llm

    async def index(self, req: IndexDocumentRequest) -> None:
        vectors = await self._embeddings.embed([req.text])
        await self._store.ensure_collection(vector_size=len(vectors[0]))
        await self._store.upsert(
            [StaffDocument(doc_id=req.doc_id, text=req.text, metadata=req.metadata)],
            vectors,
        )

    async def index_many(self, docs: list[IndexDocumentRequest]) -> int:
        if not docs:
            return 0
        vectors = await self._embeddings.embed([d.text for d in docs])
        await self._store.ensure_collection(vector_size=len(vectors[0]))
        await self._store.upsert(
            [StaffDocument(doc_id=d.doc_id, text=d.text, metadata=d.metadata) for d in docs],
            vectors,
        )
        return len(docs)

    async def ask(self, req: AskRequest) -> AgentAnswer:
        q_vec = (await self._embeddings.embed([req.question]))[0]
        chunks = await self._store.search(q_vec, top_k=req.top_k)
        context = "\n\n".join(f"- {c.text}" for c in chunks) or "(sin contexto)"
        user_prompt = f"Contexto:\n{context}\n\nPregunta: {req.question}"
        answer = await self._llm.complete(system=SYSTEM_PROMPT, user=user_prompt)
        return AgentAnswer(answer=answer, sources=chunks)
