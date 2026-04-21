from __future__ import annotations

from ..config import Settings
from .embeddings import DeterministicEmbeddings, OpenAIEmbeddings
from .llm import GeminiLLM, OpenAILLM, StubLLM
from .vector_store import InMemoryVectorStore, QdrantVectorStore


def build_embeddings(settings: Settings):
    if settings.llm_provider == "openai" and settings.openai_api_key:
        return OpenAIEmbeddings(settings.openai_api_key, settings.openai_embedding_model)
    return DeterministicEmbeddings()


def build_vector_store(settings: Settings):
    if settings.use_memory_vector_store:
        return InMemoryVectorStore()
    return QdrantVectorStore(settings.qdrant_url, settings.qdrant_collection)


def build_llm(settings: Settings):
    provider = settings.llm_provider.lower()
    if provider == "openai" and settings.openai_api_key:
        return OpenAILLM(settings.openai_api_key, settings.openai_model)
    if provider == "gemini" and settings.gemini_api_key:
        return GeminiLLM(settings.gemini_api_key, settings.gemini_model)
    return StubLLM()
