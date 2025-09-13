from llm_models import get_deepseek_model, initialize_models
from parser_and_prompts import field_to_set_parser,field_extraction_prompt

def field_to_set_agent(user_query):
    # Initialize models if not already done
    initialize_models()
    deepseek_model = get_deepseek_model()
    field_set_chain=field_extraction_prompt|deepseek_model|field_to_set_parser
    result=field_set_chain.invoke(user_query)
    # print(result)
    return result

# print(field_to_set_agent(input("Enter User Query")))

