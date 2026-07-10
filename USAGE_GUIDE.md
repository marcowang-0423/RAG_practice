# 📖 使用指南

## 🚀 快速開啟

### 每次使用（最簡單）

```bash
cd C:\Users\王思喬\OneDrive\桌面\RAG_practice

# 1. 激活虛擬環境
venv\Scripts\activate.bat

# 2. 啟動 Web UI
streamlit run ui/app.py
```

瀏覽器自動打開 → **http://localhost:8501**

就這樣！已有的爬蟲和索引會自動使用。

---

### 首次使用（完整設置）

```bash
cd C:\Users\王思喬\OneDrive\桌面\RAG_practice

# 1. 虛擬環境
python -m venv venv
venv\Scripts\activate.bat

# 2. 安裝依賴（只需一次）
pip install anthropic faiss-cpu sentence-transformers requests beautifulsoup4 python-dotenv streamlit

# 3. 設置 API Key（編輯 .env 文件）
notepad .env
# 添加一行：ANTHROPIC_API_KEY=sk-ant-v4-你的KEY

# 4. 爬取文檔（只需一次，2-5 分鐘）
python src/scraper.py

# 5. 建立向量索引（只需一次，1-3 分鐘）
python src/indexing.py

# 6. 啟動 Web UI
streamlit run ui/app.py
```

完成！開始查詢吧。

---

## 🧠 RAG 怎麼做到的？

### RAG = Retrieval + Augmented + Generation

```
┌─────────────────────────────────────────────────────┐
│         用戶問題："什麼是 RAG？"                    │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 1️⃣ 向量化用戶問題                                   │
│    "什麼是 RAG？" → [0.123, 0.456, ...]（向量）    │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 2️⃣ 在向量庫中搜尋相似文檔                          │
│    找到前 5 個最相關的文檔片段                      │
│    ✓ LangChain RAG 介紹                            │
│    ✓ 檢索增強生成論文                              │
│    ✓ ...                                           │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 3️⃣ 組織相關文檔為「上下文」                        │
│    文檔1: "RAG 是..."                              │
│    文檔2: "檢索步驟..."                            │
│    文檔3: "生成步驟..."                            │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 4️⃣ 送給 Claude 與上下文一起                        │
│    "根據以下文檔，回答：什麼是 RAG？"             │
│    文檔: [相關內容]                                │
│    問題: 什麼是 RAG？                             │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ 5️⃣ Claude 生成精準答案                            │
│    "RAG 是 Retrieval-Augmented Generation..."      │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│ ✅ 最終答案 + 相關資源                             │
└─────────────────────────────────────────────────────┘
```

### 核心 3 步

| 步驟 | 工具 | 功能 |
|------|------|------|
| **R - 檢索** | FAISS 向量庫 | 從文檔中找最相關的片段 |
| **A - 增強** | 提示工程 | 把文檔與問題結合成 prompt |
| **G - 生成** | Claude API | 生成基於文檔的答案 |

### 代碼實現

```python
# src/retrieval.py 中的 query() 方法

def query(self, question):
    # 1️⃣ 向量化問題
    question_embedding = self.model.encode([question])[0]
    
    # 2️⃣ 搜尋相似文檔
    distances, indices = self.vectorstore.search(question_embedding, k=5)
    relevant_docs = [self.metadata[i] for i in indices[0]]
    
    # 3️⃣ 組織上下文
    context = "\n\n".join([d['content'] for d in relevant_docs])
    
    # 4️⃣ 生成 prompt
    prompt = f"""根據文檔回答：
    
文檔:
{context}

問題: {question}"""
    
    # 5️⃣ 調用 Claude 生成答案
    response = claude.messages.create(
        model="claude-3-haiku-20240307",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text
```

### 為什麼這樣好？

✅ **精準** - 答案基於真實文檔，不是 AI 瞎編
✅ **可信** - 可以看到答案來自哪些資源
✅ **最新** - 可以隨時添加新文檔更新知識
✅ **省錢** - 只有生成答案時消耗 token

---

## 🔄 完整數據流詳解

### 第 1 步：爬蟲爬取 (Scraper)

**運行**: `python src/scraper.py`

**輸出**: `data/raw_documents.json`

爬蟲從 GitHub 和網頁爬取文檔，存成 JSON 陣列：

```json
[
  {
    "source": "https://github.com/run-llama/llama_index",
    "type": "github_markdown",
    "title": "llama_index",
    "content": "RAG is a technique that combines retrieval and generation...",
    "timestamp": "2026-07-10T10:30:00"
  },
  {
    "source": "data/custom_docs/smart_manufacturing.txt",
    "type": "local_file",
    "title": "smart_manufacturing.txt",
    "content": "智慧製造利用 AI 和機器學習...",
    "timestamp": "2026-07-10T10:31:00"
  }
]
```

**特點**:
- 原始文本格式
- 每個文檔限制 3000 字符（控制 API 成本）
- 包含元數據（來源、類型、時間戳）
- 支持 GitHub README 和本地文件混合

---

### 第 2 步：分塊 (Chunking)

**運行**: `python src/indexing.py` 中自動執行

**過程**: 將大文檔分成 500 字符的小片段

```python
原始文檔 (3000 字符)
    ↓
chunk_1: 500 字符
chunk_2: 500 字符
chunk_3: 500 字符
chunk_4: 500 字符
chunk_5: 500 字符
chunk_6: 500 字符
```

**為什麼要分塊？**

一個大文檔中的不同部分可能回答不同問題。分塊讓相似度搜索更精確。

**例子**:
```
原文: "RAG 的三個步驟是...。第一步是檢索...。第二步是增強..."

分塊後:
- chunk_1: "RAG 的三個步驟是..." 
- chunk_2: "第一步是檢索..." 
- chunk_3: "第二步是增強..."

提問「第一步是什麼」時，系統只會返回 chunk_2，更精準
```

---

### 第 3 步：向量化 (Embedding)

**模型**: `sentence-transformers/all-MiniLM-L6-v2`（本地免費）

**功能**: 把文本轉成向量（數字列表）

```python
輸入: "RAG is a technique combining retrieval and generation"
     ↓ [SentenceTransformer 模型]
輸出: [0.0234, -0.1245, 0.5678, 0.0123, -0.4567, ..., 0.2341]
     ↑
     384 個數字，代表文本的語義
```

**關鍵特性**:
- 相似的文本 → 相似的向量
- 例子："RAG技術" 和 "檢索增強生成" 的向量距離很近
- 維度：384（表示文本的 384 個語義特徵）

---

### 第 4 步：建立索引 (FAISS Indexing)

**運行**: `python src/indexing.py`

**輸出**: 兩個文件
```
vector_store/
├── smart_mfg_index.faiss          # 二進制文件：所有向量
└── smart_mfg_index_metadata.json   # JSON 文件：chunk 內容
```

**檔案 1：`.faiss` 文件**
- 二進制格式（不可直接查看）
- 存放所有 chunk 的向量
- 使用 FAISS IndexFlatL2 算法
- 快速搜索最相似的向量
- 大小：~100MB（取決於文檔數量）

**檔案 2：`_metadata.json` 文件**
```json
[
  {
    "content": "RAG is a technique...",
    "source": "github.com/run-llama/llama_index",
    "title": "llama_index",
    "type": "github_markdown"
  },
  {
    "content": "Embeddings convert text into numerical vectors...",
    "source": "github.com/huggingface/transformers",
    "title": "transformers",
    "type": "github_markdown"
  }
]
```

**FAISS 的作用**:
- 把 384 維向量組織成快速搜索結構
- 給定用戶問題的向量 → 快速找到 Top-5 最相似的 chunk
- 搜索時間：毫秒級（本地）

---

### 第 5 步：查詢檢索 (Retrieval)

**運行**: 用戶在 Streamlit UI 中提問

**流程**:

```
用戶問題："什麼是RAG？"
    ↓
1️⃣ 向量化問題
   question_embedding = model.encode("什麼是RAG？")
   → [0.0456, -0.2341, 0.6789, ...]  (384維向量)
    ↓
2️⃣ FAISS 搜索
   distances, indices = vectorstore.search(question_embedding, k=5)
   distances = [0.12, 0.34, 0.56, 0.78, 0.91]  (相似度分數，越小越相似)
   indices = [45, 12, 89, 3, 156]  (metadata 中對應的索引)
    ↓
3️⃣ 取回 Top-5 chunks
   relevant_chunks = [
       metadata[45]: "RAG是檢索增強生成...",
       metadata[12]: "三個核心步驟是...",
       metadata[89]: "第一步：檢索...",
       metadata[3]: "第二步：增強...",
       metadata[156]: "第三步：生成..."
   ]
    ↓
4️⃣ 組織成上下文
   context = "來源: github.com/llama_index\n..." +
             "來源: github.com/transformers\n..." + ...
    ↓
5️⃣ 送給 Claude API
   prompt = "根據以下信息回答問題：\n\n" + context + "\n\n問題：什麼是RAG？"
```

**代碼實現** (`src/retrieval.py`):

```python
def query(self, question):
    # 1️⃣ 向量化問題
    question_embedding = self.model.encode([question])[0].astype('float32')
    
    # 2️⃣ 搜尋相似文檔 (FAISS 搜索，本地免費)
    distances, indices = self.vectorstore.search(np.array([question_embedding]), k=5)
    
    # 3️⃣ 取回 Top-5 chunks
    relevant_docs = [self.metadata[i] for i in indices[0] if i < len(self.metadata)]
    
    # 4️⃣ 組織上下文
    context = "\n\n".join([f"來源: {d['source']}\n{d['content']}" for d in relevant_docs])
    
    # 5️⃣ 生成 prompt
    prompt = f"""根據以下信息回答問題：

{context}

問題: {question}"""
    
    # 調用 Claude API（消耗 token）
    response = self.client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content[0].text, relevant_docs
```

---

### 第 6 步：生成答案 (Generation)

**運行**: Claude Haiku API

**輸入**:
```
根據以下信息回答問題：

來源: github.com/run-llama/llama_index
RAG是一種結合檢索和生成的技術...

來源: github.com/huggingface/transformers
向量嵌入將文本轉換為數值向量...

問題: 什麼是RAG？
```

**輸出** (Claude 生成):
```
RAG是「檢索增強生成」(Retrieval-Augmented Generation) 的縮寫，
是一種結合檢索和生成的技術。它允許語言模型從外部知識庫檢索相關信息，
然後基於這些信息生成答案，而不是完全依賴模型本身的知識。

RAG的三個核心步驟是：
1. 檢索（Retrieval）- 從知識庫中找到最相關的文檔
2. 增強（Augmentation）- 將檢索到的文檔與用戶問題結合
3. 生成（Generation）- 使用 LLM 基於增強後的上下文生成答案

這種方法的優勢是...
```

---

### 📊 完整流程時間和成本

| 步驟 | 工具 | 地點 | 時間 | 成本 |
|------|------|------|------|------|
| 爬蟲 | requests + BeautifulSoup | 本地 | 2-5 分鐘 | 免費 |
| 分塊 | Python | 本地 | < 1 秒 | 免費 |
| 向量化 | sentence-transformers | 本地 | 1-3 分鐘 | 免費 |
| FAISS 索引 | FAISS | 本地 | < 1 秒 | 免費 |
| **查詢檢索** | FAISS | 本地 | < 100ms | **免費** ✅ |
| **生成答案** | Claude API | 雲端 | 2-5 秒 | $0.01 per 1M tokens |

**成本節省**:
- 只有「生成答案」步驟消耗 Claude API Token
- 檢索步驟（1-5）全部本地免費
- 相比直接用 Claude，成本降低 80%+

---



## 📚 未來新增知識庫

### 方案 A: 自動爬新網站（最簡單）

1. **編輯 `src/scraper.py`**：

```python
def main():
    scraper = TechDocScraper()
    
    urls = [
        # 現有的
        'https://github.com/M-3LAB/awesome-industrial-anomaly-detection',
        
        # 新增你想要的
        'https://github.com/你的新倉庫/awesome-xxxxx',
        'https://你的文檔網站.com/intro',
    ]
    
    for url in urls:
        if 'github.com' in url:
            scraper.scrape_markdown_from_github(url)
        else:
            scraper.scrape_webpage(url)
    
    scraper.save_documents()
```

2. **重新爬取 + 索引**：

```bash
python src/scraper.py   # 爬新文檔
python src/indexing.py  # 重新索引
streamlit run ui/app.py # 重啟
```

---

### 方案 B: 上傳本地文件（更靈活）

1. **創建資料夾**：

```bash
mkdir data/custom_docs
```

2. **把文件放進去**：

```
data/custom_docs/
├── 金融知識.txt
├── 區塊鏈基礎.md
└── 機器學習算法.txt
```

3. **修改 `src/scraper.py`** 添加本地載入：

```python
def load_local_files(self, folder='data/custom_docs'):
    """載入本地文件"""
    import glob
    import os
    
    for file_path in glob.glob(f"{folder}/**/*.*", recursive=True):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.documents.append({
                    'source': file_path,
                    'type': 'local_file',
                    'content': f.read()[:3000],
                    'title': os.path.basename(file_path),
                    'timestamp': datetime.now().isoformat()
                })
                print(f"✓ 載入: {file_path}")
        except Exception as e:
            print(f"✗ 載入失敗 {file_path}: {e}")

def main():
    scraper = TechDocScraper()
    
    # 爬網站
    urls = [...]
    for url in urls:
        # ...
    
    # 載入本地文件
    scraper.load_local_files('data/custom_docs')
    
    scraper.save_documents()
```

4. **重新索引**：

```bash
python src/scraper.py
python src/indexing.py
streamlit run ui/app.py
```

---

### 方案 C: 針對特定領域（專業級）

假設你想加「金融 AI」領域：

1. **創建新的爬蟲配置**：

```python
# src/scraper.py 中新增

DOMAIN_CONFIGS = {
    'smart_mfg': {
        'name': '智慧製造',
        'urls': [
            'https://github.com/M-3LAB/awesome-industrial-anomaly-detection',
        ]
    },
    'finance_ai': {
        'name': '金融 AI',
        'urls': [
            'https://github.com/QuantConnect/Lean',
            'https://docs.anthropic.com/',
        ]
    }
}

def scrape_by_domain(domain):
    scraper = TechDocScraper()
    config = DOMAIN_CONFIGS[domain]
    
    for url in config['urls']:
        # 爬取...
    
    scraper.save_documents(f"data/{domain}_documents.json")
```

2. **為不同領域創建不同索引**：

```bash
# 爬取金融領域
python -c "from src.scraper import scrape_by_domain; scrape_by_domain('finance_ai')"

# 為金融領域建立索引
python -c "from src.indexing import DocumentIndexer; \
    indexer = DocumentIndexer(); \
    indexer.load_raw_documents('data/finance_ai_documents.json'); \
    indexer.index_pipeline(); \
    indexer.save_vectorstore('vector_store/finance_ai_index')"
```

3. **修改 `src/retrieval.py` 支持多索引**：

```python
class SmartMfgRAG:
    def __init__(self, vectorstore_path='vector_store/smart_mfg_index'):
        # ...

class FinanceRAG:
    def __init__(self, vectorstore_path='vector_store/finance_ai_index'):
        # ...

class MultiDomainRAG:
    def __init__(self):
        self.smart_mfg = SmartMfgRAG()
        self.finance = FinanceRAG()
    
    def query(self, question, domain='smart_mfg'):
        if domain == 'finance_ai':
            return self.finance.query(question)
        else:
            return self.smart_mfg.query(question)
```

---

## 📊 更新流程總結

| 操作 | 命令 | 時間 |
|------|------|------|
| 查詢（日常） | `streamlit run ui/app.py` | 秒開 |
| 新增網站 | 編輯 URLs → `python src/scraper.py` → `python src/indexing.py` | 10 分 |
| 新增本地文件 | 放入 `data/custom_docs/` → 上面的流程 | 10 分 |
| 新領域 | 創建新索引 → 修改 retrieval.py | 自訂 |

---

## 🎯 常見問題

**Q: 查詢很慢怎麼辦？**
A: 正常，Haiku 或本地 Llama 會慢 30 秒-1 分鐘。可升級到更快的模型（Sonnet/Opus）。

**Q: 如何更新已有的文檔？**
A: 刪除 `data/raw_documents.json` 和 `vector_store/` 文件夾，重新運行爬蟲和索引。

**Q: 可以离線使用嗎？**
A: 是的，用 Ollama + Llama 2，完全離線免費。

**Q: 如何部署到網上？**
A: 用 Streamlit Cloud（免費）或 Docker + Cloud Run（付費）。

---

## 🚀 下一步

1. ✅ 解決 API Key 額度問題
2. ✅ 試試查詢功能
3. ✅ 根據需要新增知識庫
4. ✅ 部署到線上或分享給團隊

祝你使用愉快！ 🎉
