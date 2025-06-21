
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI  # ✅ correct
from dotenv import load_dotenv  # ✅ Import this
import os

load_dotenv() 

# Initialize Azure LLM
llm = AzureChatOpenAI(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    temperature=0
) 

prompt = PromptTemplate(
    input_variables=["text"],
    template="""
You are a document classification expert. Classify the following document into one of these categories:
- Invoice
- Resume
- Contract
- Letter
- Report
- Others

Respond only with the category name.

Document:
{text}
"""
)

classification_chain = LLMChain(llm=llm, prompt=prompt)

def classify_document(text):
    response = classification_chain.invoke({"text": text})
    print("🔍 LLM response:", response)
    return response.get("text", "Others").strip()
