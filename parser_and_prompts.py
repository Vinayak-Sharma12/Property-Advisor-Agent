from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from models import Intent,FieldToSearch,SearchData,ApplyFilterToColumn,YesNoResults



search_parser=PydanticOutputParser(pydantic_object=SearchData)
intent_parser=PydanticOutputParser(pydantic_object=Intent)
field_to_set_parser=PydanticOutputParser(pydantic_object=FieldToSearch) 
filter_column_parser=PydanticOutputParser(pydantic_object=ApplyFilterToColumn)
yes_no_parser = PydanticOutputParser(pydantic_object=YesNoResults)


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

**Instructions:**
- For each field, only use "Greater than" or "Lesser than" if the query asks for a comparison (e.g., more than, less than, above, under).
- Never use numbers or other values for these fields.
- If no comparison is needed for a field, set its value to null.


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





hybrid_query_maker_prompt = PromptTemplate(
    template="""
You are a professional and friendly real estate assistant. Your task is to **reform the user's query** so that it focuses **only** on these aspects of a flat:

- Nearby locations  
- Features (e.g., Fire Alarm, Swimming Pool, Park, Lift)  
- Furnishing details (e.g., Wardrobe, Exhaust Fan, Modular Kitchen, Microwave, Geyser, ACs)  
- General description of the flat  

Do **not** include or ask about: price, area, area type, exact address, floor number, or total floors or BHK or bedrooms or bathrooms or balconies or additional room or no side facing or sector or society,city,country .  

Strict rules:
1. Only use information present in the original user query.  
2. Do **not** add any extra information, assumptions, or commentary.  
3. Output **only the reformulated query in a single line**.  
4. If the original query contains no relevant information related to the above aspects, output exactly: "No_User_Query".  
5. Do not include quotes, formatting, or any explanations in the output.

Original User Query: "{user_query}"

Examples"
1.
User Query: "Looking for a 3BHK flat near a school with swimming pool and lift, fully furnished."
Reformed Query: "A flat near a school with swimming pool and lift."

2.
User Query: "Need a flat near McDonald's with ACs, wardrobe, and modular kitchen."
Reformed Query: "A flat near McDonald's with ACs, wardrobe, and modular kitchen."

3.
User Query: "Tell me flats in Mumbai, 1200 sq.ft, semi-furnished with geyser and exhaust fan."
Reformed Query: "A flat in Mumbai with geyser and exhaust fan."

4.
User Query: "Any 2BHK apartments with park, lift, and fire alarm?"
Reformed Query: "A flat with park, lift, and fire alarm."

5.
User Query: "Looking for a flat fully furnished with microwave, ACs, and wardrobe, near a shopping mall."
Reformed Query: "A flat with microwave, ACs, and wardrobe near a shopping mall."

6.
User Query: "I want a flat in Pune with balcony, lift, and modular kitchen, priced under 70 lakhs."
Reformed Query: "A flat in  with balcony, lift, and modular kitchen."

7.
User Query: "Tell me flats with swimming pool and park nearby."
Reformed Query: "A flat with swimming pool and park nearby."

8.
User Query: "Looking for a flat near metro station with ACs, wardrobe, and geyser."
Reformed Query: "A flat near metro station having  ACs, wardrobe, and geyser."

9.
User Query: "I want a 1BHK flat under 5 crore sea side facing  with fire alarm and lift, on 2nd floor."
Reformed Query: "A fully furnished flat with fire alarm and lift."

10.
User Query: "Need a flat with park, swimming pool, lift, and ACs."
Reformed Query: "A flat with park, swimming pool, lift, and ACs."

11.
User Query: "Looking for a flat near office, semi-furnished with microwave and geyser, no preference for floor."
Reformed Query: "A semi-furnished flat near office with microwave and geyser."

12.
User Query: "I want a flat near a hospital with modular kitchen, ACs, and wardrobe."
Reformed Query: "A flat near a hospital with modular kitchen, ACs, and wardrobe."

13.
User Query: "Show me flats with swimming pool, gym, and park."
Reformed Query: "A flat with swimming pool, gym, and park."

14.
User Query: "Tell me 3BHK flats with lift, balcony, and fire alarm, near a school."
Reformed Query: "A flat with lift, balcony, and fire alarm near a school."

15.
User Query: "Looking for a flat near McDonald's or Starbucks, fully furnished with ACs and geyser."
Reformed Query: "A fully furnished flat near McDonald's or Starbucks with ACs and geyser."

16.
User Query: "I want a flat near park and metro, with modular kitchen and microwave, ignore floor or price."
Reformed Query: "A flat near park and metro with modular kitchen and microwave."

17.
User Query: "Any flats near a shopping mall with swimming pool, lift, ACs, and wardrobe?"
Reformed Query: "A flat near a shopping mall with swimming pool, lift, ACs, and wardrobe."

18.
User Query: "Looking for a flat in Bangalore having  fire alarm facility and geyser included."
Reformed Query: "A flat  with fire alarm and geyser."

19.
User Query: "Flats near hospital or school with park, lift, and ACs."
Reformed Query: "A flat near hospital or school with park, lift, and ACs."

20.
User Query: "I want a flat with swimming pool, gym, and park, no need to mention BHK or price."
Reformed Query: "A flat with swimming pool, gym, and park."
Reformed Query:
""",
    input_variables=["user_query"]
)

yes_no_prompt = PromptTemplate(
    template="""
You are an assistant that evaluates document chunks against a user query.

Task
- For each chunk, decide if it is relevant to answering the user query correctly and stictly.
- If the chunk is relevant or contains information that answer the query → "Yes".
- Otherwise → "No".
- Return exactly one decision per chunk, preserving the given chunk_id values.
- Do not add extra fields or commentary.

{format_instructions}

User Query:
{user_query}

Document Chunks:
{document_text}
""".strip(),
    input_variables=["user_query", "document_text"],
    partial_variables={"format_instructions": yes_no_parser.get_format_instructions()},
)