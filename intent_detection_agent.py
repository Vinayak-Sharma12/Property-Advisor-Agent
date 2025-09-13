from llm_models import get_llama_model, initialize_models
from parser_and_prompts import intent_prompt,intent_response_prompt
from parser_and_prompts import intent_parser

def find_intent(user_query):
    # Initialize models if not already done
    initialize_models()
    llama_model = get_llama_model()
    intent_chain=intent_prompt|llama_model|intent_parser
    intent=intent_chain.invoke({'user_query':user_query})
    return intent


def intent_response_agent(user_query):
    # Initialize models if not already done
    initialize_models()
    llama_model = get_llama_model()
    intent_response_chain=intent_response_prompt|llama_model
    result=intent_response_chain.invoke(user_query).content
    return result

# print(find_intent(input("Enter the query")))

     
     