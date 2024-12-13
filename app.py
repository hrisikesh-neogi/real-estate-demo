import chainlit as cl
from src.agents import RealEstateAgent  # Import your RealEstateAgent class
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.runnables import RunnableConfig


# Initialize the RealEstateAgent
agent_builder = RealEstateAgent()
agent = agent_builder.build_agent()

@cl.on_chat_start
async def on_chat_start():
    """Set the agent at the start of the chat"""
    # Store the agent in the user session for future use
    cl.user_session.set("agent", agent)

@cl.on_message
async def on_message(message: cl.Message):
    """Handles incoming messages and streams responses from the agent"""
    
    # Retrieve the agent from the session
    agent = cl.user_session.get("agent")
    
    # # Create a new message that will hold the streamed response
    # msg = cl.Message(content="")  # Empty message to hold streamed tokens
    

    # response = agent.invoke(
    #     {"input": message.content},
    #     config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    # )
    
    # msg.content = response["output"]

    # await msg.send()

    
    response = await agent.ainvoke(
        {"input": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    )
    
    await cl.Message(response["output"]).send()
