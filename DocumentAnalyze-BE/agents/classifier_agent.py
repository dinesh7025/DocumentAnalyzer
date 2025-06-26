
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI  # ✅ correct
from dotenv import load_dotenv  # ✅ Import this
import os
import re

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
You are a document classification expert.

Classify the document into one of the following categories:
- Invoice
- Resume
- Contract
- Letter
- Report
- Others

Respond with two fields:
1. Category (one of the above)
2. Confidence score (a number between 0 and 1)

Format:
Category: <category>
Confidence: <score>

Document:
{text}
"""
)


classification_chain = LLMChain(llm=llm, prompt=prompt)

def classify_document(text: str) -> dict:
    response = classification_chain.invoke({"text": text})
    print("🔍 LLM raw response:", response)

    label = "others"
    confidence = 0.0

    try:
        output = response.get("text", "").strip()

        # Extract category
        label_match = re.search(r"Category:\s*(\w+)", output, re.IGNORECASE)
        if label_match:
            label = label_match.group(1).lower()

        # Extract confidence score
        conf_match = re.search(r"Confidence:\s*([0-9.]+)", output, re.IGNORECASE)
        if conf_match:
            confidence = round(float(conf_match.group(1)), 2)

    except Exception as e:
        print("⚠️ Failed to parse classification output:", e)

    return {
        "label": label,
        "confidence": confidence
    }

