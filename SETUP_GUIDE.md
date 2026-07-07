# 🛠️ 詳細設置指南

## Step 1: 獲取 OpenAI API Key

1. 訪問 [OpenAI API](https://platform.openai.com/api-keys)
2. 登錄或註冊賬戶
3. 創建新的 API Key
4. 複製 API Key

## Step 2: 環境配置

### Windows

```powershell
# 創建虛擬環境
python -m venv venv

# 啟用虛擬環境
venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 設置 API Key
$env:OPENAI_API_KEY = "your_api_key_here"

# 或編輯 .env 文件
copy .env.example .env
# 用編輯器打開 .env，填入你的 API Key
```

### macOS / Linux

```bash
# 創建虛擬環境
python3 -m venv venv

# 啟用虛擬環境
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 設置 API Key
export OPENAI_API_KEY="your_api_key_here"

# 或編輯 .env 文件
cp .env.example .env
# 編輯 .env，填入你的 API Key
```

## Step 3: 爬取文檔

```bash
# 爬取技術文檔（約 2-5 分鐘，取決於網絡速度）
python src/scraper.py
```

預期輸出：
```
開始爬取技術文檔...

✓ 爬取成功: https://github.com/M-3LAB/awesome-industrial-anomaly-detection
✓ 爬取成功: https://github.com/mala-lab/Awesome-Anomaly-Detection-Foundation-Models
...

✓ 已保存 N 份文檔到 data/raw_documents.json

爬蟲完成！
```

## Step 4: 建立向量索引

```bash
# 建立 FAISS 向量索引（約 1-3 分鐘）
python src/indexing.py
```

預期輸出：
```
正在載入原始文檔...
✓ 已載入 N 份文檔

正在分塊 N 份文檔...
✓ 分塊完成：M 個 chunks

正在初始化 OpenAI Embeddings...
正在建立向量庫...
✓ 向量庫建立完成：M 個文檔

✓ 向量庫已保存到 vector_store/smart_mfg_index

✅ 索引完成！
```

## Step 5: 啟動 Web UI

```bash
# 啟動 Streamlit 應用
streamlit run ui/app.py
```

預期輸出：
```
You can now view your Streamlit app in your browser.

  URL: http://localhost:8501
```

在瀏覽器中打開 http://localhost:8501，開始使用！

## 常見問題

### 🚨 "OpenAI API Key not found"

確保你已經：
1. 在 `.env` 文件中設置 `OPENAI_API_KEY`，或
2. 通過環境變量設置 `OPENAI_API_KEY`

```bash
# 檢查是否設置成功
echo $OPENAI_API_KEY
```

### 🚨 "找不到向量庫"

需要先運行 indexing 步驟：
```bash
python src/indexing.py
```

### 🚨 爬蟲超時

網絡連接可能不穩定，嘗試：
- 增加超時時間（編輯 `scraper.py` 的 `timeout` 參數）
- 檢查網絡連接
- 稍後重試

### 🚨 Streamlit 無法啟動

確保 streamlit 已安裝：
```bash
pip install streamlit --upgrade
```

## 性能優化

### 加快向量化速度

編輯 `src/indexing.py`：
```python
# 增加 chunk_size 可以減少 chunks 數量，但可能降低精度
indexer = DocumentIndexer(chunk_size=1000, chunk_overlap=200)
```

### 改進檢索質量

編輯 `src/retrieval.py`：
```python
# 增加 search_kwargs['k'] 返回更多相關文檔
search_kwargs={'k': 10}  # 默認是 5
```

### 支持更多 LLM

在 `src/retrieval.py` 中修改：
```python
# 使用 Claude
from langchain.chat_models import ChatAnthropic
self.llm = ChatAnthropic(model="claude-3-opus", temperature=0.2)

# 或使用開源模型
from langchain.chat_models import ChatOllama
self.llm = ChatOllama(model="llama2")
```

## 下一步

- ✅ 完成基本部署
- 📊 查看檢索質量和延遲
- 🎯 添加更多技術文檔
- 🔄 迭代改進系統
- 🚀 部署到線上服務

## 獲取幫助

遇到問題？
1. 檢查 [README.md](README.md) 的快速開始部分
2. 查看 Python 錯誤信息
3. 檢查 OpenAI API 配額和使用情況
