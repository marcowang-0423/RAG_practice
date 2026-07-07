"""爬蟲：從網頁和 GitHub 爬取技術文檔"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime

class TechDocScraper:
    """爬取技術文檔"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.documents = []

    def scrape_markdown_from_github(self, repo_url):
        """從 GitHub repo 爬取 README 和相關文檔"""
        try:
            # 獲取 README 內容
            readme_url = repo_url.replace('github.com', 'raw.githubusercontent.com').rstrip('/') + '/main/README.md'
            resp = requests.get(readme_url, headers=self.headers, timeout=10)

            if resp.status_code == 200:
                self.documents.append({
                    'source': repo_url,
                    'type': 'github_markdown',
                    'content': resp.text,
                    'title': repo_url.split('/')[-1],
                    'timestamp': datetime.now().isoformat()
                })
                print(f"✓ 爬取成功: {repo_url}")
                return True
        except Exception as e:
            print(f"✗ 爬取失敗 {repo_url}: {e}")
        return False

    def scrape_webpage(self, url):
        """爬取網頁內容"""
        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.encoding = 'utf-8'
            soup = BeautifulSoup(resp.content, 'html.parser')

            # 移除 script 和 style
            for tag in soup(['script', 'style']):
                tag.decompose()

            text = soup.get_text(separator='\n', strip=True)

            self.documents.append({
                'source': url,
                'type': 'webpage',
                'content': text,
                'title': soup.title.string if soup.title else url,
                'timestamp': datetime.now().isoformat()
            })
            print(f"✓ 爬取成功: {url}")
            return True
        except Exception as e:
            print(f"✗ 爬取失敗 {url}: {e}")
        return False

    def save_documents(self, filepath='data/raw_documents.json'):
        """保存爬取的文檔"""
        import os
        os.makedirs('data', exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 已保存 {len(self.documents)} 份文檔到 {filepath}")

    def load_documents(self, filepath='data/raw_documents.json'):
        """載入已爬取的文檔"""
        import os
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
            print(f"✓ 已載入 {len(self.documents)} 份文檔")
            return True
        return False


def main():
    """爬取智慧製造 AI 相關文檔"""

    scraper = TechDocScraper()

    # 爬取資源清單
    urls = [
        # GitHub Awesome 列表
        'https://github.com/M-3LAB/awesome-industrial-anomaly-detection',
        'https://github.com/mala-lab/Awesome-Anomaly-Detection-Foundation-Models',
        'https://github.com/kaushikb11/awesome-llm-agents',
        'https://github.com/zli12321/Vision-Language-Models-Overview',

        # 官方文檔
        'https://docs.langchain.com/',
        'https://docs.ultralytics.com/',

        # 其他資源
        'https://www.langflow.org/',
        'https://flowiseai.com/',
    ]

    print("開始爬取技術文檔...\n")
    for url in urls:
        if 'github.com' in url:
            scraper.scrape_markdown_from_github(url)
        else:
            scraper.scrape_webpage(url)

    scraper.save_documents()
    print("\n爬蟲完成！")


if __name__ == '__main__':
    main()
