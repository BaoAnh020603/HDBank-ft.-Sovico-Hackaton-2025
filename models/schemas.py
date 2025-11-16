from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Context Models
class ConversationContext(BaseModel):
    user_id: str
    intent: Optional[str] = None
    slots: Dict[str, Any] = {}
    booking_state: Dict[str, Any] = {}
    query_history: List[str] = []
    previous_intent: Optional[str] = None
    
    # Enhanced contexts with structured data
    flight_context: Optional['FlightContext'] = None
    hotel_context: Optional['HotelContext'] = None
    transfer_context: Optional['TransferContext'] = None
    combo_context: Optional['ComboContext'] = None
    user_profile: Optional['UserProfile'] = None
    
    # Trip planning context
    trip_context: Dict[str, Any] = {}
    destination_info: Dict[str, Any] = {}
    budget_context: Dict[str, Any] = {}
    group_context: Dict[str, Any] = {}
    
    last_updated: datetime = datetime.now()

# Agent Request/Response Models
class AgentRequest(BaseModel):
    intent: str
    slots: Dict[str, Any]
    context: ConversationContext
    user_input: Optional[str] = None  # For intelligent reasoning agents

class AgentResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str = ""

# Flight Models
class FlightInfo(BaseModel):
    service_id: str
    flight_id: str
    airline: str
    from_city: str
    to_city: str
    date: str
    time: str
    price: int
    seats_left: int
    class_type: str = "Economy"

class FlightSearchRequest(BaseModel):
    from_city: str
    to_city: str
    date: str
    time_range: Optional[str] = None
    class_type: str = "Economy"

# Price Models
class PriceRequest(BaseModel):
    service: str
    from_city: str
    to_city: str
    date: str
    filter_type: str = "cheapest"  # cheapest, fastest, best

class PriceResponse(BaseModel):
    best_price: int
    service_id: str
    flight_id: Optional[str] = None
    time: Optional[str] = None
    seats_left: Optional[int] = None

# Booking Models
class BookingRequest(BaseModel):
    user_id: str
    services: List[Dict[str, Any]]
    payment_method: str = "credit_card"

class BookingResponse(BaseModel):
    booking_id: str
    payment_code: str
    status: str
    deadline: str
    total_amount: int

# Hotel Models
class HotelInfo(BaseModel):
    service_id: str
    name: str
    location: str
    rating: int
    price_per_night: int
    rooms_left: int
    type: str
    amenities: List[str] = []
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    nights: Optional[int] = 1
    guests: Optional[int] = 2

class HotelSearchRequest(BaseModel):
    city: str
    check_in: str
    check_out: str
    guests: int = 2
    rooms: int = 1
    rating_min: Optional[int] = None
    price_max: Optional[int] = None

# Transfer Models
class TransferInfo(BaseModel):
    service_id: str
    type: str
    from_location: str
    to_location: str
    price: int
    vehicle: str
    duration: Optional[str] = None
    pickup_time: Optional[str] = None
    passengers: Optional[int] = 2

class TransferSearchRequest(BaseModel):
    city: str
    pickup_location: str
    drop_location: str
    pickup_time: Optional[str] = None
    passengers: int = 2
    vehicle_type: Optional[str] = None

# Combo Models
class ComboItem(BaseModel):
    type: str  # flight, hotel, transfer
    service_id: str
    name: str
    price: int
    details: Dict[str, Any] = {}

class ComboResponse(BaseModel):
    combo_id: str
    name: str
    items: List[ComboItem]
    total_price: int
    discount: int
    final_price: int
    validity: Optional[str] = None

# User Profile Models
class PassengerInfo(BaseModel):
    full_name: str
    date_of_birth: Optional[str] = None
    passport_number: Optional[str] = None
    nationality: Optional[str] = "Vietnam"
    phone: Optional[str] = None
    email: Optional[str] = None

class UserProfile(BaseModel):
    contact_info: Dict[str, str] = {}
    passengers: List[PassengerInfo] = []
    preferences: Dict[str, Any] = {}
    payment_methods: List[str] = []
    booking_history: List[str] = []

# Enhanced Context Models
class FlightContext(BaseModel):
    search_criteria: Dict[str, Any] = {}
    search_results: List[FlightInfo] = []
    selected_flights: List[str] = []
    preferences: Dict[str, Any] = {}

class HotelContext(BaseModel):
    search_criteria: Dict[str, Any] = {}
    search_results: List[HotelInfo] = []
    selected_hotels: List[str] = []
    preferences: Dict[str, Any] = {}

class TransferContext(BaseModel):
    search_criteria: Dict[str, Any] = {}
    search_results: List[TransferInfo] = []
    selected_transfers: List[str] = []
    preferences: Dict[str, Any] = {}

class ComboContext(BaseModel):
    available_combos: List[ComboResponse] = []
    selected_combo: Optional[str] = None
    combo_preferences: Dict[str, Any] = {}