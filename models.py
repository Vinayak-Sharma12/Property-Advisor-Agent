from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from typing import List


class Intent(BaseModel):
     Greeting:bool
     Property_Related:bool
     Farewell:bool
     Other:bool

class FieldToSearch(BaseModel):
#   property_name: bool = Field(..., description="Whether the user is asking about the name/type of the property")
    #society: bool = Field(..., description="Whether the query involves the name of the society or project")
    Price_in_Crore: bool = Field(..., description="Is the user concerned with price (e.g. in Lacs or Crores)?")
    Rate_rs_sqft: bool = Field(..., description="Does the query mention rate per sq.ft?")
    AreaType: bool = Field(..., description="Is the user interested in the area of the flat and its type (e.g. carpet, built-up)?")
    Area_in_sq_meter: bool = Field(None, description="Does the query mention about the area or space of the property")
    bedRoom: bool = Field(..., description="Is the number of bedrooms or BHK mentioned?")
    bathroom: bool = Field(..., description="Does the query include details about bathrooms?")
    balcony: bool = Field(..., description="Is there a mention of balconies?")
    additionalRoom: bool = Field(..., description="Are extra rooms (servant/study/store) discussed/asked?")
    address: bool = Field(..., description="Is the location or full address part of the query?")
    floorNum: bool = Field(..., description="Does the query talk about the floor")
    Totalfloor: bool = Field(..., description="Does the query talk about total floors?")
    facing: bool = Field(..., description="Is the direction of the property mentioned (e.g. East-facing)?")
    agePossession: bool = Field(..., description="Does the user ask for construction age or possession date?")
    nearbyLocations: bool = Field(..., description="Does the user ask nearest to particular thing")
#     description: bool = Field(..., description="Is the user asking for a general description of the property?")
    furnishDetails: bool = Field(..., description="Is the furnishing (e.g. AC, wardrobe) mentioned?")
    features: bool = Field(..., description="Are amenities or society features mentioned?")
    rating: bool = Field(..., description="Is there a reference to rating for environment, safety,LifeStyle,Connectivity etc.?")

class AreaTypeEnum(str, Enum):
    carpet = "Carpet"
    built_up = "Built Up"
    super_built_up = "Super Built up"


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
    storeandservant="Store Room,Servant Room"
    storeandstudy='Store Room,Study Room'
    storeandpooja='Store Room,Pooja Room'
    studyandpooja='Study Room,Pooja Room'
    studyandstore='Study Room,Store Room'
    studyandservant='Study Room,Servant Room'
    poojaandstudy='Pooja Room,Study Room'
    poojaandservant='Pooja Room,Servant Room'
    poojaandstore='Pooja Room,Store Room'
    servantandpooja='Servant Room,Pooja Room'
    servantandstudy='Servant Room,Study Room'
    servantandstore='Servant Room,Store Room'

class SearchData(BaseModel):
    Price_in_Crore: Optional[float] = Field(None, description="Price mentioned(should be in Crore)?")
    Rate_rs_sqft: Optional[int] = Field(None, description="Does the query mention rate per sq.ft?")
    AreaType: Optional[AreaTypeEnum] = Field(None, description="Type of area (Carpet, Built Up, Super Built Up)")
    Area_in_sq_meter: Optional[float] = Field(None, description="Area in sq.meter")

    bedRoom: Optional[int] = Field(None, description="Number of bedrooms or BHK mentioned")
    bathroom: Optional[int] = Field(None, description="Number of bathrooms mentioned")
    balcony: Optional[int] = Field(None, description="Number of balconies mentioned")

    additionalRoom: Optional[AdditionalRoomType] = Field(None, description="Type of extra room if mentioned")

    floorNum: Optional[int] = Field(None, description="Floor number if mentioned. Note:0th floor is the ground floor")
    Totalfloor: Optional[int] = Field(None, description="Total floors in the building if mentioned")

    facing: Optional[FacingDirection] = Field(None, description="Direction of the property if mentioned")

    agePossession: Optional[int] = Field(None, description="Age of construction or possession in years")

    connectivity_rating: Optional[bool] = Field(None, description="Whether ratings for connectivity/lifestyle/etc. are mentioned")


class ComparisonEnum(str, Enum):
    greater = "Greater than"
    lesser = "Lesser than"


class ApplyFilterToColumn(BaseModel):
    Price_in_Crore: Optional[ComparisonEnum] = Field(None, description="Filter on price in Crore if query mentioned greater than or less than  price or above or under for price striclty ")
    Rate_rs_sqft: Optional[ComparisonEnum] = Field(None, description="Filter on rate per sq.ft if query mention greater than or lesser or above or under for rate strictly ")  # Optional: include if needed
    Area_in_sq_meter: Optional[ComparisonEnum] = Field(None, description="Filter on area in square meters if query mention greater than or lesser than or above or under for area or space striclty")

    bedRoom: Optional[ComparisonEnum] = Field(None, description="Filter on number of bedrooms (BHK) if user query mention more than or less than or greater than or lesser than for area or space strictly")
    bathroom: Optional[ComparisonEnum] = Field(None, description="Filter on number of bathrooms if user query mention more than or less than or greater than or lesser than for bathroom  strictly ")
    balcony: Optional[ComparisonEnum] = Field(None, description="Filter on number of balconies if user query mention more than or less than or greater than or lesser than  for balcony strictly ")

    floorNum: Optional[ComparisonEnum] = Field(None, description="Filter on floor number if user query mention above or below for floor stricltly ")
    Totalfloor: Optional[ComparisonEnum] = Field(None, description="Filter on total number of floors  if the user query mention greater than or lesser than or more than or less than for Total floor ")



