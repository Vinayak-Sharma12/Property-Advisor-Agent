from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from models import Intent

parser=PydanticOutputParser(pydantic_object=Intent)

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from models import Intent

parser = PydanticOutputParser(pydantic_object=Intent)

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

