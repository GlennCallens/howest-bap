import os
import uuid

from azure.search.documents.indexes.models import SimpleField, SearchableField, SearchField, SearchFieldDataType
from dotenv import load_dotenv
from langchain_community.callbacks import get_openai_callback
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from models.InsertDocument import InsertDocument

load_dotenv('.env')


def get_file_paths():
    print("🏃 Started getting file paths.")
    root_dir = "//Users//glenncallens//PycharmProjects//DelawareCodeSearch//pythonProject//SonarReport"

    docs = []

    for dir_path, dir_names, filenames in os.walk(root_dir):
        for file in filenames:
            docs.append(os.path.join(dir_path, file))

    return docs


def process_files(llm, file_paths):
    print("🏃 Started processing files.")

    docs = []
    print("     🔎 Found " + str(len(file_paths)) + " files.")
    i = 0
    for file in file_paths:
        i += 1
        try:
            loader = TextLoader(file, encoding="utf-8")
            file_name = file.split("/")[-1]
            doc = loader.load()
            print("            📄 " + file + " .")
            model = InsertDocument(file_name=file_name, content=doc[0].page_content,
                                   explanation=get_explanation_of_file(llm, doc[0].page_content)
                                   )

            docs.append(model)
            print("         📁 " + str(i) + "/" + str(len(file_paths)) + " processed.")
        except Exception as e:
            print(e)

    return docs


def get_explanation_of_file(llm, file_content):
    system = SystemMessage("Give a short description about what this file is about / does. Max 3 lines please. Just "
                           "return that. Nothing else.")
    human = HumanMessage(str(file_content))

    with get_openai_callback() as cb:
        llm(messages=[system, human])

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    if cb.total_tokens > 8100:
        n_file_content = splitter.split_text(file_content)
        human_l = HumanMessage(str(n_file_content[0]))
        try:
            return llm(messages=[system, human_l]).content
        except Exception as e:
            print(e)
    else:
        try:
            return llm(messages=[system, human]).content
        except Exception as e:
            print(e)


def embed_file(model: InsertDocument):
    index_name = "index-sonar-report"
    embed_explanation(index_name, model)
    embed_content(index_name, model)


def embed_explanation(index_name, model: InsertDocument):
    embeddings = AzureOpenAIEmbeddings(azure_deployment=os.getenv('AZURE_EMBEDDING_DEPLOYMENT_NAME'),
                                       model=os.getenv('AZURE_EMBEDDING_MODEL_NAME'),
                                       azure_endpoint=os.getenv('AZURE_OPENAI_BASE_URL'),
                                       api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                                       openai_api_type="azure",
                                       chunk_size=1)
    embedding_function = embeddings.embed_query

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="file_name", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchField(name="content_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=len(embedding_function(model.explanation)),
                    vector_search_profile_name="myHnswProfile"),
        SearchableField(
            name="metadata",
            type=SearchFieldDataType.String,
            searchable=True,
        ),
    ]

    index_name = index_name + "-explanation"
    acs = AzureSearch(azure_search_endpoint=os.getenv('AZURE_AI_SEARCH_ENDPOINT'),
                      azure_search_key=os.getenv('AZURE_AI_SEARCH_KEY'),
                      index_name=index_name,
                      embedding_function=embedding_function,
                      fields=fields)
    acs.add_texts([model.file_name], [{
        "file_name": model.file_name,
        "content": model.explanation,
        "id": str(uuid.uuid4())
    }])


def embed_content(index_name, model: InsertDocument):
    embeddings = AzureOpenAIEmbeddings(azure_deployment=os.getenv('AZURE_EMBEDDING_DEPLOYMENT_NAME'),
                                       model=os.getenv('AZURE_EMBEDDING_MODEL_NAME'),
                                       azure_endpoint=os.getenv('AZURE_OPENAI_BASE_URL'),
                                       api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                                       openai_api_type="azure",
                                       chunk_size=1)
    embedding_function = embeddings.embed_query

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="file_name", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchField(name="content_vector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=len(embedding_function(model.content)),
                    vector_search_profile_name="myHnswProfile"),
        SearchableField(name="explanation", type=SearchFieldDataType.String),
        SearchableField(
            name="metadata",
            type=SearchFieldDataType.String,
            searchable=True,
        ),
    ]

    index_name = index_name + "-content"
    acs = AzureSearch(azure_search_endpoint=os.getenv('AZURE_AI_SEARCH_ENDPOINT'),
                      azure_search_key=os.getenv('AZURE_AI_SEARCH_KEY'),
                      index_name=index_name,
                      embedding_function=embedding_function,
                      fields=fields)
    acs.add_texts([model.file_name], [{
        "file_name": model.file_name,
        "content": model.content,
        "explanation": model.explanation,
        "id": str(uuid.uuid4())
    }])


def run():
    print("✅ Project started.")
    file_paths = get_file_paths()
    print("✅ File paths collected.")
    llm = AzureChatOpenAI(deployment_name="gpt-4",
                          azure_endpoint=os.getenv('AZURE_OPENAI_BASE_URL'),
                          api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
                          temperature=0)
    docs = process_files(llm, file_paths)
    print("✅ Files collected.")
    print("🏃 Started embedding.")
    i = 0
    for doc in docs:
        i += 1
        print("     🔍 Started embedding file " + str(i) + "/" + str(len(docs)) + " .")
        print("         📁 " + doc.file_name + " .")
        embed_file(doc)


run()
