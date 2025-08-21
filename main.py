from intent_detection_agent import find_intent,intent_response_agent
from checklist_agent import field_to_set_agent
from csv_agent import run_csv_agent,get_search_data,get_filter_for_columns

def workflow(user_query: str, df):
    # csv_path = 'dataset/property_dataset_with_beautiful_description.csv'  # Not needed anymore

    intent = find_intent(user_query)
    print(intent)
    if intent.Property_Related:
        fields = field_to_set_agent(user_query)
        fields_dict = fields.model_dump()
        print(fields_dict)
        print(intent)
        search_data = get_search_data(user_query)
        filter_on_columns = get_filter_for_columns(user_query)
        print(filter_on_columns)
        print(f"This is the Search{search_data}")
        result = run_csv_agent(fields_dict, df, search_data, filter_on_columns)  # Pass df

        return result
    else:
        result = intent_response_agent(user_query)
        return result
    


    
# workflow(input("Enter your query"))