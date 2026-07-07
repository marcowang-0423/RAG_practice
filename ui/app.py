"""Streamlit UI - 智慧製造 AI 技術文檔助手"""

import streamlit as st
import sys
import os

# 添加 src 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.retrieval import SmartMfgRAG

st.set_page_config(
    page_title="智慧製造 AI 文檔助手",
    page_icon="🏭",
    layout="wide"
)

# 標題和說明
st.title("🏭 智慧製造 AI 技術文檔助手")
st.markdown("""
這是一個 RAG (Retrieval-Augmented Generation) 應用，可以幫助你快速查詢和理解：
- **瑕疵檢測** - 工業異常檢測技術
- **流程優化** - MLOps 和模型部署
- **視覺 AI** - YOLO、物體檢測、實例分割
- **AI Agent** - 多代理框架和自動化工作流
- **生成式 AI** - LLM、VLM、RAG 等前沿技術
""")

# 初始化 RAG 系統
@st.cache_resource
def load_rag():
    try:
        return SmartMfgRAG()
    except FileNotFoundError as e:
        st.error(f"❌ 系統初始化失敗：{str(e)}")
        st.info("請先執行以下命令：")
        st.code("pip install -r requirements.txt", language="bash")
        st.code("python src/scraper.py", language="bash")
        st.code("python src/indexing.py", language="bash")
        return None

rag = load_rag()

if rag:
    # 側邊欄 - 預設查詢
    st.sidebar.header("📋 預設查詢")
    example_queries = [
        "瑕疵檢測有哪些常見的深度學習方法？",
        "如何使用 YOLO 進行工業品質檢測？",
        "在 Kubernetes 上部署機器學習模型有什麼最佳實踐？",
        "AI Agent 框架有哪些選擇？",
        "什麼是 RAG，它怎麼改進 LLM 的答案？",
        "Vision Language Model (VLM) 有什麼應用？",
        "如何監測和檢測數據漂移？",
        "音頻異常檢測的原理是什麼？",
    ]

    selected_example = st.sidebar.selectbox(
        "選擇一個預設查詢：",
        example_queries,
        index=None
    )

    # 主區域 - 查詢輸入
    st.header("🔍 提出你的問題")
    col1, col2 = st.columns([4, 1])

    with col1:
        user_query = st.text_input(
            "輸入你的問題：",
            value=selected_example or "",
            placeholder="例如：瑕疵檢測有哪些方法？"
        )

    with col2:
        search_button = st.button("🔎 搜尋", use_container_width=True)

    # 執行查詢
    if search_button and user_query:
        with st.spinner("🤔 思考中..."):
            result = rag.query(user_query)

        # 顯示結果
        st.header("💡 答案")
        st.write(result['answer'])

        # 顯示參考資源
        if result['sources']:
            st.header("📚 參考資源")
            for i, doc in enumerate(result['sources'], 1):
                with st.expander(f"📖 {doc.metadata.get('title', 'Unknown')} - 相關片段 {i}"):
                    st.code(doc.page_content, language="markdown")
                    st.caption(f"來源: {doc.metadata.get('source', 'Unknown')}")
        else:
            st.info("ℹ️ 未找到相關參考資源")

    # 底部 - 說明和快速開始
    st.divider()
    st.subheader("📖 快速開始")

    with st.expander("ℹ️ 如何使用這個應用？"):
        st.markdown("""
        1. 在上方输入框中輸入你的問題
        2. 点击 "🔎 搜尋" 按钮
        3. 系统会从相关文档中检索信息
        4. 生成式 AI 会基于这些信息生成答案
        5. 查看参考资源了解更多细节

        **範例問題：**
        - 什麼是 RAG？
        - YOLO 怎麼訓練？
        - MLOps 最佳實踐是什麼？
        """)

    with st.expander("🛠️ 技術棧"):
        st.markdown("""
        - **向量化**: OpenAI Embeddings
        - **向量庫**: FAISS (本地)
        - **LLM**: GPT-4 Turbo
        - **框架**: LangChain
        - **UI**: Streamlit
        """)

    with st.expander("📚 涵蓋的技術方向"):
        st.markdown("""
        - **瑕疵檢測** - 工業異常檢測、深度學習方法
        - **MLOps** - 模型部署、監測、Data Drift
        - **視覺 AI** - YOLO、物體檢測、實例分割
        - **AI Agent** - 多代理框架、自動化工作流
        - **生成式 AI** - LLM、VLM、RAG、提示工程
        - **音頻 AI** - 異常檢測、ASR、TTS
        """)

else:
    st.error("❌ 無法初始化系統，請查看上方的設置說明")
