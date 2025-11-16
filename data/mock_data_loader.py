"""
Mock data loader - Tải dữ liệu từ file JSON đã generate
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class MockDataLoader:
    def __init__(self, data_file: str = None):
        """Khởi tạo loader với file data"""
        if not data_file:
            # Tìm file mới nhất trong thư mục generated
            generated_dir = os.path.join(os.path.dirname(__file__), "generated")
            if os.path.exists(generated_dir):
                files = [f for f in os.listdir(generated_dir) if f.startswith("vietjet_mock_data_") and f.endswith(".json")]
                if files:
                    data_file = os.path.join(generated_dir, sorted(files)[-1])
        
        if not data_file or not os.path.exists(data_file):
            raise FileNotFoundError("Không tìm thấy file mock data. Hãy chạy scripts/generate_mock_data.py trước.")
        
        self.data_file = data_file
        self.data = self._load_data()
        
    def _load_data(self) -> Dict:
        """Load data từ file JSON"""
        with open(self.data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_flights_by_route_and_date(self, from_city: str, to_city: str, date: str) -> List[Dict]:
        """Lấy chuyến bay theo tuyến và ngày - Generate động nếu cần"""
        target_date = self._parse_date(date)
        from_code, to_code = self._get_airport_codes(from_city, to_city)
        
        # Kiểm tra xem có dữ liệu không
        flights = self._get_existing_flights(from_code, to_code, target_date)
        
        if not flights:
            # Generate dữ liệu động nếu không có
            flights = self._generate_dynamic_flights(from_city, to_city, from_code, to_code, target_date)
        
        return flights
    
    def _parse_date(self, date: str) -> datetime:
        """Parse ngày linh hoạt"""
        try:
            if date in ["hôm nay", "today"]:
                return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            elif date in ["ngày mai", "tomorrow"]:
                return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            elif "/" in date:
                return datetime.strptime(date, "%d/%m/%Y")
            else:
                return datetime.strptime(date, "%Y-%m-%d")
        except:
            return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    def _get_airport_codes(self, from_city: str, to_city: str) -> tuple:
        """Lấy airport codes"""
        city_to_code = {}
        for code, airport in self.data["airports"].items():
            city_to_code[airport["city"]] = code
        
        from_code = city_to_code.get(from_city, from_city)
        to_code = city_to_code.get(to_city, to_city)
        return from_code, to_code
    
    def _get_existing_flights(self, from_code: str, to_code: str, target_date: datetime) -> List[Dict]:
        """Lấy flights có sẵn"""
        route_key = f"{from_code}-{to_code}"
        date_key = target_date.strftime("%Y-%m-%d")
        
        if date_key in self.data["flights_by_date"] and route_key in self.data["flights_by_date"][date_key]:
            flights = self.data["flights_by_date"][date_key][route_key]
            return self._convert_flights(flights, target_date)
        return []
    
    def _generate_dynamic_flights(self, from_city: str, to_city: str, from_code: str, to_code: str, target_date: datetime) -> List[Dict]:
        """Generate flights động cho bất kỳ tuyến và ngày nào"""
        import random
        
        # Tạo seed cố định dựa trên route và ngày để đảm bảo dữ liệu nhất quán
        seed_string = f"{from_code}-{to_code}-{target_date.strftime('%Y-%m-%d')}"
        random.seed(hash(seed_string) % (2**32))
        
        # Kiểm tra xem có phải tuyến hợp lệ không
        if not self._is_valid_route(from_code, to_code):
            return []
        
        flights = []
        flight_times = ["06:00", "08:30", "10:15", "12:45", "15:20", "17:30", "19:45", "21:15"]
        base_prices = {"HAN-SGN": 1500000, "SGN-HAN": 1500000, "SGN-DAD": 1200000, "DAD-SGN": 1200000}
        
        route_key = f"{from_code}-{to_code}"
        base_price = base_prices.get(route_key, 1300000)
        
        # Số lượng chuyến bay cố định dựa trên seed
        num_flights = 5 + (hash(seed_string) % 4)  # 5-8 chuyến
        
        for i, time in enumerate(flight_times[:num_flights]):
            # Tạo giá và mã chuyến cố định dựa trên index
            price_variation = 0.8 + (i * 0.15)  # Giá tăng dần theo giờ
            flight_codes = ["VJ112", "VJ114", "VJ116", "VJ118", "VJ120", "VJ122", "VJ124", "VJ126"]
            
            flight = {
                "service_id": f"F{11000 + i * 100}",
                "flight_id": flight_codes[i % len(flight_codes)],
                "airline": "VietJet Air",
                "airline_code": "VJ",
                "from_city": from_city,
                "to_city": to_city,
                "from_code": from_code,
                "to_code": to_code,
                "from_airport": self._get_airport_name(from_code),
                "to_airport": self._get_airport_name(to_code),
                "route": f"{from_code} → {to_code}",
                "route_detail": f"{self._get_airport_name(from_code)} → {self._get_airport_name(to_code)}",
                "date": target_date.strftime("%d/%m/%Y"),
                "time": time,
                "price": int(base_price * price_variation),
                "seats_left": 2 + (i % 6),  # 2-7 chỗ, cố định theo index
                "class_type": "Economy",
                "quality": "sovico_premium",
                "duration": self._get_flight_duration(from_code, to_code),
                "date_display": target_date.strftime("%A, %d/%m/%Y"),
                "weekday": target_date.strftime("%A"),
                "is_weekend": target_date.weekday() >= 5
            }
            flights.append(flight)
        
        return flights
    
    def _is_valid_route(self, from_code: str, to_code: str) -> bool:
        """Kiểm tra tuyến hợp lệ"""
        valid_routes = ["HAN-SGN", "SGN-HAN", "SGN-DAD", "DAD-SGN", "SGN-PQC", "PQC-SGN"]
        return f"{from_code}-{to_code}" in valid_routes
    
    def _get_airport_name(self, code: str) -> str:
        """Lấy tên sân bay"""
        airport_names = {
            "HAN": "Sân bay Nội Bài",
            "SGN": "Sân bay Tân Sơn Nhất",
            "DAD": "Sân bay Đà Nẵng",
            "PQC": "Sân bay Phú Quốc"
        }
        return airport_names.get(code, f"Sân bay {code}")
    
    def _get_flight_duration(self, from_code: str, to_code: str) -> str:
        """Lấy thời gian bay"""
        durations = {
            "HAN-SGN": "2h05m", "SGN-HAN": "2h05m",
            "SGN-DAD": "1h25m", "DAD-SGN": "1h25m",
            "SGN-PQC": "50m", "PQC-SGN": "50m"
        }
        return durations.get(f"{from_code}-{to_code}", "1h30m")
    
    def _convert_flights(self, flights: List[Dict], target_date: datetime) -> List[Dict]:
        """Convert flights với ngày đích"""
        for flight in flights:
            flight["date"] = target_date.strftime("%d/%m/%Y")
            flight["date_display"] = target_date.strftime("%A, %d/%m/%Y")
        
        converted_flights = []
        for flight in flights:
            converted_flight = {
                "service_id": flight["service_id"],
                "flight_id": flight["flight_id"],
                "airline": flight["airline"],
                "airline_code": flight["airline_code"],
                "from_city": flight["from_city"],
                "to_city": flight["to_city"],
                "from_code": flight["from_code"],
                "to_code": flight["to_code"],
                "from_airport": flight.get("from_airport", self._get_airport_name(flight["from_code"])),
                "to_airport": flight.get("to_airport", self._get_airport_name(flight["to_code"])),
                "route": flight["route"],
                "route_detail": f"{flight.get('from_airport', '')} → {flight.get('to_airport', '')}",
                "date": flight["date"],
                "time": flight.get("departure_time", flight.get("time")),
                "price": flight["price"],
                "seats_left": flight["seats_left"],
                "class_type": flight["class_type"],
                "quality": "sovico_premium",
                "duration": flight.get("duration", "2h00m"),
                "date_display": flight["date_display"],
                "weekday": flight.get("weekday", target_date.strftime("%A")),
                "is_weekend": flight.get("is_weekend", target_date.weekday() >= 5)
            }
            converted_flights.append(converted_flight)
        
        return converted_flights
    
    def get_flight_by_code(self, flight_code: str, from_city: str = None, to_city: str = None, date: str = None) -> Optional[Dict]:
        """Tìm chuyến bay theo mã chuyến bay"""
        if from_city and to_city and date:
            flights = self.get_flights_by_route_and_date(from_city, to_city, date)
            for flight in flights:
                if flight["flight_id"] == flight_code:
                    return flight
        
        # Tìm trong tất cả ngày nếu không có thông tin cụ thể
        for date_data in self.data["flights_by_date"].values():
            for route_flights in date_data.values():
                for flight in route_flights:
                    if flight["flight_id"] == flight_code:
                        return self._convert_flight_format(flight)
        
        return None
    
    def _convert_flight_format(self, flight: Dict) -> Dict:
        """Chuyển đổi format flight để tương thích"""
        return {
            "service_id": flight["service_id"],
            "flight_id": flight["flight_id"],
            "airline": flight["airline"],
            "airline_code": flight["airline_code"],
            "from_city": flight["from_city"],
            "to_city": flight["to_city"],
            "from_code": flight["from_code"],
            "to_code": flight["to_code"],
            "route": flight["route"],
            "date": flight["date"],
            "time": flight["departure_time"],
            "price": flight["price"],
            "seats_left": flight["seats_left"],
            "class_type": flight["class_type"],
            "quality": "sovico_premium",
            "duration": flight["duration"],
            "aircraft": flight["aircraft"],
            "seating": flight["seating"],
            "baggage": flight["baggage"],
            "services": flight["services"],
            "pricing": {
                "base_fare": flight["base_fare"],
                "taxes_fees": flight["taxes_fees"],
                "service_fee": flight["service_fee"],
                "total": flight["price"],
                "currency": flight["currency"]
            },
            "policies": flight["policies"]
        }

# Global instance
mock_data_loader = None

def get_mock_data_loader():
    """Lấy instance của mock data loader"""
    global mock_data_loader
    if mock_data_loader is None:
        mock_data_loader = MockDataLoader()
    return mock_data_loader

# Compatibility functions cho hệ thống cũ
def get_flights_by_route(from_city: str, to_city: str, date: str = None):
    """Compatibility function"""
    if not date:
        date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    loader = get_mock_data_loader()
    return loader.get_flights_by_route_and_date(from_city, to_city, date)

def get_cheapest_flight(from_city: str, to_city: str, date: str = None):
    """Lấy chuyến bay rẻ nhất"""
    flights = get_flights_by_route(from_city, to_city, date)
    if flights:
        return min(flights, key=lambda x: x["price"])
    return None

def get_flight_by_flight_code(flight_code: str, from_city: str = None, to_city: str = None, date: str = None):
    """Tìm chuyến bay theo mã"""
    loader = get_mock_data_loader()
    return loader.get_flight_by_code(flight_code, from_city, to_city, date)