from langchain_groq import ChatGroq
from config import GROQ_API_KEY,GROQ_MODEL
from prompts import SYSTEM_PROMPT

model = ChatGroq(
    model=GROQ_MODEL,
    api_key=GROQ_API_KEY,
    temperature=0
)

def ai_response(messages:list,tools:list=None):
    try:
        if tools:
            llm_with_tool = model.bind_tools(tools)
        else:
            llm_with_tool = model
        
        if not messages or messages[0].get("role") != "system":
            messages.insert(0,{"role":"system","content":SYSTEM_PROMPT})
        
        response =  llm_with_tool.invoke(messages)
        return response
    except Exception as e:
        return f"error occur while calling llm:{e}"