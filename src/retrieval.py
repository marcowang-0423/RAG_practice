"""RAG 查詢引擎"""

import os
import json
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import faiss
from anthropic import Anthropic

load_dotenv()

class SmartMfgRAG:
    """智慧製造 AI 技術文檔 RAG 系統"""

    def __init__(self, vectorstore_path='vector_store/smart_mfg_index'):
        self.vectorstore_path = vectorstore_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vectorstore = None
        self.metadata = None
        self.client = Anthropic()
        self.load_system()

    def load_system(self):
        """載入向量庫和 API"""
        if not os.path.exists(f"{self.vectorstore_path}.faiss"):
            raise FileNotFoundError(
                f"向量庫不存在: {self.vectorstore_path}\n"
                "請先執行: python src/scraper.py && python src/indexing.py"
            )

        print("正在載入向量庫...")
        self.vectorstore = faiss.read_index(f"{self.vectorstore_path}.faiss")
        with open(f"{self.vectorstore_path}_metadata.json", 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        print(f"✓ 向量庫載入完成：{len(self.metadata)} 個文檔")

    def query(self, question):
        """查詢並生成答案"""
        try:
            # 向量化查詢
            question_embedding = self.model.encode([question])[0].astype('float32')

            # 搜尋相關文檔
            distances, indices = self.vectorstore.search(np.array([question_embedding]), k=5)

            # 獲取相關內容
            relevant_docs = [self.metadata[i] for i in indices[0] if i < len(self.metadata)]
            context = "\n\n".join([f"來源: {d['source']}\n{d['content']}" for d in relevant_docs])

            # 用 Claude 生成答案
            prompt = f"""你是一個智慧製造和 AI 技術的專家助手。
根據以下相關文檔，用中文回答用戶的問題。
如果文檔中沒有相關信息，請說明你無法從提供的文檔中找到答案。

相關文檔:
{context}

問題: {question}

答案:"""

            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return {
                'answer': message.content[0].text,
                'sources': relevant_docs
            }
        except Exception as e:
            return {
                'answer': f'查詢失敗: {str(e)}',
                'sources': []
            }

    def format_result(self, result):
        """格式化結果"""
        answer = result['answer']
        sources = result['sources']

        output = f"\n{'='*60}\n"
        output += f"💡 答案：\n{answer}\n"

        if sources:
            output += f"\n📚 參考資源:\n"
            for i, doc in enumerate(sources, 1):
                output += f"  {i}. {doc['title']}\n     ({doc['source']})\n"

        output += f"{'='*60}\n"
        return output


def main():
    rag = SmartMfgRAG()

    queries = [
        "瑕疵檢測有哪些常見的深度學習方法？",
        "什麼是 RAG？",
    ]

    print("🚀 智慧製造 AI 技術文檔助手\n")

    for query in queries:
        print(f"\n❓ 問題: {query}")
        result = rag.query(query)
        print(rag.format_result(result))


if __name__ == '__main__':
    main()
