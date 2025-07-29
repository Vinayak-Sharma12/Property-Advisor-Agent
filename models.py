from pydantic import BaseModel,Field

class Intent(BaseModel):
     Greeting:bool
     Property_Related:bool
     Farewell:bool
     Other:bool
