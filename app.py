import os
import streamlit as st
import sys
import tempfile

# ============================================
# 🔐 1. 安全核心：密钥配置 (必须放在最前面)
# ============================================
# 逻辑：如果在 Streamlit Cloud 运行，从 st.secrets 读取 Key
# 如果在本地运行，你可以在这里临时写死，或者配置本地 secrets.toml
if "DEEPSEEK_API_KEY" in st.secrets:
    os.environ["DEEPSEEK_API_KEY"] = st.secrets["DEEPSEEK_API_KEY"]

# 假 Key (过安检用)
os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-check"
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"

# 去代理 (保留也没事)
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['all_proxy'] = ''
os.environ['no_proxy'] = '*'

from agents import run_crew

# ... (后面的 UI 代码保持不变) ...
st.set_page_config(page_title="简历助手", layout="wide")

# 👇👇👇 复制这段"终极隐藏代码" 👇👇👇
hide_ui_style = """
<style>
    /* 1. 隐藏右上角的"三点"菜单 (汉堡菜单) */
    #MainMenu {visibility: hidden;}

    /* 2. 隐藏顶部的工具栏 (GitHub图标, Deploy按钮, Fork按钮等) */
    [data-testid="stToolbar"] {visibility: hidden;}

    /* 3. 隐藏顶部的彩色装饰条 */
    header {visibility: hidden;}

    /* 4. 隐藏底部的 "Made with Streamlit" */
    footer {visibility: hidden;}

    /* 5. 针对某些版本的额外隐藏 (保险起见) */
    div[data-testid="stDecoration"] {visibility: hidden;}
    div[data-testid="stStatusWidget"] {visibility: hidden;}
</style>
"""
st.markdown(hide_ui_style, unsafe_allow_html=True)
# 👆👆👆 代码结束 👆👆👆

st.title("🕵️‍♂️ 简历匹配 & 岗位分析助手")

with st.sidebar:
    st.header("📝 任务中心")
    uploaded_file = st.file_uploader("上传简历 (PDF)", type="pdf")
    jd_input = st.text_area("粘贴岗位描述 (JD)", height=300)
    start_btn = st.button("开始分析 🚀", type="primary")

if start_btn:
    if not uploaded_file or not jd_input:
        st.error("请先上传简历并填写 JD！")
    else:
        with st.spinner("正在思考中..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                result = run_crew(jd_input, tmp_path)

                st.success("任务完成！")
                st.markdown("### 📋 分析报告")
                st.markdown(result)

                os.unlink(tmp_path)
            except Exception as e:
                st.error(f"发生错误: {e}")
                with st.expander("🔍 查看详细错误信息"):
                    import traceback

                    st.code(traceback.format_exc())