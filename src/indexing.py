"""索引引擎：向量化和儲存文檔"""

import json
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document


class DocumentIndexer:
    """文檔索引和向量化"""

    def __init__(self, chunk_size=500, chunk_overlap=100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        self.embeddings = None
        self.vectorstore = None

    def load_raw_documents(self, filepath='data/raw_documents.json'):
        """載入原始文檔"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"找不到文檔: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            raw_docs = json.load(f)

        # 轉換為 LangChain Document 格式
        documents = []
        for doc in raw_docs:
            documents.append(Document(
                page_content=doc['content'][:5000],  # 限制長度避免超時
                metadata={
                    'source': doc['source'],
                    'type': doc['type'],
                    'title': doc['title'],
                    'timestamp': doc['timestamp']
                }
            ))
        return documents

    def split_documents(self, documents):
        """分塊文檔"""
        print(f"正在分塊 {len(documents)} 份文檔...")
        chunks = self.splitter.split_documents(documents)
        print(f"✓ 分塊完成：{len(chunks)} 個 chunks")
        return chunks

    def create_vectorstore(self, documents):
        """創建向量庫"""
        print("正在初始化 OpenAI Embeddings...")
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        print("正在建立向量庫...")
        try:
            self.vectorstore = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
            print(f"✓ 向量庫建立完成：{len(documents)} 個文檔")
            return self.vectorstore
        except Exception as e:
            print(f"✗ 向量庫建立失敗: {e}")
            raise

    def save_vectorstore(self, filepath='vector_store/smart_mfg_index'):
        """保存向量庫"""
        os.makedirs('vector_store', exist_ok=True)
        if self.vectorstore:
            self.vectorstore.save_local(filepath)
            print(f"✓ 向量庫已保存到 {filepath}")
        else:
            print("✗ 尚未建立向量庫")

    def load_vectorstore(self, filepath='vector_store/smart_mfg_index'):
        """載入已保存的向量庫"""
        if not os.path.exists(filepath):
            print(f"✗ 找不到向量庫: {filepath}")
            return None

        print("正在載入向量庫...")
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vectorstore = FAISS.load_local(
            filepath,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        print(f"✓ 向量庫載入完成")
        return self.vectorstore

    def index_pipeline(self):
        """完整索引流程"""
        try:
            # 1. 載入原始文檔
            documents = self.load_raw_documents()

            # 2. 分塊
            chunks = self.split_documents(documents)

            # 3. 建立向量庫
            self.create_vectorstore(chunks)

            # 4. 保存
            self.save_vectorstore()

            print("\n✅ 索引完成！")
            return self.vectorstore

        except Exception as e:
            print(f"✗ 索引失敗: {e}")
            raise


def main():
    """運行索引流程"""
    indexer = DocumentIndexer()
    indexer.index_pipeline()


if __name__ == '__main__':
    main()
