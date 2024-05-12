import logging
import os

from langchain_community.embeddings import AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch


def get_context(index_name, question):
    files = []
    explanation = get_search(index_name + "-explanation", question)
    content = get_search(index_name + "-content", question)
    for x in explanation:
        files.append(x.metadata['file_name'])
        print(files)
    for x in content:
        files.append(x.metadata['file_name'])
        print(files)

    return list(set(files))


def get_search(index_name, question):
    embeddings = AzureOpenAIEmbeddings(azure_deployment=os.getenv('AZURE_EMBEDDING_DEPLOYMENT_NAME'),
                                       model=os.getenv('AZURE_EMBEDDING_MODEL_NAME'),
                                       azure_endpoint=os.getenv('AZURE_OPENAI_BASE_URL'),
                                       api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                                       openai_api_type="azure",
                                       chunk_size=1)
    acs = AzureSearch(azure_search_endpoint=os.getenv('AZURE_AI_SEARCH_ENDPOINT'),
                      azure_search_key=os.getenv('AZURE_AI_SEARCH_KEY'),
                      index_name=index_name,
                      embedding_function=embeddings.embed_query)

    return acs.search(question, search_type="similarity")


def get_file(index_name, file_name):
    file = get_search(index_name, file_name)[0].page_content
    return file


def search(question: str, repo: str):
    index_name = "index-" + repo
    context = get_context(index_name, question)
    logging.error(context)
    result = {}
    for file in context:
        print(file)
        result[file] = get_file(index_name + "-content", file)

    return result
