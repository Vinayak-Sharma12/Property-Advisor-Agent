from parser_and_prompts import hybrid_query_maker_prompt
from llm_models import deepseek_model,llama_model

def query_maker_hybrid(user_query):
    llm=hybrid_query_maker_prompt|deepseek_model
    result=llm.invoke(user_query)
    result=result.content
    hybrid_query = result.split("</think>", 1)[-1].strip()

    print(hybrid_query)
    return hybrid_query



# query_maker_hybrid("Tell me flat of 3bhk of Area 5000 sq.ft with carpet Area havign 24/7 power backup ")