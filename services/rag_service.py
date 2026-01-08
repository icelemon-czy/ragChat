import os
import asyncio
from typing import List, Dict

from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
import chromadb
from PyQt5.QtCore import QStandardPaths, QObject, pyqtSignal

class RagService(QObject):
    """
    Service to handle RAG operations: ChromaDB access and LLM calls.
    Inherits from QObject to use Signals if needed, but primarily used via async methods.
    """
    
    def __init__(self, api_key: str):
        super().__init__()
        # Set API Key for DashScope
        os.environ["DASHSCOPE_API_KEY"] = api_key
        
        # 1. Initialize Embeddings
        self.embeddings = DashScopeEmbeddings(
            model="text-embedding-v1"
        )
        
        # 2. Initialize ChromaDB (Persistent)
        # Store in AppData folder to avoid permission issues
        data_path = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        db_path = os.path.join(data_path, "RagDataBase", "chroma_db")
        os.makedirs(db_path, exist_ok=True)
        
        # Using langchain-chroma wrapper for easier integration
        self.vector_store = Chroma(
            collection_name="rag_collection",
            embedding_function=self.embeddings,
            persist_directory=db_path
        )

        # 3. Initialize Chat Model
        self.chat_model = ChatTongyi(
            model="qwen-plus",
            streaming=True
        )

    async def add_document(self, title: str, content: str, source: str = ""):
        """
        Splits text and adds to ChromaDB with metadata. 
        Also generates a brief summary for the metadata.
        """
        # Generate summary (first 200 chars or LLM summary)
        # For speed, we'll use a simple extraction. 
        # Ideally, use self.chat_model to summarize, but that consumes tokens.
        summary = content[:200] + "..." if len(content) > 200 else content

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        splits = text_splitter.create_documents(
            texts=[content],
            metadatas=[{"title": title, "source": source, "summary": summary, "full_content": content}]
        )
        
        # Async add documents
        await self.vector_store.aadd_documents(splits)
        return len(splits)

    async def get_all_documents(self) -> List[Dict]:
        """
        Retrieves all unique documents (by title/source) from metadata.
        Note: Chroma doesn't have a direct 'get all unique docs' efficiently, 
        so we fetch all and deduplicate based on metadata for the UI list.
        """
        # This is a bit of a hack since VectorStores aren't relational DBs.
        # We fetch all data to list in the UI. 
        # For a production app, we might store document/metadata list in a separate SQLite table.
        # Here we just `get` everything.
        results = self.vector_store.get()
        metadatas = results['metadatas']
        
        unique_docs = {}
        for m in metadatas:
            if not m: continue
            title = m.get('title', 'Untitled')
            if title not in unique_docs:
                unique_docs[title] = {
                    'title': title,
                    'source': m.get('source', ''),
                    'summary': m.get('summary', m.get('full_content', '')[:100]), # Use summary if available
                }
        return list(unique_docs.values())

    async def extract_text_from_file(self, file_path: str) -> str:
        """
        Extracts text from a local file using unstructured.
        Runs in a separate thread to avoid blocking the event loop.
        """
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._extract_text_sync, file_path)

    def _extract_text_sync(self, file_path: str) -> str:
        from unstructured.partition.auto import partition
        try:
            elements = partition(filename=file_path)
            return "\n\n".join([str(e) for e in elements]) 
        except Exception as e:
            raise RuntimeError(f"Unstructured parsing failed: {str(e)}")

    async def query(self, user_input: str) -> str:
        """
        Performs RAG: Search -> Augment -> Generate
        """
        # 1. Retrieve
        docs = await self.vector_store.asimilarity_search(user_input, k=3)
        context_text = "\n\n".join([d.page_content for d in docs])
        
        # 2. Prompt
        system_prompt = f"""You are a helpful assistant. Use the following context to answer the user's question.
If the answer is not in the context, say you don't know.

Context:
{context_text}
"""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ]
        
        # 3. Generate (Streaming not implemented in this simple method, returns full str)
        response = await self.chat_model.ainvoke(messages)
        return response.content

    async def stream_query(self, user_input: str):
        """
        Generator for streaming response
        """
        docs = await self.vector_store.asimilarity_search(user_input, k=3)
        context_text = "\n\n".join([d.page_content for d in docs])
        
        system_prompt = f"""You are a helpful assistant. Use the following context to answer the user's question.
If the answer is not in the context, say you don't know. Do not invent facts.

Context:
{context_text}
"""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ]
        
        # Use astream
        async for chunk in self.chat_model.astream(messages):
            yield chunk.content
