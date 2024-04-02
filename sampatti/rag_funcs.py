from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain_community.document_loaders import DirectoryLoader

from langchain.chains import RetrievalQA
import textwrap

def load_documents(DATA_PATH):
    loader = DirectoryLoader(DATA_PATH, glob="*.md")
    documents = loader.load()
    return documents


def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    # print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    # document = chunks[0]
    # print(document.page_content)
    # print(document.metadata)

    return chunks



def load_embedding_model(model_path, normalize_embedding=True):
    return HuggingFaceEmbeddings(
        model_name=model_path,
        model_kwargs={'device':'cpu'}, # here we will run the model with CPU only
        encode_kwargs = {
            'normalize_embeddings': normalize_embedding # keep True to compute cosine similarity
        }
    )


# Function for creating embeddings using FAISS
def create_embeddings(chunks, embedding_model, storing_path="vectorstore"):

    # Creating the embeddings using FAISS
    vectorstore = FAISS.from_documents(chunks, embedding_model)
    
    # Saving the model in current directory
    vectorstore.save_local(storing_path)
    
    # returning the vectorstore
    return vectorstore


prompt = """
### System:
You are an AI Assistant that follows instructions extreamly well. \
Help as much as you can.

### User:
{prompt}

### Response:

"""

template = """
### System:
You are an respectful and honest assistant. You have to answer the user's \
questions using only the context provided to you. If you don't know the answer, \
just say you don't know. Don't try to make up an answer.

### Context:
{context}

### User:
{question}

### Response:
"""


def load_qa_chain(retriever, llm, prompt):
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever, # here we are using the vectorstore as a retriever
        chain_type="stuff",
        return_source_documents=True, # including source documents in output
        chain_type_kwargs={'prompt': prompt} # customizing the prompt
    )


# def get_response(query, chain):
#     # Getting response from chain
#     response = chain({'query': query})
    
#     # Wrapping the text for better output in Jupyter Notebook
#     wrapped_text = textwrap.fill(response['result'], width=100)
#     return wrapped_text


conversation_history = []  # List to store conversation history

def get_response(query, chain):
  # Update context with conversation history
  context = "\n".join(conversation_history)

  # Include context in the prompt
  response = chain({'query': query, 'context': context})

  # Update conversation history
  conversation_history.append(f"User: {query}\nSystem: {response['result']}")

  # Wrap and return the response
  wrapped_text = textwrap.fill(response['result'], width=100)
  return wrapped_text

