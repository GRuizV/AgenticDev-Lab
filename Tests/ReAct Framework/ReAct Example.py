from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain.tools.serpapi.tool import SerpAPIWrapper
from langchain_together import Together
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure TogetherAI model
llm = Together(
    model="mistralai/Mistral-7B-Instruct-v0.1",
    together_api_key=os.getenv("TOGETHER_API_KEY"),
    temperature=0.0,
    max_tokens=512
)

# Create SerpAPI search tool
search = SerpAPIWrapper()
tools = [
    Tool(
        name="Search",
        func=search.run,
        description="Useful for answering questions about current events or factual lookups"
    )
]

# Initialize agent with ReAct loop
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Run the ReAct agent
question = "How many kids do the band members of Metallica have?"
response = agent.run(question)
print(f"\n🟢 Final Answer: {response}")