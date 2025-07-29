from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from models import Intent,FieldToSearch

parser=PydanticOutputParser(pydantic_object=Intent)
field_to_set_parser=PydanticOutputParser(pydantic_object=FieldToSearch)

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
    partial_variables={"format_instructions": parser.get_format_instructions()}
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
