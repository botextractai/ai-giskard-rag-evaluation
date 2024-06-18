# Giskard automated Retrieval-Augmented Generation (RAG) answer evaluation

Giskard is an evaluation and testing framework for Large Language Models (LLMs). It is an open source Python library that automatically detects performance, bias and security issues in Artificial Intelligence (AI) applications. Giskard also covers LLM-based applications such as RAG agents.

## RAG Evaluation Toolkit (RAGET): Automatically generate evaluation datasets & evaluate RAG application answers

Waiting to collect data from production to evaluate RAG agents extensively is a risky business. But building an in-house evaluation dataset is a painful task that requires manual curation and review.

Luckily, for testing RAG applications, Giskard's RAG Evaluation Toolkit (RAGET) can automatically generate a list of "question", "reference_answer" and "reference_context" from the knowledge base of the RAG. This generated test set can then be used to evaluate the RAG agent.

RAGET computes scores for each component of the RAG agent. The scores are computed by aggregating the correctness of the agent's answers on different question types.

This is the list of the components evaluated by RAGET:

| Component        | Usage                                                                                                |
| ---------------- | ---------------------------------------------------------------------------------------------------- |
| `Generator`      | The LLM used inside the RAG to generate the answers                                                  |
| `Retriever`      | Fetch relevant documents from the knowledge base according to a user query                           |
| `Rewriter`       | Rewrite the user query to make it more relevant to the knowledge base or to account for chat history |
| `Router`         | Filter the query of the user based on intentions                                                     |
| `Knowledge Base` | The set of documents given to the RAG to generate the answers                                        |

![alt text](https://github.com/botextractai/ai-giskard-rag-evaluation/assets/159737833/a7758353-593d-4bbe-bba4-c97482cd3030 "RAG workflow")

This example first builds a LlamaIndex agent that answers questions about climate change, based on the document `ipcc_report.pdf`, the "Climate Change Synthesis Report" by the Intergovernmental Panel on Climate Change (IPCC).

It then creates a knowledge base from a pandas DataFrame. This knowledge base is used to generate a test set called `ipcc_testset.jsonl`

The test set is then used to evaluate and diagnose the agent. It creates a web page (HTML) report called `ipcc_evaluation_report.html`

Please make sure you use a Python version that is officially supported by Giskard, or this example might fail.

The test set generation can take several minutes and might be expensive, depending on your LLM provider and model (this example uses OpenAI's "gpt-4-turbo" as default). To keep costs low, this example therefore uses only 12 questions (which would be insufficient for production use). If you want to generate an evaluation report with a larger data set of 120 questions, then you can do this:

1. Add this import: `from giskard.rag import QATestset`
2. In step 2, delete or comment out: `testset = generate_testset(...)`
3. In step 2, delete or comment out: `testset.save("ipcc_testset.jsonl")`
4. Add this before step 3: `testset = QATestset.load("demo_ipcc_testset.jsonl")`

You need an OpenAI API key for this example. [Get your OpenAI API key here](https://platform.openai.com/login). You can insert your OpenAI API key in the `main.py` script, or you can supply your OpenAI API key either via the `.env` file, or through an environment variable called `OPENAI_API_KEY`.

### Example Report

![alt text](https://github.com/botextractai/ai-giskard-rag-evaluation/assets/159737833/eefb05cb-ff20-41de-add4-88a7e6f3e351 "RAGET report")

### RAGET question types

By default, RAGET automatically generates 6 different question types (these can be selected if needed). The total number of questions is divided equally between each question type. For this reason, it is best to set the number of questions (`num_questions` in the `main.py` script) of the test set to multiples of 6 (this example uses 12 questions by default).

Each question type assesses a few RAG components. This makes it possible to localise weaknesses in the RAG agent and give feedback to the developers.

| Question type      | Description                                                                                                                                           | Example                                                                                                                         | Targeted RAG components              |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| **Simple**         | Simple questions generated from an excerpt of the knowledge base                                                                                      | _How much will the global temperature rise by 2100?_                                                                            | `Generator`, `Retriever`             |
| **Complex**        | Questions made more complex by paraphrasing                                                                                                           | _How much will the temperature rise in a century?_                                                                              | `Generator`                          |
| **Distracting**    | Questions made to confuse the retrieval part of the RAG with a distracting element from the knowledge base but irrelevant to the question             | _Renewable energy are cheaper but how much will the global temperature rise by 2100?_                                           | `Generator`, `Retriever`, `Rewriter` |
| **Situational**    | Questions including user context to evaluate the ability of the generation to produce relevant answer according to the context                        | _I want to take personal actions to reduce my carbon footprint and I wonder how much will the global temperature rise by 2100?_ | `Generator`                          |
| **Double**         | Questions with two distinct parts to evaluate the capabilities of the query rewriter of the RAG                                                       | _How much will the global temperature rise by 2100 and what is the main source of Greenhouse Gases?_                            | `Generator`, `Rewriter`              |
| **Conversational** | Questions made as part of a conversation, first message describe the context of the question that is ask in the last message, also tests the rewriter | _I want to know more about the global temperature evolution by 2100. How high will it be?_                                      | `Rewriter`, `Routing`                |
