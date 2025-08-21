from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from models import Intent,FieldToSearch,SearchData,ApplyFilterToColumn



search_parser=PydanticOutputParser(pydantic_object=SearchData)
intent_parser=PydanticOutputParser(pydantic_object=Intent)
field_to_set_parser=PydanticOutputParser(pydantic_object=FieldToSearch)
filter_column_parser=PydanticOutputParser(pydantic_object=ApplyFilterToColumn)

intent_prompt = PromptTemplate(
    template="""
You are a User Query Analyst Agent specialized in analyzing whether a query is a Greeting, Property_Related, Farewell, or Other.

Query:
{user_query}

Return the answer in the following Pydantic JSON format, with no extra explanation or text:

{format_instructions}

Schema:
{{
  "Greeting": bool,         # True if it's a greeting
  "Property_Related": bool, # True if it's about a property
  "Farewell": bool,         # True if it's a farewell
  "Other": bool             # True if it falls into none of the above
}}

Note:
- Only one of these should be True. The rest must be False.
- Respond with valid JSON only. No explanation.
""",
    input_variables=["user_query"],
    partial_variables={"format_instructions": intent_parser.get_format_instructions()}
)


field_extraction_prompt = PromptTemplate(
    template="""
You are a structured information extraction agent designed to interpret user intent from property-related queries.

Your task is to analyze the input query and return a structured JSON indicating whether each predefined field is explicitly mentioned or reasonably implied in the query.

Instructions:
- Carefully examine the user query to determine intent.
- Mark a field as `true` only if the user is clearly asking about it or if it is strongly implied.
- If there is no direct or clear indirect mention, set the field to `false`.
- Do not infer fields unless there is strong context.
- Respond strictly in the format below — return only a valid JSON as per the specified schema, without any natural language explanation or additional output.

User Query:
{user_query}

Expected Output:
{format_instructions}

Return only valid JSON. Do not explain your answer. Do not include any text outside the JSON.
""",
    input_variables=["user_query"],
    partial_variables={"format_instructions": field_to_set_parser.get_format_instructions()}
)


query_generate_prompt = PromptTemplate(
    template="""
You are a helpful assistant that generates a valid Pandas DataFrame filtering query in Python.

The DataFrame is named `df` and has the following columns:
{columns}
exclude top_floor column

The user has provided the following search criteria:
{search_data}

Some of the columns require comparison filtering (`greater than` or `lesser than`) instead of equality. These rules are defined below:
{value_greater_or_lesser}

Please follow these steps:
1. Match each key in `search_data` to the closest corresponding column in the DataFrame from the provided list.
2. Ignore keys that do not match any column.
3. For matched columns:
   - If the column is listed in `value_greater_or_lesser`, use the specified comparison operator:
     - "Greater than" → `df['column'] > value`
     - "Lesser than" → `df['column'] < value`
   - Otherwise, use an equality check: `df['column'] == value`
4. Combine all conditions using the `&` (bitwise AND) operator.
5. Wrap each condition in parentheses to ensure correct order of evaluation.
6. Construct and return only the final Python statement to filter the DataFrame (e.g., `df[...]`).

Output:
Return only the final line of code, starting with `df[...]`, that applies the appropriate filters to the DataFrame.
""",
    input_variables=["columns", "search_data", "value_greater_or_lesser"],
)


search_prompt_template = PromptTemplate(
    template="""
You are a real estate assistant that extracts **structured search filters** from a user's natural language query.

Your job is to identify and extract:
- Property attributes: price, area, number of bedrooms, bathrooms, balconies, floor information, etc.
- City names mentioned in the query.
-Society or colony or residency name mentioned  and convert it to lower case
- Country name mentioned in the query.

**Extraction Rules:**
1. **Always take numeric values exactly as stated in the query.**
2. Do **not** infer, calculate, or transform values.
3. Ignore comparative words like "more than", "less than", "above", "under", "at least", etc.  
   Example:  
   - Query: "more than one balcony" → Extract: `balcony = 1`  
4. Do not convert words to numbers unless explicitly given (e.g., "two bedrooms" → `bedrooms = 2` is acceptable).
5. Do not make assumptions about missing data.

**Output Format:**  
Return the output strictly in this format:  
{format_instructions}

User Query: "{user_query}"
""",
    input_variables=["user_query"],
    partial_variables={"format_instructions": search_parser.get_format_instructions()}
)


filter_prompt_template = PromptTemplate(
    template="""
You are a real estate assistant that you need to analyse the user query and find those columns that needs filter of greater than or lesser than 


Extract the following information and return it in the correct format:

{format_instructions}

User Query: "{user_query}"
""",
    input_variables=["user_query"],
    partial_variables={"format_instructions": filter_column_parser.get_format_instructions()}
)

intent_response_prompt = PromptTemplate(
    template="""
You are a friendly and helpful real estate assistant bot.

The user has not asked a property-related query. Your task is to respond politely and naturally — acknowledging the user's intent (Greeting, Farewell, or Other) — while smartly redirecting the conversation back to real estate topics without sounding forceful.

Always keep your tone warm, engaging, and professional.

User Query: "{user_query}"
""",
    input_variables=["user_query"]
)

