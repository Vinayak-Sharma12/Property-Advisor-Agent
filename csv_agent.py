import re
import os
from llm_models import deepseek_model
from parser_and_prompts import query_generate_prompt,search_prompt_template,filter_prompt_template,search_parser,filter_column_parser
import pandas as pd 
from dotenv import load_dotenv
load_dotenv()


local_path=os.getenv("LOCAL_PATH")
 
# value_greater_or_lesser={
#     "Price_in_Crore":'Greater than'
# }

def get_filter_for_columns(user_query):
    filter_chain=filter_prompt_template|deepseek_model|filter_column_parser
    result=filter_chain.invoke({'user_query':user_query})
    filter_on_column=result.model_dump(exclude_none=True)
    # print(type(filter_on_column))
    # print(filter_on_column)
    return result
    
# get_filter_for_columns("Tell me flat under 5 Crore and Rate per sq meter more than 5000 with area more than 800 sq ft")

def make_query_and_fetch_result(df,columns,search_data,filter_on_columns):
    
    query_prompt = query_generate_prompt.format(columns=columns, search_data=search_data,value_greater_or_lesser=filter_on_columns)
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

def run_csv_agent(fields,csv_path,search_data,filter_on_columns):
    df=pd.read_csv(csv_path)
    if fields['top_floor']==True:
        df = df[df['Totalfloor'] == df['floorNum']]
        print(df.head())

    columns=[]
    for key in fields:
        if key=='top_floor':
            continue
        if fields[key]==True:
            columns.append(key)
    
    print(columns)

    result=make_query_and_fetch_result(df,columns,search_data,filter_on_columns)
    if result is None and fields['top_floor']==True and columns==[]:
            result=df

    print(result)
    return result 

# user_query=input("Enter Your Query")
# run_csv_agent({'Price_in_Crore':True},"dataset/property_dataset_new.csv",get_search_data("Give me a flat more than 1.5 Crore"))
