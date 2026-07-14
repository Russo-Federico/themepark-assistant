# All provider swaps are controlled here. No other files need to change.

# Vector store
VECTOR_STORE_PROVIDER = "chromadb"      # "chromadb" | "vertex_ai"

# Speech to text
STT_PROVIDER = "whisper"                # "whisper" | "google"

# Models
GEMINI_MODEL = "gemini-3.1-flash-lite"
EMBEDDING_MODEL = "gemini-embedding-2"

# RAG
RETRIEVAL_TOP_K = 5
SIMILARITY_THRESHOLD = 0.70              # Level 3 guardrail threshold
CHUNK_SIZE_TOKENS = 512
CHUNK_OVERLAP_TOKENS = 50

# ChromaDB
CHROMA_PERSIST_PATH = "./chroma_db"

# CORS
FRONTEND_ORIGIN = "http://localhost:5173"
