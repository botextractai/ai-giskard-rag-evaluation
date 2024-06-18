import os
import pandas as pd
import warnings
from giskard.llm import set_llm_api, set_default_client
from giskard.llm.client.openai import OpenAIClient
from giskard.rag import KnowledgeBase, generate_testset, evaluate
from llama_index.core import VectorStoreIndex
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.node_parser import SentenceSplitter
from llama_index.readers.file import PyMuPDFReader

os.environ['OPENAI_API_KEY'] = "REPLACE_THIS_WITH_YOUR_OPENAI_API_KEY"

pd.set_option("display.max_colwidth", 400)
warnings.filterwarnings('ignore')

# Set the LLM provider and model
set_llm_api("openai")
oc = OpenAIClient(model="gpt-4-turbo")
set_default_client(oc)

# STEP 1 - Build a RAG agent on the IPCC report
# =============================================

loader = PyMuPDFReader()
ipcc_documents = loader.load(file_path="./ipcc_report.pdf")

splitter = SentenceSplitter(chunk_size=512)
index = VectorStoreIndex.from_documents(ipcc_documents, transformations=[splitter])
chat_engine = index.as_chat_engine()

# Test the agent (not required, just checking)
print(chat_engine.chat("How much will the global temperature rise by 2100?"))

# STEP 2 - Generate a test set for the IPCC report
# ================================================

text_nodes = splitter(ipcc_documents)
knowledge_base_df = pd.DataFrame([node.text for node in text_nodes], columns=["text"])
knowledge_base = KnowledgeBase(knowledge_base_df)

testset = generate_testset(knowledge_base,
                           num_questions=12,
                           agent_description="A chatbot answering questions about the IPCC report")

# Save the generated test set
testset.save("ipcc_testset.jsonl")

# STEP 3 - Evaluate and diagnose the agent
# ========================================

def answer_fn(question, history=None):
    if history:
        answer = chat_engine.chat(question, chat_history=[ChatMessage(role=MessageRole.USER if msg["role"] =="user" else MessageRole.ASSISTANT,
                                                          content=msg["content"]) for msg in history])
    else:
        answer = chat_engine.chat(question, chat_history=[])
    return str(answer)

report = evaluate(answer_fn,
                testset=testset,
                knowledge_base=knowledge_base)

# Save the evaluation report
report.to_html("ipcc_evaluation_report.html")
