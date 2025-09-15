import asyncio
import time
from typing import Dict, Any
import pandas as pd

from intent_detection_agent import find_intent, intent_response_agent
from checklist_agent import field_to_set_agent
from csv_agent import run_csv_agent, get_search_data, get_filter_for_columns
from query_for_hybrid import query_maker_hybrid
from hybrid_search import hybrid_search_in_property, build_retriever

# ------------------------------------------------------
# Build retriever once (cached outside async function)
# ------------------------------------------------------
try:
    retriever = build_retriever()
    if retriever is not None:
        print("[INFO] Retriever built successfully.")
    else:
        print("[INFO] Retriever not available (Pinecone dependencies missing).")
except Exception as e:
    retriever = None
    print(f"[WARN] build_retriever() failed at import: {e!r}. Hybrid disabled.")


def _no_hybrid(q: str) -> bool:
    """Helper: decide if hybrid query should be skipped."""
    if not q:
        return True
    q = str(q).strip()
    return q in {"", "No_User_Query", "N/A", "None"}


# ------------------------------------------------------
# Main Orchestration Workflow
# ------------------------------------------------------
async def async_workflow(user_query: str, df1: pd.DataFrame) -> Dict[str, Any]:
    """
    Orchestrates intent detection, field selection, hybrid search, and
    deterministic CSV filtering in parallel.
    Returns a dict with a `result_type` and a `final_df` if property-related.
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
    print(fields)
    timings["intent_fields_hybridQuery"] = time.time() - start
    print("[INFO] Intent, Fields, and Hybrid Query computed.")

    property_related = bool(getattr(intent, "Property_Related", False))

    # ------------------------
    # Property-related flow
    # ------------------------
    if property_related:
        # Case A: Hybrid query unusable or retriever unavailable
        if retriever is None or _no_hybrid(hybrid_query):
            # Step 2: CSV preprocessing (search_data + filter comparators)
            start = time.time()
            search_data_task = asyncio.to_thread(get_search_data, user_query)

            filter_task = asyncio.to_thread(get_filter_for_columns, user_query)
            search_data, filter_on_columns = await asyncio.gather(
                search_data_task, filter_task
            )
            timings["csvPreproc"] = time.time() - start
            print(search_data)
            print("[INFO] Search data & filter-on-columns ready (CSV-only branch).")

            # Step 3: Deterministic CSV filter
            start = time.time()
            csv_result = await asyncio.to_thread(
                run_csv_agent, fields.model_dump(), df1, search_data, filter_on_columns
            )
            timings["csv_agent"] = time.time() - start
            print("[INFO] CSV agent (manual filtering) done (CSV-only branch).")

            return {
                "result_type": "property",
                "final_df": csv_result,      # <- final DataFrame is just CSV result
                "csv_result": csv_result,
                "hybrid_result": [],
                "timings": timings,
            }

        # Case B: Hybrid query usable
        print("[INFO] Hybrid Working...")
        # Step 2: Kick off hybrid search in background
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
        print("[INFO] Search data & filter-on-columns ready.")

        print("[DEBUG] search_data:", search_data)
        print("[DEBUG] filter_on_columns:", filter_on_columns)

        # Step 4: Deterministic CSV filter
        start = time.time()
        csv_result = await asyncio.to_thread(
            run_csv_agent, fields.model_dump(), df1, search_data, filter_on_columns
        )
        timings["csv_agent"] = time.time() - start
        print("[INFO] CSV agent (manual filtering) done.")

        # Step 5: Await hybrid result
        start = time.time()
        hybrid_result = await hybrid_task
        timings["hybrid_agent"] = time.time() - start
        print("[INFO] Hybrid Agent Done.")
        print("[RESULT] Hybrid search property_ids:", hybrid_result)
        

        # After awaiting hybrid_result
        used_hybrid = True  # we’re in the hybrid branch

        final_df = csv_result
        if used_hybrid:
            if isinstance(hybrid_result, list) and len(hybrid_result) > 0:
                if "property_id" in csv_result.columns:
                    hybrid_ids = {str(i) for i in hybrid_result}
                    before_count = len(csv_result)
                    final_df = csv_result[csv_result["property_id"].astype(str).isin(hybrid_ids)]
                    after_count = len(final_df)
                    print(f"[DEBUG] CSV rows before intersection: {before_count}")
                    print(f"[DEBUG] Hybrid ID count: {len(hybrid_ids)}")
                    print(f"[DEBUG] Rows after intersection by property_id: {after_count}")
                else:
                    print("[WARN] property_id missing; forcing empty due to strict intersection.")
                    final_df = csv_result.iloc[0:0]
            else:
                # hybrid ran but found nothing → strict empty
                final_df = csv_result.iloc[0:0]
                print("[DEBUG] Hybrid returned no IDs; final result forced empty.")

        return {
            "result_type": "property",
            "final_df": final_df,           # <- unified DataFrame
            "csv_result": csv_result,
            "hybrid_result": hybrid_result, # raw hybrid list for debugging
            "timings": timings,
        }

    # ------------------------
    # Non-property-related flow
    # ------------------------
    start = time.time()
    result = await asyncio.to_thread(intent_response_agent, user_query)
    timings["intent_response_agent"] = time.time() - start

    print("[INFO] Non-property flow timings (seconds):", timings)
    return {
        "result_type": "chat",
        "result": result,
        "timings": timings,
    }
