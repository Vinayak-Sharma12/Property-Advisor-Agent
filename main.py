import asyncio
import time
from intent_detection_agent import find_intent, intent_response_agent
from checklist_agent import field_to_set_agent
from csv_agent import run_csv_agent, get_search_data, get_filter_for_columns

async def async_workflow(user_query: str, df):
    timings = {}

    # Intent detection and field extraction in parallel
    start = time.time()
    intent_task = asyncio.to_thread(find_intent, user_query)
    fields_task = asyncio.to_thread(field_to_set_agent, user_query)
    intent, fields = await asyncio.gather(intent_task, fields_task)
    timings['intent_and_fields'] = time.time() - start

    if intent.Property_Related:
        # Search data and filter extraction in parallel
        start = time.time()
        search_data_task = asyncio.to_thread(get_search_data, user_query)
        filter_task = asyncio.to_thread(get_filter_for_columns, user_query)
        search_data, filter_on_columns = await asyncio.gather(search_data_task, filter_task)
        timings['search_and_filter'] = time.time() - start

        # DataFrame filtering
        start = time.time()
        result = run_csv_agent(fields.model_dump(), df, search_data, filter_on_columns)
        timings['run_csv_agent'] = time.time() - start

        print("Timings (seconds):", timings)
        return result
    else:
        start = time.time()
        result = await asyncio.to_thread(intent_response_agent, user_query)
        timings['intent_response_agent'] = time.time() - start

        print("Timings (seconds):", timings)
        return result