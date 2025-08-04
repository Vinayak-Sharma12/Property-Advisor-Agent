from intent_detection_agent import find_intent
from checklist_agent import field_to_set_agent
from csv_agent import run_csv_agent

def workflow(user_query:str):
    # user_query=input("Enter Your Query")
    csv_path='dataset/property_dataset_floor.csv'

    intent=find_intent(user_query)
    fields=field_to_set_agent(user_query)
    fields_dict = fields.model_dump()
    print(intent)
    print(type(fields_dict))
    print(fields_dict)
    result=run_csv_agent(user_query,fields_dict,csv_path)
    return result
    

    
# workflow()