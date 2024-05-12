import os

from langchain_community.chat_models import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from ai.get_context import search
from github.issue import get_issue, post_comment_with_solution


def get_solution(question, context):
    system = SystemMessage("""
    Here you have a file, try to implement the solution for the issue. 
    Return the complete file with the issue implemented.
    Give the complete file with the issue implemented. Just give the file not the explanation.
    And no other comments or text.
    """ + str(context))

    llm = AzureChatOpenAI(deployment_name=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                          azure_endpoint=os.getenv('AZURE_OPENAI_BASE_URL'),
                          api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
                          temperature=0)

    return llm(messages=[system, HumanMessage(question)]).content


def decide_file(question, context):
    system = SystemMessage("""
    Provided with a question that needs to be implemented in the code.
    I have the following files, which file is best to implement the solution?
    Just provide the file name, nothing else. Only the filename!!
    """ + str(context))

    llm = AzureChatOpenAI(deployment_name=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
                          azure_endpoint=os.getenv('AZURE_OPENAI_BASE_URL'),
                          api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
                          temperature=0)

    return llm(messages=[system, HumanMessage(question)]).content


def post_solution(repo: str, issue_number: str):
    question = get_issue(repo, issue_number)
    context = search(question, repo)
    file = decide_file(question, context)
    solution = get_solution(question, context[file])
    post_comment_with_solution(repo, issue_number, solution)
