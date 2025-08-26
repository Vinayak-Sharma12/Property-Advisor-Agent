from llm_models import deepseek_model,llama_model
from parser_and_prompts import intent_prompt,intent_response_prompt
from parser_and_prompts import intent_parser

def find_intent(user_query):
    intent_chain=intent_prompt|llama_model|intent_parser
    intent=intent_chain.invoke({'user_query':user_query})
    return intent


def intent_response_agent(user_query):
    intent_response_chain=intent_response_prompt|llama_model
    result=intent_response_chain.invoke(user_query).content
    return result

# print(find_intent(input("Enter the query")))

     
     