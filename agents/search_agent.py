from typing import Dict, Any
from .base_agent import BaseAgent
from models.schemas import AgentRequest, AgentResponse
# Import cũ - sẽ thay thế bằng loader mới trong các function

class SearchAgent(BaseAgent):
    """Agent for searching flights, hotels, transfers"""
    
    def __init__(self):
        super().__init__("SearchAgent")
    
    def process_sync(self, request: AgentRequest) -> AgentResponse:
        """Synchronous process method"""
        slots = request.slots
        service_type = slots.get("service", "flight")
        
        if service_type == "flight":
            return self._search_flights_sync(slots)
        else:
            return self.create_response(
                success=False,
                data={},
                message=f"Service type {service_type} not supported yet"
            )
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        """Process search request"""
        slots = request.slots
        context = request.context
        
        # Determine service type
        service_type = slots.get("service", "flight")
        
        if service_type == "flight":
            return await self._search_flights(slots, context)
        elif service_type == "hotel":
            return await self._search_hotels(slots, context)
        else:
            return self.create_response(
                success=False,
                data={},
                message=f"Service type {service_type} not supported yet"
            )
    
    async def _search_flights(self, slots: Dict[str, Any], context=None) -> AgentResponse:
        """Search for flights và lưu vào session context"""
        from_city = slots.get("from_city")
        to_city = slots.get("to_city")
        
        # Xử lý missing info một cách thân thiện
        if not from_city and not to_city:
            return self.create_response(
                success=True,
                data={"need_info": "route"},
                message="😊 Tôi có thể giúp bạn tìm vé máy bay! Bạn muốn bay từ đâu đến đâu ạ?"
            )
        elif not from_city:
            city_name = self._get_city_name(to_city)
            return self.create_response(
                success=True,
                data={"need_info": "from_city", "to_city": to_city},
                message=f"😊 Bạn muốn bay từ đâu đến {city_name} ạ?"
            )
        elif not to_city:
            city_name = self._get_city_name(from_city)
            return self.create_response(
                success=True,
                data={"need_info": "to_city", "from_city": from_city},
                message=f"😊 Từ {city_name} bạn muốn bay đến đâu ạ?"
            )
        
        from_city = slots["from_city"]
        to_city = slots["to_city"]
        date = slots.get("date")
        
        # Search flights - sử dụng loader mới để đảm bảo dữ liệu nhất quán
        from data.mock_data_loader import get_mock_data_loader
        loader = get_mock_data_loader()
        flights = loader.get_flights_by_route_and_date(from_city, to_city, date or "hôm nay")
        
        print(f"DEBUG: Search flights - from: {from_city}, to: {to_city}, date: {date}")
        print(f"DEBUG: Found {len(flights)} flights")
        
        if not flights:
            return self.create_response(
                success=False,
                data={"flights": []},
                message=f"😔 Không tìm thấy chuyến bay từ {self._get_city_name(from_city)} đến {self._get_city_name(to_city)}. Bạn thử ngày khác nhé!"
            )
        
        # Filter by time if specified
        time_filter = slots.get("time")
        if time_filter:
            # Simple time filtering (within 2 hours)
            filtered_flights = []
            for flight in flights:
                flight_time = flight["time"]
                # Simple time comparison logic
                filtered_flights.append(flight)
            flights = filtered_flights
        
        # Update session context với flight search results
        if context and hasattr(context, 'flight_context'):
            if not context.flight_context:
                from models.schemas import FlightContext
                context.flight_context = FlightContext()
            
            # Save search criteria
            context.flight_context.search_criteria = {
                "from_city": from_city,
                "to_city": to_city, 
                "date": date,
                "time_filter": time_filter
            }
            
            # Convert flights to FlightInfo objects and save
            from models.schemas import FlightInfo
            flight_infos = []
            for flight in flights:
                flight_info = FlightInfo(
                    service_id=flight["service_id"],
                    flight_id=flight["flight_id"],
                    airline=flight["airline"],
                    from_city=flight["from_city"],
                    to_city=flight["to_city"],
                    date=flight["date"],
                    time=flight["time"],
                    price=flight["price"],
                    seats_left=flight["seats_left"],
                    class_type=flight["class_type"]
                )
                flight_infos.append(flight_info)
            
            context.flight_context.search_results = flight_infos
            print(f"DEBUG: Saved {len(flight_infos)} flights to session context")
        
        return self.create_response(
            success=True,
            data={"flights": flights},
            message=f"🛫 Tìm thấy {len(flights)} chuyến bay từ {self._get_city_name(from_city)} đến {self._get_city_name(to_city)}"
        )
    
    def _search_flights_sync(self, slots: Dict[str, Any]) -> AgentResponse:
        """Synchronous version of flight search"""
        from_city = self._normalize_city(slots.get("from_city", ""))
        to_city = self._normalize_city(slots.get("to_city", ""))
        date = self._normalize_date(slots.get("date"))
        
        print(f"DEBUG: Normalized - from: {from_city}, to: {to_city}, date: {date}")
        
        if not from_city or not to_city:
            return self.create_response(
                success=False,
                data={},
                message="Cần thông tin điểm đi và điểm đến"
            )
        
        # Sử dụng loader mới để đảm bảo dữ liệu nhất quán
        from data.mock_data_loader import get_mock_data_loader
        loader = get_mock_data_loader()
        flights = loader.get_flights_by_route_and_date(from_city, to_city, date or "hôm nay")
        print(f"DEBUG: Found {len(flights)} flights")
        
        if not flights:
            return self.create_response(
                success=False,
                data={"flights": []},
                message=f"Không tìm thấy chuyến bay từ {from_city} đến {to_city} ngày {date}"
            )
        
        # Check if user wants cheapest flight
        user_input = slots.get('user_input', '')
        if 'rẻ nhất' in user_input or 'giá rẻ' in user_input:
            # Sort by price and return only cheapest
            flights = sorted(flights, key=lambda x: x['price'])
            flights = [flights[0]]  # Only cheapest
            message = f"Vé rẻ nhất từ {from_city} đến {to_city} ngày {date}: {flights[0]['airline']} {flights[0]['flight_id']} - {flights[0]['price']:,} VNĐ lúc {flights[0]['time']}"
        else:
            message = f"Tìm thấy {len(flights)} chuyến bay từ {from_city} đến {to_city} ngày {date}"
        
        return self.create_response(
            success=True,
            data={"flights": flights},
            message=message
        )
    
    def _normalize_city(self, city: str) -> str:
        """Normalize city names"""
        if not city:
            return ""
        
        city_lower = city.lower().strip()
        city_map = {
            "hồ chí minh": "Ho Chi Minh City",
            "tp.hcm": "Ho Chi Minh City", 
            "hcm": "Ho Chi Minh City",
            "sài gòn": "Ho Chi Minh City",
            "hà nội": "Hanoi",
            "hanoi": "Hanoi",
            "hn": "Hanoi",
            "đà nẵng": "Da Nang",
            "da nang": "Da Nang",
            "dn": "Da Nang"
        }
        
        return city_map.get(city_lower, city)
        

    
    def _normalize_date(self, date: str) -> str:
        """Normalize date formats - linh hoạt với mọi format"""
        from datetime import datetime, timedelta
        import re
        
        if not date:
            return datetime.now().strftime("%Y-%m-%d")
        
        date_str = date.lower().strip()
        current_year = datetime.now().year
        
        # Xử lý các từ khóa thời gian
        if date_str in ["hôm nay", "today"]:
            return datetime.now().strftime("%Y-%m-%d")
        elif date_str in ["ngày mai", "tomorrow"]:
            return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Xử lý format dd/mm hoặc dd/mm/yyyy
        date_patterns = [
            (r"^(\d{1,2})/(\d{1,2})/(\d{4})$", "%d/%m/%Y"),  # dd/mm/yyyy
            (r"^(\d{1,2})/(\d{1,2})$", f"%d/%m/{current_year}"),  # dd/mm -> dd/mm/current_year
            (r"^(\d{4})-(\d{1,2})-(\d{1,2})$", "%Y-%m-%d"),  # yyyy-mm-dd
        ]
        
        for pattern, format_str in date_patterns:
            match = re.match(pattern, date)
            if match:
                try:
                    if "/{current_year}" in format_str:
                        # Thêm năm hiện tại cho format dd/mm
                        date_with_year = f"{date}/{current_year}"
                        parsed_date = datetime.strptime(date_with_year, "%d/%m/%Y")
                    else:
                        parsed_date = datetime.strptime(date, format_str.replace(f"/{current_year}", "/" + str(current_year)))
                    return parsed_date.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        
        # Nếu không parse được, trả về ngày mai
        return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    def _get_city_name(self, city_code: str) -> str:
        """Convert city code to readable name"""
        city_names = {
            "Hanoi": "Hà Nội", "Ho Chi Minh City": "TP.HCM", "Da Nang": "Đà Nẵng",
            "Phu Quoc": "Phú Quốc", "Nha Trang": "Nha Trang", "Da Lat": "Đà Lạt",
            "Can Tho": "Cần Thơ", "Hai Phong": "Hải Phòng", "Hue": "Huế",
            "Vung Tau": "Vũng Tàu", "Quy Nhon": "Quy Nhon"
        }
        return city_names.get(city_code, city_code)
    
    async def _search_hotels(self, slots: Dict[str, Any], context=None) -> AgentResponse:
        """Search for hotels và lưu vào session context"""
        city = slots.get("city")
        check_in = slots.get("check_in")
        check_out = slots.get("check_out")
        guests = slots.get("guests", 2)
        
        if not city:
            return self.create_response(
                success=True,
                data={"need_info": "city"},
                message="🏨 Bạn muốn tìm khách sạn ở thành phố nào ạ?"
            )
        
        # Get hotels from mock data
        try:
            from data.mock_data_loader import hotel_generator
        except ImportError:
            from data.mock_data import hotel_generator
        hotels = hotel_generator.generate_hotels(city, check_in, 1)
        
        if not hotels:
            return self.create_response(
                success=False,
                data={"hotels": []},
                message=f"😔 Không tìm thấy khách sạn ở {city}. Bạn thử thành phố khác nhé!"
            )
        
        # Update session context với hotel search results
        if context and hasattr(context, 'hotel_context'):
            if not context.hotel_context:
                from models.schemas import HotelContext
                context.hotel_context = HotelContext()
            
            # Save search criteria
            context.hotel_context.search_criteria = {
                "city": city,
                "check_in": check_in,
                "check_out": check_out,
                "guests": guests
            }
            
            # Convert hotels to HotelInfo objects and save
            from models.schemas import HotelInfo
            hotel_infos = []
            for hotel in hotels:
                hotel_info = HotelInfo(
                    service_id=hotel["service_id"],
                    name=hotel["name"],
                    location=hotel["location"],
                    rating=hotel["rating"],
                    price_per_night=hotel["price_per_night"],
                    rooms_left=hotel["rooms_left"],
                    type=hotel["type"],
                    guests=guests
                )
                hotel_infos.append(hotel_info)
            
            context.hotel_context.search_results = hotel_infos
            print(f"DEBUG: Saved {len(hotel_infos)} hotels to session context")
        
        return self.create_response(
            success=True,
            data={"hotels": hotels},
            message=f"🏨 Tìm thấy {len(hotels)} khách sạn ở {city}"
        )