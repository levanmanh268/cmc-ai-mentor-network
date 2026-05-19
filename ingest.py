import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Đường dẫn
KNOWLEDGE_PATH = "knowledge_base"
PERSIST_DIRECTORY = "chroma_db"

print("Đang nạp dữ liệu từ knowledge_base...")

# Load file .md
loader = DirectoryLoader(
    KNOWLEDGE_PATH,
    glob="**/*.md",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"}
)
documents = loader.load()
print(f"Đã load {len(documents)} file.")

# Chia nhỏ văn bản
text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
chunks = text_splitter.split_documents(documents)
print(f"Đã chia thành {len(chunks)} đoạn.")

# Dùng model nhẹ hơn
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    model_kwargs={'device': 'cpu'}
)

# Lưu vào Chroma
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=PERSIST_DIRECTORY
)

print("✅ Đã nạp xong dữ liệu vào ChromaDB!")
print(f"Dữ liệu được lưu tại: {PERSIST_DIRECTORY}")