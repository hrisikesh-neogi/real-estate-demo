from src.tools import (sql_agent_tool,
                       generate_lease_agreement_tool,
                       send_email_tool)

from src.prompts import SYSTEM_PROMPT
from src.constants.llm import llm 

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory


memory = ConversationBufferMemory(memory_key="chat_history",
                                  return_messages=True)


class RealEstateAgent:
    
    def __init__(self):
        pass
    
    
    def get_prompt(self):
        prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
        
        return prompt
    
    def build_agent(self)-> AgentExecutor:
        
        prompt = self.get_prompt()
        
        tools = [sql_agent_tool,
                 generate_lease_agreement_tool,
                 send_email_tool]
        
        
        agent = create_tool_calling_agent(llm, 
                                          tools, 
                                          prompt)
        
        agent_executor = AgentExecutor(
            agent=agent, 
            tools=tools,
            verbose=False,
            memory=memory  # You might want to add memory here
        )
        
        return agent_executor