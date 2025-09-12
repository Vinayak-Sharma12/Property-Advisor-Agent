import streamlit as st  
import pandas as pd
import asyncio
import os
import re
import ast
from langchain_community.document_loaders import CSVLoader

DATA_PATH = "dataset/Description.csv"

# ---------------------------
# Load Data
# ---------------------------
@st.cache_resource
def load_data():
    loader = CSVLoader(file_path=DATA_PATH, metadata_columns=["property_id"])
    docs = loader.load()
    return pd.DataFrame([{"property_id": d.metadata["property_id"], "description": d.page_content} for d in docs])

df = load_data()
# Build a fast lookup from property_id -> description (from df)
try:
    _desc_by_id = {str(r["property_id"]): r.get("description", "") for _, r in df.iterrows()}
except Exception:
    _desc_by_id = {}

# Helper to clean odd prefixes like "90:" or "Description:"
def _clean_description(text: str) -> str:
    if text is None:
        return ""
    s = str(text).strip()
    # Remove leading colon/dash and numbers like ": 90" or "90"
    s = re.sub(r'^\s*[:\-]*\s*\d+\s*', '', s)
    # Remove leading "Description:" label (case-insensitive)
    s = re.sub(r'^description\s*[:\-]*\s*', '', s, flags=re.IGNORECASE)
    return s.strip()

@st.cache_data
def csv_load_data():
    return pd.read_csv("dataset/property_dataset_with_beautiful_description.csv")

df1 = csv_load_data()

# ---------------------------
# Streamlit UI
# ---------------------------
st.title("Property Advisor Agent")

# Sidebar: API Keys
with st.sidebar:
    st.subheader("API Keys")
    groq_key = st.text_input("GROQ API Key", type="password")
    mistral_key = st.text_input("Mistral API Key (optional)", type="password")
    if groq_key:
        os.environ["GROQ_API_KEY"] = groq_key
    if mistral_key:
        os.environ["MISTRAL_API_KEY"] = mistral_key

# Import after keys are possibly set so models read fresh env vars
from main import async_workflow

query = st.text_input("Enter your query:")

# Tabs for view
tabs = st.tabs(["📋 Cards", "📊 Table", "🎨 Beautiful Grid"])

# ---------------------------
# State management
# ---------------------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_property" not in st.session_state:
    st.session_state.selected_property = None
if "search_df" not in st.session_state:
    st.session_state.search_df = None

if not os.getenv("GROQ_API_KEY"):
    st.info("Enter your GROQ API key in the sidebar to enable search.")

if st.button("Search") and query.strip() and os.getenv("GROQ_API_KEY"):
    with st.spinner("Processing your query..."):
        result = asyncio.run(async_workflow(query, df1))

    if isinstance(result, dict) and result.get("result_type") == "property":
        st.session_state.search_df = result["final_df"]
        st.session_state.page = "home"
    elif isinstance(result, dict) and result.get("result_type") == "chat":
        st.subheader("Answer")
        st.write(result["result"])

    else:
        st.write(result)

# ---------------------------
# Render Results (persist across reruns)
# ---------------------------
if st.session_state.search_df is not None:
    final_df = st.session_state.search_df

    if st.session_state.page == "home":
        # ✅ Cards View
        with tabs[0]:
            st.subheader("Properties (Cards View)")
            for idx, row in final_df.iterrows():
                with st.container():
                    st.markdown(
                        f"""
                        <div style=\"border:1px solid #444; border-radius:10px; padding:15px; margin-bottom:10px; background-color:#111;\">
                            <h3 style=\"margin:0;\">🏡 {row['property_name']}</h3>
                            <p style=\"margin:5px 0;\"><b>BHK:</b> {row.get('bedRoom', 'N/A')} BHK</p>
                            <p style=\"margin:5px 0;\"><b>Price:</b> {row.get('Price_in_Crore', 'N/A')} Cr</p>
                            <p style=\"margin:5px 0;\"><b>Society:</b> {row.get('society', 'N/A')}</p>
                            <p style=\"margin:5px 0; color:#ccc;\"><b>Description:</b> {str(row.get('description', 'N/A'))}...</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button("Let's Explore →", key=f"explore_{idx}"):
                        st.session_state.page = "details"
                        st.session_state.selected_property = row.to_dict() if hasattr(row, 'to_dict') else dict(row)
                        st.rerun()

        # ✅ Table View
        with tabs[1]:
            st.subheader("Properties (Table View)")
            st.dataframe(final_df, use_container_width=True)

        # ✅ Grid View
        with tabs[2]:
            st.subheader("Properties (Grid View)")
            cols = st.columns(3)
            for idx, row in final_df.iterrows():
                with cols[idx % 3]:
                    st.markdown(
                        f"""
                        <div style=\"border:1px solid #333; border-radius:10px; padding:15px; margin:10px; background:#1a1a1a;\">
                            <h4 style=\"margin:0;\">🏡 {row['property_name']}</h4>
                            <p><b>BHK:</b> {row.get('bedRoom', 'N/A')}</p>
                            <p><b>Price:</b> {row.get('Price_in_Crore', 'N/A')} Cr</p>
                            <p><b>Society:</b> {row.get('society', 'N/A')}</p>
                            <p style=\"color:#ccc;\"><b>Description:</b> {str(row.get('description', 'N/A'))[:150]}...</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button("Let's Explore →", key=f"grid_explore_{idx}"):
                        st.session_state.page = "details"
                        st.session_state.selected_property = row.to_dict() if hasattr(row, 'to_dict') else dict(row)
                        st.rerun()

    elif st.session_state.page == "details":
        row = st.session_state.selected_property
        if row is None:
            st.warning("No property selected.")
        else:
            # Back action on top for convenience
            if st.button("⬅ Back to results"):
                st.session_state.page = "home"
                st.session_state.selected_property = None
                st.rerun()

            # Header (simplified to avoid stray literal tags)
            property_name = row.get("property_name", "Property")
            city = row.get("city", "N/A")
            status = row.get("status", "N/A")
            society = row.get("society", "N/A")

            st.markdown(
                f"""
                <div style="border:1px solid #333; background:linear-gradient(180deg, #141414, #0f0f0f); padding:20px; border-radius:14px; margin-bottom:16px;">
                    <div style="font-size:28px; font-weight:700;">🏡 {property_name}</div>
                    <div style="color:#aaa; font-size:14px; margin-top:4px;">{society} • {city}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Quick metrics chips
            price_cr = row.get("Price_in_Crore", "N/A")
            bhk = row.get("bedRoom", "N/A")
            area_sqft = row.get("Area_in_sq_meter", "N/A")

            c1, c2, c3 = st.columns(3)
            c1.markdown(f"""
                <div style=\"border:1px solid #2a2a2a; background:#121212; border-radius:12px; padding:14px; text-align:center;\">
                    <div style=\"color:#9aa; font-size:12px;\">Price</div>
                    <div style=\"font-size:20px; font-weight:700; margin-top:4px;\">₹ {price_cr} Cr</div>
                </div>
            """, unsafe_allow_html=True)
            c2.markdown(f"""
                <div style=\"border:1px solid #2a2a2a; background:#121212; border-radius:12px; padding:14px; text-align:center;\">
                    <div style=\"color:#9aa; font-size:12px;\">Configuration</div>
                    <div style=\"font-size:20px; font-weight:700; margin-top:4px;\">{bhk} BHK</div>
                </div>
            """, unsafe_allow_html=True)
            c3.markdown(f"""
                <div style=\"border:1px solid #2a2a2a; background:#121212; border-radius:12px; padding:14px; text-align:center;\">
                    <div style=\"color:#9aa; font-size:12px;\">Area</div>
                    <div style=\"font-size:20px; font-weight:700; margin-top:4px;\">{area_sqft} sq m</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("\n")

            # Two-column specs grid
            left_col, right_col = st.columns(2)
            left_col.markdown(f"""
                <div style=\"border:1px solid #2a2a2a; background:#121212; border-radius:12px; padding:16px;\">
                    <div style=\"font-weight:700; margin-bottom:8px;\">Key Specs</div>
                    <div style=\"display:grid; grid-template-columns: 1fr 1fr; gap:10px;\">
                        <div>🧭 Facing<br><b>{row.get('facing', 'N/A')}</b></div>
                        <div>🛁 Bathrooms<br><b>{row.get('bathroom', 'N/A')}</b></div>
                        <div>🚪 Balconies<br><b>{row.get('balcony', 'N/A')}</b></div>
                        <div>📍Address<br><b>{row.get('address', 'N/A')}</b></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            # Compute floor info string like 4/14
            floor_num = row.get('floorNum', 'N/A')
            total_floor = row.get('Totalfloor', 'N/A')
            floor_str = f"{floor_num}/{total_floor}" if floor_num != 'N/A' or total_floor != 'N/A' else 'N/A'

            right_col.markdown(f"""
                <div style=\"border:1px solid #2a2a2a; background:#121212; border-radius:12px; padding:16px;\">
                    <div style=\"font-weight:700; margin-bottom:8px;\">Additional</div>
                    <div style=\"display:grid; grid-template-columns: 1fr 1fr; gap:10px;\">
                        <div>🏢 Society<br><b>{row.get('society', 'N/A')}</b></div>
                        <div>🆔 ID<br><b>{row.get('property_id', 'N/A')}</b></div>
                        <div>🧱 Floor<br><b>{floor_str}</b></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # Facilities in flat from features column
            features_raw = row.get('features', [])
            features_list = []
            if isinstance(features_raw, list):
                features_list = [str(x).strip() for x in features_raw if str(x).strip()]
            elif isinstance(features_raw, str):
                try:
                    parsed = ast.literal_eval(features_raw)
                    if isinstance(parsed, list):
                        features_list = [str(x).strip() for x in parsed if str(x).strip()]
                    else:
                        # Fallback: comma-separated string
                        features_list = [s.strip() for s in features_raw.split(',') if s.strip()]
                except Exception:
                    features_list = [s.strip() for s in features_raw.split(',') if s.strip()]

            if features_list:
                chips_html = " ".join([
                    f"<span style=\"display:inline-block; margin:4px 6px 0 0; padding:6px 10px; border:1px solid #2a2a2a; border-radius:999px; background:#121212; color:#ddd; font-size:12px;\">{f}</span>"
                    for f in features_list
                ])
            else:
                chips_html = "<span style=\"color:#999;\">N/A</span>"

            st.markdown(
                f"""
                <div style=\"border:1px solid #2a2a2a; background:#101010; border-radius:12px; padding:16px; margin-top:16px;\">
                    <div style=\"font-weight:700; margin-bottom:8px;\">Facilities in flat</div>
                    <div>{chips_html}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Additional Rooms from additionalRooms column
            add_rooms_raw = row.get('additionalRoom', [])
            add_rooms_list = []
            if isinstance(add_rooms_raw, list):
                add_rooms_list = [str(x).strip() for x in add_rooms_raw if str(x).strip()]
            elif isinstance(add_rooms_raw, str):
                try:
                    parsed = ast.literal_eval(add_rooms_raw)
                    if isinstance(parsed, list):
                        add_rooms_list = [str(x).strip() for x in parsed if str(x).strip()]
                    else:
                        add_rooms_list = [s.strip() for s in add_rooms_raw.split(',') if s.strip()]
                except Exception:
                    add_rooms_list = [s.strip() for s in add_rooms_raw.split(',') if s.strip()]

            if add_rooms_list:
                add_rooms_html = " ".join([
                    f"<span style=\"display:inline-block; margin:4px 6px 0 0; padding:6px 10px; border:1px solid #2a2a2a; border-radius:999px; background:#121212; color:#ddd; font-size:12px;\">{r}</span>"
                    for r in add_rooms_list
                ])
            else:
                add_rooms_html = "<span style=\\\"color:#999;\\\">N/A</span>"

            st.markdown(
                f"""
                <div style=\"border:1px solid #2a2a2a; background:#101010; border-radius:12px; padding:16px; margin-top:16px;\">
                    <div style=\"font-weight:700; margin-bottom:8px;\">Additional Rooms</div>
                    <div>{add_rooms_html}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Description: combine df (by property_id) and row's Description if both exist
            _prop_id = str(row.get("property_id", "")).strip()
            raw_df_desc = _desc_by_id.get(_prop_id)
            raw_row_desc = row.get("Description", row.get("description", ""))
            cleaned_parts = []
            # Clean ONLY the df description (remove leading numbers/labels)
            if raw_df_desc is not None and str(raw_df_desc).strip():
                cleaned_df_desc = _clean_description(raw_df_desc)
                if cleaned_df_desc:
                    cleaned_parts.append(cleaned_df_desc)
            # Keep the row description AS-IS (except trimming whitespace)
            if raw_row_desc is not None and str(raw_row_desc).strip():
                cleaned_parts.append(str(raw_row_desc).strip())
            # Deduplicate while preserving order
            seen = set()
            unique_parts = []
            for p in cleaned_parts:
                if p not in seen:
                    unique_parts.append(p)
                    seen.add(p)
            if unique_parts:
                description_html = "<br><br>".join(unique_parts)
            else:
                description_html = "N/A"
            st.markdown(
                f"""
                <div style="border:1px solid #2a2a2a; background:#101010; border-radius:12px; padding:16px; margin-top:16px;">
                    <div style="font-weight:700; margin-bottom:8px;">Description</div>
                    <div style="color:#ddd; line-height:1.6;">{description_html}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

           

