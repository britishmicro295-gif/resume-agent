import os
from crewai import Agent, Task, Crew, Process, LLM
from tools import search_tool, pdf_tool

# 再次确保环境纯净
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''
os.environ['all_proxy'] = ''
os.environ['no_proxy'] = '*'

# 假 Key (过安检)
os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-check"

# ============================================
# 🤖 模型配置：删除明文 Key！
# ============================================
my_llm = LLM(
    model="openai/deepseek-chat",
    base_url="https://api.deepseek.com",
    # 👇👇👇 重点在这里！
    # 原来是: api_key="sk-1fd64190c48c4ee5ac774b4a17ac1321"
    # 现在改成: os.environ.get(...)
    # 意思是：去环境变量里找 Key，找不到就报错（或者用后面的占位符）
    api_key=os.environ.get("DEEPSEEK_API_KEY", "sk-placeholder"),
    temperature=0,
    timeout=600
)

def run_crew(jd_text, pdf_path):
    detective = Agent(
        role='互联网岗位侦探',
        goal='挖掘JD背后的真实需求',
        backstory='你擅长使用搜索引擎挖掘互联网上的碎片信息。',
        tools=[search_tool],
        llm=my_llm,
        function_calling_llm=my_llm,
        verbose=True,
        allow_delegation=False,
    )

    coach = Agent(
        role='资深简历顾问',
        goal='给出修改建议',
        backstory='你是一个在招聘行业摸爬滚打10年的专家。',
        tools=[pdf_tool],
        llm=my_llm,
        function_calling_llm=my_llm,
        verbose=True,
        allow_delegation=False,
    )

    task_research = Task(
        description=f"分析JD: '{jd_text}'。提取核心技能，并搜索该岗位的市场行情。",
        expected_output="一份包含JD隐性需求和市场行情的简报。",
        agent=detective
    )

    task_analyze = Task(
        description=f"读取简历 '{pdf_path}'。结合简报，对简历打分，并列出3个弱点及修改建议。",
        expected_output="Markdown格式的最终简历诊断报告。",
        agent=coach,
        context=[task_research]
    )

    crew = Crew(
        agents=[detective, coach],
        tasks=[task_research, task_analyze],
        process=Process.sequential,
        verbose=True,
        memory=False,
    )

    return crew.kickoff()