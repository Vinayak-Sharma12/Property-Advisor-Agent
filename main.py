from intent_detection_agent import find_intent
from checklist_agent import field_to_set_agent
from csv_agent import run_csv_agent,get_search_data,get_filter_for_columns

def workflow(user_query:str):
    # user_query=input("Enter Your Query")
    csv_path='dataset/property_dataset_new.csv'

    intent=find_intent(user_query)
    fields=field_to_set_agent(user_query)
    fields_dict = fields.model_dump()
    print(intent)
    print(fields_dict)
    search_data=get_search_data(user_query)
    filter_on_columns=get_filter_for_columns(user_query)
    print(filter_on_columns)
    print(f"This is the Search{search_data}")
    result=run_csv_agent(fields_dict,csv_path,search_data,filter_on_columns)
    return result
    


    
# workflow()