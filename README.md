# 🏭 智慧製造 AI 技術文檔助手

一個基於 RAG (Retrieval-Augmented Generation) 的智慧助手，專門用於查詢和理解智慧製造、工業自動化和生成式 AI 的技術知識。

## 🎯 項目特色

- **RAG 架構**: 結合向量檢索和生成式 AI，提供精準的答案
- **多源文檔**: 整合 LangChain、YOLO、MLOps、AI Agent 等多個領域的技術文檔
- **易用界面**: Streamlit Web UI，支持預設查詢和自定義提問
- **快速上手**: 一鍵部署，無需複雜配置

## 📋 涵蓋的技術方向

| 類別 | 內容 |
|------|------|
| **瑕疵檢測** | 工業異常檢測、深度學習方法、圖像分類 |
| **流程優化** | MLOps、模型部署、Kubernetes、Data Drift |
| **視覺 AI** | YOLO、物體檢測 (YOLO26)、實例分割 |
| **AI Agent** | MetaGPT、多代理框架、自動化工作流 |
| **生成式 AI** | LLM、VLM、RAG、提示工程 |
| **音頻 AI** | 異常檢測、ASR、TTS |

## 🚀 快速開始

### 前置條件

- Python 3.10+
- OpenAI API Key (或 Claude API Key)

### 安裝步驟

1. **克隆或進入項目目錄**
```bash
cd RAG_practice
```

2. **創建虛擬環境**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **安裝依賴**
```bash
pip install -r requirements.txt
```

4. **配置 API Key**
```bash
cp .env.example .env
# 編輯 .env，填入你的 OpenAI API Key
export OPENAI_API_KEY=your_api_key_here
```

### 使用流程

#### 方式 1: 爬蟲 + 索引 + 查詢 (完整流程)

```bash
# Step 1: 爬取技術文檔
python src/scraper.py

# Step 2: 建立向量索引
python src/indexing.py

# Step 3: 啟動 Web UI
streamlit run ui/app.py
```

#### 方式 2: 直接 CLI 查詢

```bash
python src/retrieval.py
```

## 📁 項目結構

```
RAG_practice/
├── src/
│   ├── scraper.py          # 網頁爬蟲，爬取技術文檔
│   ├── indexing.py         # 向量化和索引建立
│   └── retrieval.py        # RAG 查詢引擎
├── ui/
│   └── app.py              # Streamlit Web UI
├── data/
│   └── raw_documents.json  # 爬取的原始文檔
├── vector_store/           # FAISS 向量庫 (運行後生成)
├── requirements.txt        # Python 依賴
├── .env.example            # API Key 模板
└── README.md              # 本文件
```

## 🔧 技術棧

| 組件 | 技術 | 用途 |
|------|------|------|
| **爬蟲** | requests, BeautifulSoup | 爬取網頁和 GitHub 文檔 |
| **向量化** | OpenAI Embeddings | 文本→向量轉換 |
| **向量庫** | FAISS | 高效向量檢索 |
| **LLM** | GPT-4 Turbo | 生成式 AI 回答 |
| **RAG 框架** | LangChain | 串聯各個組件 |
| **UI** | Streamlit | 交互式 Web 界面 |

## 🎓 學習點

此項目展示：

1. **RAG 系統設計** - 檢索 + 生成的完整流程
2. **向量數據庫** - FAISS 的使用和優化
3. **工程最佳實踐** - 模塊化設計、易於擴展
4. **LangChain 應用** - 從文檔加載到查詢鏈的實現
5. **Web UI 開發** - Streamlit 快速原型開發

## 📈 可擴展方向

- [ ] 支持更多數據源 (PDF、本地文件、數據庫)
- [ ] 添加多語言支持
- [ ] 實現緩存機制加速檢索
- [ ] 支持自定義文檔上傳
- [ ] 添加反饋機制改進模型
- [ ] 部署到雲端 (Google Cloud Run、AWS Lambda)
- [ ] 集成其他 LLM (Claude、Llama 2)

## 🤝 貢獻

歡迎提出建議和改進！

## 📞 聯絡方式

Email: m0983557762@gmail.com

## 📄 License

MIT License
