import os
from crewai import Agent, Task, Crew, Process, LLM
from tools import search_tool, pdf_tool

# ============================================
# 🤖 1. 模型配置
# ============================================
os.environ["OPENAI_API_KEY"] = "sk-dummy-key"
os.environ['HTTP_PROXY'] = ""
os.environ['HTTPS_PROXY'] = ""
os.environ['ALL_PROXY'] = ""

my_llm = LLM(
    model="openai/deepseek-chat",
    base_url="https://api.deepseek.com",
    api_key=os.environ.get("DEEPSEEK_API_KEY", "sk-placeholder"),
    temperature=0.2,
    timeout=600
)

# ============================================
# 🚀 2. 核心函数定义
# ============================================
def run_crew(augmented_input, pdf_path):
    # --- Agent 定义 ---
    market_expert = Agent(
        role='互联网岗位画像专家',
        goal='深度还原岗位真实需求，定义该岗位的“能力证据链”标准',
        backstory='你擅长从JD中反推面试官的考核心理，能准确描述出从业者在工作场景中的核心KPI与日常任务。',
        tools=[search_tool],
        llm=my_llm,
        verbose=True
    )

    resume_critic = Agent(
        role='大厂资深面试官 (全量审计版)',
        goal='对简历进行地毯式扫描，确保每一段实习、项目、甚至个人爱好都被转化为岗位战斗力',
        backstory='你是一个极其细致的审计者。你认为简历上没有废话，只有还没被挖掘出价值的宝藏。你擅长将跨领域的经历转化为硬核职业能力。',
        tools=[pdf_tool],
        llm=my_llm,
        verbose=True
    )

    # --- 任务 1：岗位灵魂剖析 ---
    task_market = Task(
        description=(
            f"基于以下背景信息：\n{augmented_input}\n"
            "1. 【岗位翻译】：用大白话翻译该岗位的核心KPI。面试官最担心的风险点是什么？\n"
            "2. 【工作全景图】：详细描述该岗位的日常。请按'30%时间做XX，40%时间做YY'的格式细化具体工作任务。\n"
            "3. 【ATS关键词】：提取5个在该领域必须出现的专业关键词。"
        ),
        expected_output="包含岗位KPI、日常工作流和关键词的画像报告。",
        agent=market_expert
    )

    # --- 任务 2：全量审计与面试闭环（通用逻辑版） ---
    task_resume = Task(
        description=(
            f"读取路径为 {pdf_path} 的简历。请执行地毯式审计，严格按照以下五个板块输出报告：\n\n"
            "### 🌟 板块一：岗位“灵魂”拆解\n"
            "整合任务1的结论，说明该岗位每天具体在干嘛。\n\n"
            "### 🔍 板块二：全量经历逻辑链审计\n"
            "**强制要求：必须扫描并审计简历中出现的所有模块，严禁漏项。**\n"
            "1. 【职业经历审计】：对所有实习或工作经历进行‘能力体现-思维跨越-价值体现’的逻辑拆解，并指出逻辑断裂点。\n"
            "2. 【项目经历审计】：分析简历中提到的所有项目。评价其技术栈应用、工程落地能力及解决实际问题的价值。\n"
            "3. 【长尾价值审计】：分析简历中的‘个人作品’、‘社会实践’、‘兴趣特长’或‘获奖感言’。挖掘其背后隐藏的软素质（如沟通力、领导力、网感），并将其转化为职业证据。\n\n"
            "### 💎 板块三：核心能力迁移总结\n"
            "**跨维度总结：** 综合用户上述所有经历，提炼出适配目标岗位的【3项底层迁移能力】。要讲清楚这些能力是如何从过去的不同场景迁移到当前目标岗位的。\n\n"
            "### 📝 板块四：简历像素级重构（对比表）\n"
            "选取简历中最具代表性的1-2段经历，给出‘低阶写法’ vs ‘大厂高阶写法’的对比表格。\n\n"
            "### 🚀 板块五：面试预判与备战 Todo\n"
            "根据简历中的细节（尤其是项目细节和个人特质），预判3个面试官最可能追问的难点，并给出具体的面试备战行动建议。"
        ),
        expected_output="一份覆盖简历全量信息（含实习、项目、特长等）的深度 Markdown 报告，内容需根据用户实际简历动态生成。",
        agent=resume_critic,
        context=[task_market]
    )

    # --- 组建团队并启动 ---
    crew = Crew(
        agents=[market_expert, resume_critic],
        tasks=[task_market, task_resume],
        process=Process.sequential,
        verbose=True
    )

    return crew.kickoff()