from llm_models import deepseek_model
from parser_and_prompts import intent_prompt
from parser_and_prompts import intent_parser

def find_intent(user_query):
    intent_chain=intent_prompt|deepseek_model|intent_parser
    intent=intent_chain.invoke({'user_query':user_query})
    return intent

# print(find_intent(input("Enter the query")))

     
     