# -*- coding: utf-8 -*-
import os
import pdfplumber
from crewai.tools import BaseTool
from duckduckgo_search import DDGS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

# ================= 配置区 =================
# 1. 数据库路径（确保你的 chroma_db 文件夹已上传到 GitHub）
DB_PATH = "./data/chroma_db"

# 2. 云端模型名称（不再使用本地 MODEL_PATH 路径）
REMOTE_MODEL_NAME = "all-MiniLM-L6-v2"


# =========================================

# --- 1. 联网搜索工具 (外网情报站) ---
class SearchTool(BaseTool):
    name: str = "Network Search"
    description: str = "使用联网搜索获取最新的岗位面试动态、行业现状和画像。输入必须是搜索关键词。"

    def _run(self, query: str) -> str:
        try:
            enhanced_query = f"{query} 面试复盘 避雷 2026"
            with DDGS() as ddgs:
                results = list(ddgs.text(enhanced_query, max_results=3))
                if not results:
                    return "未在网上搜寻到相关实时动态。"
                return str(results)
        except Exception as e:
            return f"Search Error: {e}"


# --- 2. PDF工具 (内容解析引擎) ---
class PDFTool(BaseTool):
    name: str = "Read PDF Content"
    description: str = "读取简历PDF文件的全量内容（包含实习、项目、特长）。输入必须是文件路径。"

    def _run(self, file_path: str) -> str:
        try:
            if not os.path.exists(file_path):
                return "错误：简历文件不存在。"

            with pdfplumber.open(file_path) as pdf:
                text = ""
                for page in pdf.pages:
                    extract = page.extract_text()
                    if extract:
                        text += extract + "\n---\n"  # 加入分页标识，方便Agent结构化识别

                if not text.strip():
                    return "解析失败：该 PDF 可能是图片扫描件，无法提取文字。"
            return text
        except Exception as e:
            return f"PDF Read Error: {e}"


# --- 3. RAG知识库工具 (内网专家库 - 云端适配版) ---
class KnowledgeBaseTool(BaseTool):
    name: str = "Internal Knowledge Base"
    description: str = "查询内部专家知识库。用于获取行业核心标准、硬性门槛和面试官评分标准。"

    def _run(self, query: str) -> str:
        try:
            # 【核心改动】直接调用模型名。
            # Streamlit Cloud 会自动下载模型，省去上传几百MB文件的烦恼
            embedding_func = SentenceTransformerEmbeddings(model_name=REMOTE_MODEL_NAME)

            # 检查 GitHub 上是否已上传向量数据库文件夹
            if not os.path.exists(DB_PATH):
                return "（内部知识库文件夹未找到，已切换至实时分析模式）"

            vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embedding_func)

            # 检索精华信息
            results = vector_db.similarity_search(query, k=1)

            if not results:
                return "（内部知识库未匹配到特定案例）"

            context_str = ""
            for doc in results:
                role_name = doc.metadata.get('role', '专家基准')
                context_str += f"\n【⚠️ 内部参考标准 - {role_name}】\n{doc.page_content}\n"

            return context_str

        except Exception as e:
            return f"Knowledge Base Error: {e}"


# --- 4. 实例化工具 ---
search_tool = SearchTool()
pdf_tool = PDFTool()
rag_tool = KnowledgeBaseTool()