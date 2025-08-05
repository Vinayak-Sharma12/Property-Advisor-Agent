import re
import os
from llm_models import deepseek_model
from parser_and_prompts import query_generate_prompt,search_prompt_template,search_parser
import pandas as pd 
from dotenv import load_dotenv
load_dotenv()


local_path=os.getenv("LOCAL_PATH")
 

def make_query_and_fetch_result(df,columns,search_data):
    
    query_prompt = query_generate_prompt.format(columns=columns, search_data=search_data)
    result=deepseek_model.invoke(query_prompt).content
    # print(f"LLM Response with COT:{result}")

    # Extracting Dataframe query code 
    match = re.search(r"```python\n(.*?)```", result, re.DOTALL)
    if match:
        query_code = match.group(1).strip()
        print("Extracted Query:\n", query_code)
    else:
        print("No query code found.")

   # Querying the DataFrame
    try:
        filtered_df = eval(query_code, {"df": df})
        print(len(filtered_df))
        print("Filtered DataFrame:\n", filtered_df)
        return filtered_df
    except Exception as e:
        print("Error while evaluating query:", e)
        return None


# make_query(df,fields)

def get_search_data(user_query):
    search_chain=search_prompt_template|deepseek_model|search_parser
    result=search_chain.invoke(user_query)
    search_data=result.model_dump(exclude_none=True)
    # print(search_data)
    return search_data


# get_search_data("Find a flat of 3bhk with 2 balocies and with Servent room")

def run_csv_agent(fields,csv_path,search_data):
    df=pd.read_csv(csv_path)
    columns=[]
    for key in fields:
        if fields[key]==True:
            columns.append(key)
    
    print(columns)
    result=make_query_and_fetch_result(df,columns,search_data)
    print(result)
    return result 

# user_query=input("Enter Your Query")
# csv_agent(user_query,fields)
