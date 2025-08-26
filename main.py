import asyncio
import time
from typing import Dict, Any
import pandas as pd

from intent_detection_agent import find_intent, intent_response_agent
from checklist_agent import field_to_set_agent
from csv_agent import run_csv_agent, get_search_data, get_filter_for_columns
from query_for_hybrid import query_maker_hybrid
from hybrid_search import hybrid_search_in_property, build_retriever

# Build retriever once (cached outside async function)
retriever = build_retriever()

async def async_workflow(user_query: str, df1: pd.DataFrame) -> Dict[str, Any]:
    """
    Orchestrates intent detection, field selection, hybrid search, and
    deterministic CSV filtering in parallel.
    `df1` must be a pandas DataFrame (not a file path).
    """
    timings: Dict[str, float] = {}

    # ------------------------
    # Step 1: Intent + Fields + Hybrid query (parallel)
    # ------------------------
    start = time.time()
    intent_task = asyncio.to_thread(find_intent, user_query)
    fields_task = asyncio.to_thread(field_to_set_agent, user_query)
    hybrid_query_task = asyncio.to_thread(query_maker_hybrid, user_query)

    intent, fields, hybrid_query = await asyncio.gather(
        intent_task, fields_task, hybrid_query_task
    )
    timings["intent_fields_hybridQuery"] = time.time() - start
    print("\n--- Step 1 Results ---")
    print("Intent:", intent)
    print("Fields:", fields)
    print("Hybrid Query:", hybrid_query)

    # ------------------------
    # Property-related flow
    # ------------------------
    if getattr(intent, "Property_Related", False):
        if hybrid_query == "No_User_Query":
            # Step 2: CSV preprocessing (search_data + filter comparators)
            start = time.time()
            search_data_task = asyncio.to_thread(get_search_data, user_query)
            filter_task = asyncio.to_thread(get_filter_for_columns, user_query)
            search_data, filter_on_columns = await asyncio.gather(
                search_data_task, filter_task
            )
            timings["csvPreproc"] = time.time() - start
            print("\n--- Step 2 Results (CSV-only branch) ---")
            print("Search Data:", search_data)
            print("Filter on Columns:", filter_on_columns)

            # Step 3: Deterministic CSV filter
            start = time.time()
            csv_result = await asyncio.to_thread(
                run_csv_agent, fields.model_dump(), df1, search_data, filter_on_columns
            )
            timings["csv_agent"] = time.time() - start
            print("\n--- Step 3 Results (CSV-only branch) ---")
            print("CSV Result:", csv_result)

            print("\nTimings (seconds):", timings)
            return {
                "csv_result": csv_result,
                "hybrid_result": [],  # no hybrid search performed
                "timings": timings,
            }

        # Otherwise, run hybrid search in background while doing CSV work.
        print("\nHybrid Working...")
        hybrid_task = asyncio.create_task(
            asyncio.to_thread(hybrid_search_in_property, hybrid_query, retriever)
        )

        # Step 3: CSV preprocessing
        start = time.time()
        search_data_task = asyncio.to_thread(get_search_data, user_query)
        filter_task = asyncio.to_thread(get_filter_for_columns, user_query)
        search_data, filter_on_columns = await asyncio.gather(
            search_data_task, filter_task
        )
        timings["csvPreproc"] = time.time() - start
        print("\n--- Step 3 Results ---")
        print("Search Data:", search_data)
        print("Filter on Columns:", filter_on_columns)

        # Step 4: Deterministic CSV filter
        start = time.time()
        csv_result = await asyncio.to_thread(
            run_csv_agent, fields.model_dump(), df1, search_data, filter_on_columns
        )
        timings["csv_agent"] = time.time() - start
        print("\n--- Step 4 Results ---")
        print("CSV Result:", csv_result)

        # Step 5: Await hybrid result
        start = time.time()
        hybrid_result = await hybrid_task
        timings["hybrid_agent"] = time.time() - start
        print("\n--- Step 5 Results ---")
        print("Hybrid Result:", hybrid_result)

        print("\nTimings (seconds):", timings)
        return {
            "csv_result": csv_result,
            "hybrid_result": hybrid_result,
            "timings": timings,
        }

    # ------------------------
    # Non-property-related flow
    # ------------------------
    start = time.time()
    result = await asyncio.to_thread(intent_response_agent, user_query)
    timings["intent_response_agent"] = time.time() - start
    print("\n--- Non-property-related Result ---")
    print("Response:", result)

    print("\nTimings (seconds):", timings)
    return {"result": result, "timings": timings}
