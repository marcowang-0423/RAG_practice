"""索引引擎：向量化和儲存文檔"""

import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

class DocumentIndexer:
    """文檔索引和向量化"""

    def __init__(self, chunk_size=500):
        self.chunk_size = chunk_size
        self.documents = []
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vectorstore = None

    def load_raw_documents(self, filepath='data/raw_documents.json'):
        """載入原始文檔"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"找不到文檔: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            raw_docs = json.load(f)

        self.documents = raw_docs
        return raw_docs

    def split_documents(self, documents):
        """簡單分塊"""
        chunks = []
        for doc in documents:
            content = doc['content']
            for i in range(0, len(content), self.chunk_size):
                chunk = {
                    'content': content[i:i+self.chunk_size],
                    'source': doc['source'],
                    'title': doc['title'],
                    'type': doc['type']
                }
                chunks.append(chunk)
        print(f"✓ 分塊完成：{len(chunks)} 個 chunks")
        return chunks

    def create_vectorstore(self, chunks):
        """創建向量庫"""
        print("正在向量化文檔（本地模型）...")
        texts = [c['content'] for c in chunks]
        embeddings = self.model.encode(texts, show_progress_bar=True)

        # 創建 FAISS 索引
        dimension = embeddings.shape[1]
        self.vectorstore = faiss.IndexFlatL2(dimension)
        self.vectorstore.add(embeddings.astype('float32'))

        # 保存元數據
        self.metadata = chunks

        print(f"✓ 向量庫建立完成：{len(chunks)} 個文檔")
        return self.vectorstore

    def save_vectorstore(self, filepath='vector_store/smart_mfg_index'):
        """保存向量庫"""
        os.makedirs('vector_store', exist_ok=True)
        if self.vectorstore:
            faiss.write_index(self.vectorstore, f"{filepath}.faiss")
            with open(f"{filepath}_metadata.json", 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            print(f"✓ 向量庫已保存到 {filepath}")
        else:
            print("✗ 尚未建立向量庫")

    def load_vectorstore(self, filepath='vector_store/smart_mfg_index'):
        """載入向量庫"""
        if not os.path.exists(f"{filepath}.faiss"):
            print(f"✗ 找不到向量庫: {filepath}")
            return None

        print("正在載入向量庫...")
        self.vectorstore = faiss.read_index(f"{filepath}.faiss")
        with open(f"{filepath}_metadata.json", 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        print(f"✓ 向量庫載入完成")
        return self.vectorstore

    def index_pipeline(self):
        """完整索引流程"""
        try:
            documents = self.load_raw_documents()
            chunks = self.split_documents(documents)
            self.create_vectorstore(chunks)
            self.save_vectorstore()
            print("\n✅ 索引完成！")
            return self.vectorstore
        except Exception as e:
            print(f"✗ 索引失敗: {e}")
            raise


def main():
    indexer = DocumentIndexer()
    indexer.index_pipeline()


if __name__ == '__main__':
    main()
