"""RAG 查詢引擎"""

from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
import os


class SmartMfgRAG:
    """智慧製造 AI 技術文檔 RAG 系統"""

    def __init__(self, vectorstore_path='vector_store/smart_mfg_index'):
        self.vectorstore_path = vectorstore_path
        self.vectorstore = None
        self.qa_chain = None
        self.llm = None
        self.load_system()

    def load_system(self):
        """載入向量庫和 LLM"""
        # 載入向量庫
        if not os.path.exists(self.vectorstore_path):
            raise FileNotFoundError(
                f"向量庫不存在: {self.vectorstore_path}\n"
                "請先執行: python src/scraper.py && python src/indexing.py"
            )

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vectorstore = FAISS.load_local(
            self.vectorstore_path,
            embeddings,
            allow_dangerous_deserialization=True
        )

        # 初始化 LLM
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.2,
            max_tokens=1024
        )

        # 自定義 prompt
        template = """你是一個智慧製造和 AI 技術的專家助手。
根據以下相關文檔，用中文回答用戶的問題。
如果文檔中沒有相關信息，請說明你無法從提供的文檔中找到答案。

相關文檔:
{context}

問題: {question}

答案:"""

        prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=template
        )

        # 建立 QA 鏈
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={'k': 5}  # 取前 5 個最相關的 chunks
            ),
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )

    def query(self, question):
        """查詢並生成答案"""
        try:
            result = self.qa_chain({"query": question})
            return {
                'answer': result['result'],
                'sources': result.get('source_documents', [])
            }
        except Exception as e:
            return {
                'answer': f'查詢失敗: {str(e)}',
                'sources': []
            }

    def format_result(self, result):
        """格式化結果用於顯示"""
        answer = result['answer']
        sources = result['sources']

        output = f"\n{'='*60}\n"
        output += f"💡 答案：\n{answer}\n"

        if sources:
            output += f"\n📚 參考資源:\n"
            for i, doc in enumerate(sources, 1):
                source = doc.metadata.get('source', 'Unknown')
                title = doc.metadata.get('title', 'Unknown')
                output += f"  {i}. {title}\n     ({source})\n"

        output += f"{'='*60}\n"
        return output


def main():
    """示例查詢"""
    rag = SmartMfgRAG()

    # 示例查詢
    queries = [
        "瑕疵檢測有哪些常見的深度學習方法？",
        "如何使用 YOLO 進行工業品質檢測？",
        "在 Kubernetes 上部署機器學習模型有什麼最佳實踐？",
        "AI Agent 框架有哪些選擇？",
        "什麼是 RAG，它怎麼改進 LLM 的答案？"
    ]

    print("🚀 智慧製造 AI 技術文檔助手\n")

    for query in queries:
        print(f"\n❓ 問題: {query}")
        result = rag.query(query)
        print(rag.format_result(result))


if __name__ == '__main__':
    main()
