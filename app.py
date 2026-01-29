import os
import streamlit as st
import tempfile
import traceback
from agents import run_crew
from tools import rag_tool, search_tool

# ============================================
# ⚙️ 1. 环境与页面配置
# ============================================
os.environ['HTTP_PROXY'] = ""
os.environ['HTTPS_PROXY'] = ""
os.environ['ALL_PROXY'] = ""

st.set_page_config(
    page_title="职场陪跑教练 · 全量经历诊断",
    layout="wide",
    page_icon="🎯"
)

# 自定义 UI 样式
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { 
        width: 100%; border-radius: 8px; height: 3.5em; 
        background-color: #FF4B4B; color: white; font-weight: bold; border: none;
    }
    .report-container { 
        padding: 25px; border-radius: 12px; background-color: white; 
        border: 1px solid #e0e6ed; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        line-height: 1.6; color: #333;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================
# 🛰️ 2. 侧边栏：输入区域
# ============================================
with st.sidebar:
    st.header("🎯 准备材料")
    uploaded_file = st.file_uploader("1. 把你的简历丢进来（PDF）", type="pdf")
    jd_input = st.text_area(
        "2. 粘贴你想投的岗位 JD",
        height=350,
        placeholder="把完整的招聘信息粘进来，我会按这个岗位来帮你审简历"
    )
    start_btn = st.button("开始帮我体检简历 🚀")

# ============================================
# 🛠️ 3. 主页面：逻辑执行
# ============================================
st.title("🎯 简历 & 面试搭子")

if start_btn:
    if not uploaded_file or not jd_input:
        st.error("⚠️ 还差一步：请先上传简历，再粘岗位 JD")
    else:
        with st.status("🤖 正在帮你拆解简历和岗位...", expanded=True) as status:
            try:
                status.write("📂 正在逐页查看你的简历结构...")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                status.write("🧠 正在对照行业标准看看你差在哪...")
                internal_standards = rag_tool._run(jd_input[:100])

                status.write("🌐 在帮你查这个岗位最近都在重点面什么...")
                market_info = search_tool._run(f"{jd_input[:15]} 岗位核心职责")

                status.write("🕵️‍♂️ 正在用面试官视角审你的经历（实习、项目、特长都会看）...")

                context_data = (
                    f"【目标岗位JD】: {jd_input} \n"
                    f"【行业参考标准】: {internal_standards} \n"
                    f"【近期市场信息】: {market_info}"
                )

                # 🔥【核心修复位置】🔥
                crew_output = run_crew(context_data, tmp_path)
                final_report_text = str(crew_output.raw)

                status.update(label="✅ 好了，我已经帮你看完了", state="complete", expanded=False)
                st.balloons()

                # --- 4. 报告展示区域 ---
                st.divider()
                st.subheader("📋 简历 & 面试诊断报告")

                st.markdown(f'<div class="report-container">', unsafe_allow_html=True)
                st.markdown(final_report_text)
                st.markdown('</div>', unsafe_allow_html=True)

                st.download_button(
                    label="保存这份诊断报告",
                    data=final_report_text,
                    file_name="Career_Report.md",
                    mime="text/markdown"
                )

                os.unlink(tmp_path)

            except Exception as e:
                status.update(label="❌ 中途出了一点问题", state="error")
                st.error(f"分析过程中遇到异常：{str(e)}")
                st.code(traceback.format_exc())
