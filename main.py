from intent_detection_agent import find_intent
from checklist_agent import field_to_set_agent

def workflow():
    user_query=input("Enter Your Query")
    intent=find_intent(user_query)
    fields=field_to_set_agent(user_query)
    print(intent)
    print(fields)

    
workflow()