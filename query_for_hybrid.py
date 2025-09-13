from parser_and_prompts import hybrid_query_maker_prompt
from llm_models import get_deepseek_model, initialize_models

def query_maker_hybrid(user_query):
    # Initialize models if not already done
    initialize_models()
    deepseek_model = get_deepseek_model()
    llm=hybrid_query_maker_prompt|deepseek_model
    result=llm.invoke(user_query)
    result=result.content
    hybrid_query = result.split("</think>", 1)[-1].strip()

    print(hybrid_query)
    return hybrid_query



# query_maker_hybrid("Tell me flat of 3bhk of Area 5000 sq.ft with carpet Area havign 24/7 power backup ")