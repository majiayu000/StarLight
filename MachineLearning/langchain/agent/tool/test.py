from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.utilities.dalle_image_generator import DallEAPIWrapper
import os
from langchain.chat_models import ChatOpenAI


# llm = OpenAI(api_key="",  temperature=0.9)
# prompt = PromptTemplate(
#     input_variables=["image_desc"],
#     template="Generate a detailed prompt to generate an image based on the following description: {image_desc}",
# )
# chain = LLMChain(llm=llm, prompt=prompt)

# image_url = DallEAPIWrapper(model="dall-e-3").run(chain.run("halloween night at a haunted museum"))

# print(image_url)

from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentType, initialize_agent, load_tools

llm = ChatOpenAI(temperature=0)

# tools = load_tools(["dalle-image-generator"])
# agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)
# output = agent.run("Create an image of a halloween night at a haunted museum")


# from langchain.agents import initialize_agent, load_tools

# tools = load_tools(["dalle-image-generator"])
# agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)
# output = agent.run("Create an image of a halloween night at a haunted museum")

from langchain.agents import initialize_agent, load_tools

tools = load_tools(["dalle-image-generator"])
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)
output = agent.run("Create an image of a halloween night at a haunted museum")

print(output)