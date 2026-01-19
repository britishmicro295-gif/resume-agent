import pdfplumber
from crewai.tools import BaseTool
from duckduckgo_search import DDGS

# --- 1. 搜索工具 (原生 Class 写法，最稳健) ---
class SearchTool(BaseTool):
    name: str = "Network Search"
    description: str = "使用 DuckDuckGo 联网搜索。输入必须是搜索关键词字符串。"

    def _run(self, query: str) -> str:
        try:
            # 限制返回结果数量为 5 条，防止内容过多
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5))
                return str(results)
        except Exception as e:
            return f"Search Error: {e}"

# --- 2. PDF工具 (原生 Class 写法) ---
class PDFTool(BaseTool):
    name: str = "Read PDF Content"
    description: str = "读取本地PDF文件内容。输入必须是文件路径。"

    def _run(self, file_path: str) -> str:
        try:
            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    extract = page.extract_text()
                    if extract:
                        text += extract + "\n"
            return text
        except Exception as e:
            return f"Error reading PDF: {e}"

# --- 3. 实例化工具 ---
# 这样 agents.py 导入的就是已经准备好的对象
search_tool = SearchTool()
pdf_tool = PDFTool()