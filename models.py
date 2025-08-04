from pydantic import BaseModel,Field

class Intent(BaseModel):
     Greeting:bool
     Property_Related:bool
     Farewell:bool
     Other:bool

class FieldToSearch(BaseModel):
#   property_name: bool = Field(..., description="Whether the user is asking about the name/type of the property")
    #society: bool = Field(..., description="Whether the query involves the name of the society or project")
    price: bool = Field(..., description="Is the user concerned with price (e.g. in Lacs or Crores)?")
    rate: bool = Field(..., description="Does the query mention rate per sq.ft?")
    areaWithType: bool = Field(..., description="Is the user interested in the area of the flat and its type (e.g. carpet, built-up)?")
    bedRoom: bool = Field(..., description="Is the number of bedrooms or BHK mentioned?")
    bathroom: bool = Field(..., description="Does the query include details about bathrooms?")
    balcony: bool = Field(..., description="Is there a mention of balconies?")
    additionalRoom: bool = Field(..., description="Are extra rooms (servant/study/store) discussed/asked?")
    address: bool = Field(..., description="Is the location or full address part of the query?")
    floorNum: bool = Field(..., description="Does the query talk about the floor or total floors?")
    facing: bool = Field(..., description="Is the direction of the property mentioned (e.g. East-facing)?")
    agePossession: bool = Field(..., description="Does the user ask for construction age or possession date?")
    nearbyLocations: bool = Field(..., description="Does the user ask nearest to particular thing")
#     description: bool = Field(..., description="Is the user asking for a general description of the property?")
    furnishDetails: bool = Field(..., description="Is the furnishing (e.g. AC, wardrobe) mentioned?")
    features: bool = Field(..., description="Are amenities or society features mentioned?")
    rating: bool = Field(..., description="Is there a reference to rating for environment, safety,LifeStyle,Connectivity etc.?")


from enum import Enum
from pydantic import BaseModel, Field


class AdditionalRoomType(str, Enum):
    servant = "servant"
    study = "study"
    store = "store"
    other = "other"


class FacingDirection(str, Enum):
    east = "East"
    west = "West"
    north = "North"
    south = "South"
    northeast = "North-East"
    northwest = "North-West"
    southeast = "South-East"
    southwest = "South-West"


from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class FacingDirection(str, Enum):
    east = "East"
    west = "West"
    north = "North"
    south = "South"
    northeast = "North-East"
    northwest = "North-West"
    southeast = "South-East"
    southwest = "South-West"

class AdditionalRoomType(str, Enum):
    pooja = "Pooja Room"
    study = "Study Room"
    servant = "Servant Room"
    store = "Store Room"

class SearchData(BaseModel):
    price: Optional[int] = Field(None, description="Price mentioned?")
    rate: Optional[bool] = Field(None, description="Does the query mention rate per sq.ft?")
    areaWithType: Optional[bool] = Field(None, description="Is the user interested in area and type (e.g. carpet, built-up)?")

    bedRoom: Optional[int] = Field(None, description="Number of bedrooms or BHK mentioned")
    bathroom: Optional[int] = Field(None, description="Number of bathrooms mentioned")
    balcony: Optional[int] = Field(None, description="Number of balconies mentioned")

    additionalRoom: Optional[AdditionalRoomType] = Field(None, description="Type of extra room if mentioned")

    floorNum: Optional[int] = Field(None, description="Floor number if mentioned")
    Total_floor: Optional[int] = Field(None, description="Total floors in the building if mentioned")

    facing: Optional[FacingDirection] = Field(None, description="Direction of the property if mentioned")

    agePossession: Optional[int] = Field(None, description="Age of construction or possession in years")

    connectivity_rating: Optional[bool] = Field(None, description="Whether ratings for connectivity/lifestyle/etc. are mentioned")




