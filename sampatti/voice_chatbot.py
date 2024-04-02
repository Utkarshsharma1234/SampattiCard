from rag_funcs import *
from langchain_community.llms import Ollama
from langchain import PromptTemplate



llm = Ollama(model="orca-mini", temperature=0)

# Loading the Embedding Model
embed = load_embedding_model(model_path="all-MiniLM-L6-v2")

docs = load_documents(DATA_PATH="data/books")
# print(f"the docs are {docs}")
documents = split_text(documents=docs)

# creating vectorstore
vectorstore = create_embeddings(documents, embed)

# converting vectorstore to a retriever
retriever = vectorstore.as_retriever()

prompt = PromptTemplate.from_template(template)

# Creating the chain
chain = load_qa_chain(retriever, llm, prompt)

print(get_response("Describe his public image.", chain=chain))