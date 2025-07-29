from llm_models import deepseek_model
from parser_and_prompts import field_to_set_parser,field_extraction_prompt

def field_to_set_agent(user_query):
    field_set_chain=field_extraction_prompt|deepseek_model|field_to_set_parser
    result=field_set_chain.invoke(user_query)
    # print(result)
    return result

# print(field_to_set_agent(input("Enter User Query")))

