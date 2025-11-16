#!/usr/bin/env python3
"""
Script tạo mock data đầy đủ và chi tiết như thực tế cho hệ thống booking VietJet
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

class MockDataGenerator:
    def __init__(self):
        self.base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Thông tin hãng bay
        self.airlines = {
            "VJ": {"name": "VietJet Air", "iata": "VJ", "icao": "VJC", "country": "Vietnam"}
        }
        
        # Sân bay Việt Nam
        self.airports = {
            "HAN": {"name": "Sân bay Nội Bài", "city": "Hanoi", "country": "VN", "timezone": "UTC+7"},
            "SGN": {"name": "Sân bay Tân Sơn Nhất", "city": "Ho Chi Minh City", "country": "VN", "timezone": "UTC+7"},
            "DAD": {"name": "Sân bay Đà Nẵng", "city": "Da Nang", "country": "VN", "timezone": "UTC+7"},
            "PQC": {"name": "Sân bay Phú Quốc", "city": "Phu Quoc", "country": "VN", "timezone": "UTC+7"},
            "CXR": {"name": "Sân bay Cam Ranh", "city": "Nha Trang", "country": "VN", "timezone": "UTC+7"},
            "DLI": {"name": "Sân bay Liên Khương", "city": "Da Lat", "country": "VN", "timezone": "UTC+7"},
            "VCA": {"name": "Sân bay Cần Thơ", "city": "Can Tho", "country": "VN", "timezone": "UTC+7"},
            "HPH": {"name": "Sân bay Cát Bi", "city": "Hai Phong", "country": "VN", "timezone": "UTC+7"},
            "HUI": {"name": "Sân bay Phú Bài", "city": "Hue", "country": "VN", "timezone": "UTC+7"}
        }
        
        # Lịch bay thực tế VietJet
        self.flight_schedules = {
            "HAN-SGN": [
                {"flight": "VJ111", "times": ["05:30", "08:15", "12:45", "16:35", "20:15"], "aircraft": "A321", "frequency": "daily"},
                {"flight": "VJ113", "times": ["06:45", "10:30", "14:20", "18:50"], "aircraft": "A320", "frequency": "daily"},
                {"flight": "VJ115", "times": ["07:00", "11:15", "15:30", "19:45"], "aircraft": "A321", "frequency": "daily"}
            ],
            "SGN-HAN": [
                {"flight": "VJ112", "times": ["05:45", "09:30", "13:15", "17:00", "20:45"], "aircraft": "A321", "frequency": "daily"},
                {"flight": "VJ114", "times": ["06:30", "10:15", "14:00", "18:30"], "aircraft": "A320", "frequency": "daily"},
                {"flight": "VJ116", "times": ["07:45", "11:30", "15:45", "19:15"], "aircraft": "A321", "frequency": "daily"}
            ],
            "SGN-DAD": [
                {"flight": "VJ321", "times": ["06:00", "10:45", "15:20", "19:30"], "aircraft": "A320", "frequency": "daily"},
                {"flight": "VJ323", "times": ["07:15", "12:00", "16:35", "20:45"], "aircraft": "A321", "frequency": "daily"}
            ],
            "DAD-SGN": [
                {"flight": "VJ322", "times": ["07:30", "12:15", "16:50", "21:00"], "aircraft": "A320", "frequency": "daily"},
                {"flight": "VJ324", "times": ["08:45", "13:30", "18:05"], "aircraft": "A321", "frequency": "daily"}
            ],
            "SGN-PQC": [
                {"flight": "VJ621", "times": ["06:30", "11:15", "16:00", "20:30"], "aircraft": "A320", "frequency": "daily"},
                {"flight": "VJ623", "times": ["07:45", "12:30", "17:15"], "aircraft": "A321", "frequency": "daily"}
            ],
            "PQC-SGN": [
                {"flight": "VJ622", "times": ["08:15", "13:00", "17:45", "22:15"], "aircraft": "A320", "frequency": "daily"},
                {"flight": "VJ624", "times": ["09:30", "14:15", "19:00"], "aircraft": "A321", "frequency": "daily"}
            ]
        }
        
        # Thông tin tuyến bay
        self.routes = {
            "HAN-SGN": {"distance": 1166, "base_price": 1299000, "duration": "2h05m", "popular": True},
            "SGN-HAN": {"distance": 1166, "base_price": 1299000, "duration": "2h05m", "popular": True},
            "SGN-DAD": {"distance": 647, "base_price": 999000, "duration": "1h25m", "popular": True},
            "DAD-SGN": {"distance": 647, "base_price": 999000, "duration": "1h25m", "popular": True},
            "SGN-PQC": {"distance": 289, "base_price": 699000, "duration": "50m", "popular": True},
            "PQC-SGN": {"distance": 289, "base_price": 699000, "duration": "50m", "popular": True}
        }
        
        # Cấu hình máy bay
        self.aircraft_configs = {
            "A320": {
                "manufacturer": "Airbus",
                "model": "A320-200",
                "total_seats": 180,
                "layout": "3-3",
                "rows": 30,
                "seat_map": "A-B-C | D-E-F",
                "premium_rows": [1, 2],
                "exit_rows": [12, 13],
                "wifi": True,
                "entertainment": False
            },
            "A321": {
                "manufacturer": "Airbus", 
                "model": "A321-200",
                "total_seats": 230,
                "layout": "3-3",
                "rows": 38,
                "seat_map": "A-B-C | D-E-F",
                "premium_rows": [1, 2, 3],
                "exit_rows": [14, 15],
                "wifi": True,
                "entertainment": True
            }
        }
    
    def generate_flights_for_date(self, from_code: str, to_code: str, date: datetime) -> List[Dict]:
        """Tạo chuyến bay cho ngày cụ thể"""
        route_key = f"{from_code}-{to_code}"
        
        if route_key not in self.flight_schedules or route_key not in self.routes:
            return []
        
        flights = []
        schedules = self.flight_schedules[route_key]
        route_info = self.routes[route_key]
        
        days_ahead = (date - self.base_date).days
        day_of_week = date.weekday()
        
        for schedule in schedules:
            flight_num = int(schedule["flight"][2:])
            
            # Số chuyến bay theo ngày trong tuần
            if day_of_week in [5, 6]:  # Cuối tuần
                num_flights = min(len(schedule["times"]), 4)
            elif day_of_week in [0, 4]:  # Đầu/cuối tuần làm việc
                num_flights = min(len(schedule["times"]), 3)
            else:  # Giữa tuần
                num_flights = min(len(schedule["times"]), 2)
            
            # Chọn giờ bay
            start_idx = flight_num % max(1, len(schedule["times"]) - num_flights + 1)
            selected_times = schedule["times"][start_idx:start_idx + num_flights]
            
            for time_str in selected_times:
                flight_data = self._create_flight_data(
                    schedule, time_str, route_info, date, days_ahead, from_code, to_code
                )
                flights.append(flight_data)
        
        return sorted(flights, key=lambda x: x["price"])
    
    def _create_flight_data(self, schedule: Dict, time_str: str, route_info: Dict, 
                           date: datetime, days_ahead: int, from_code: str, to_code: str) -> Dict:
        """Tạo dữ liệu chi tiết cho 1 chuyến bay"""
        
        flight_id = schedule["flight"]
        aircraft_type = schedule["aircraft"]
        time_hour = int(time_str.split(':')[0])
        
        # Tính giá
        price = self._calculate_price(route_info["base_price"], days_ahead, time_hour, date.weekday())
        
        # Tính số ghế còn lại
        seats_left = self._calculate_available_seats(flight_id, time_hour, date.weekday(), days_ahead)
        
        # Thông tin máy bay
        aircraft_config = self.aircraft_configs[aircraft_type]
        
        # Ghế còn trống
        available_seats = self._generate_available_seats(aircraft_config, seats_left)
        
        return {
            # Thông tin cơ bản
            "service_id": f"F{flight_id[2:]}{time_hour:02d}",
            "flight_id": flight_id,
            "airline": self.airlines["VJ"]["name"],
            "airline_code": "VJ",
            
            # Tuyến bay
            "from_code": from_code,
            "to_code": to_code,
            "from_airport": self.airports[from_code]["name"],
            "to_airport": self.airports[to_code]["name"],
            "from_city": self.airports[from_code]["city"],
            "to_city": self.airports[to_code]["city"],
            "route": f"{from_code} → {to_code}",
            "distance": route_info["distance"],
            
            # Thời gian
            "date": date.strftime("%d/%m/%Y"),
            "date_display": self._get_vietnamese_date_display(date),
            "weekday": self._get_vietnamese_weekday(date.weekday()),
            "day_of_week": date.weekday(),
            "is_weekend": date.weekday() >= 5,
            "is_holiday": self._is_holiday(date),
            "season": self._get_season(date.month),
            "departure_time": time_str,
            "arrival_time": self._calculate_arrival_time(time_str, route_info["duration"]),
            "duration": route_info["duration"],
            
            # Giá vé
            "price": price,
            "base_fare": int(price * 0.7),
            "taxes_fees": int(price * 0.2),
            "service_fee": int(price * 0.1),
            "currency": "VND",
            
            # Ghế ngồi
            "seats_left": seats_left,
            "class_type": "Economy",
            "total_seats": aircraft_config["total_seats"],
            
            # Máy bay
            "aircraft": {
                "type": aircraft_type,
                "manufacturer": aircraft_config["manufacturer"],
                "model": aircraft_config["model"],
                "total_seats": aircraft_config["total_seats"],
                "seat_layout": aircraft_config["layout"],
                "wifi": aircraft_config["wifi"],
                "entertainment": aircraft_config["entertainment"]
            },
            
            # Ghế ngồi chi tiết
            "seating": {
                "available_seats": available_seats,
                "seat_map": aircraft_config["seat_map"],
                "premium_seats": self._get_premium_seats(aircraft_config),
                "exit_row_seats": self._get_exit_row_seats(aircraft_config)
            },
            
            # Hành lý
            "baggage": {
                "cabin": {"weight": "7kg", "dimensions": "56x36x23cm", "pieces": 1},
                "checked": {"included": "20kg", "max_weight": "32kg", "excess_fee": "200,000 VND/kg"},
                "special_items": {"sports": "Có phí bổ sung", "instruments": "Cần đăng ký trước"}
            },
            
            # Dịch vụ
            "services": {
                "meals": {"available": True, "price_range": "80,000-150,000 VND"},
                "beverages": {"complimentary": ["Nước lọc", "Trà", "Cà phê"]},
                "wifi": {"available": True, "fee": "50,000 VND"},
                "entertainment": {"streaming": "VieON miễn phí"}
            },
            
            # Chính sách
            "policies": {
                "cancellation": "Có thể hủy với phí 500,000 VND",
                "change": "Có thể đổi với phí 300,000 VND", 
                "refund": "Hoàn tiền 70% nếu hủy trước 24h",
                "check_in": "Mở check-in online 24h trước giờ bay"
            }
        }
    
    def _calculate_price(self, base_price: int, days_ahead: int, hour: int, day_of_week: int) -> int:
        """Tính giá vé dựa trên nhiều yếu tố"""
        price = base_price
        
        # Hệ số theo thời gian book trước
        if days_ahead <= 3:
            price *= 1.5
        elif days_ahead <= 7:
            price *= 1.2
        elif days_ahead >= 30:
            price *= 0.8
        
        # Hệ số theo giờ bay
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Giờ cao điểm
            price *= 1.1
        elif 12 <= hour <= 14:  # Giờ trưa
            price *= 0.95
        
        # Hệ số theo ngày trong tuần
        if day_of_week >= 5:  # Cuối tuần
            price *= 1.15
        
        # Biến động cố định dựa trên giờ
        fluctuation = 0.9 + ((hour * 60 + int(str(hour)[-1]) * 6) % 21) / 100
        price *= fluctuation
        
        return int(price)
    
    def _calculate_available_seats(self, flight_id: str, hour: int, day_of_week: int, days_ahead: int) -> int:
        """Tính số ghế còn lại"""
        flight_num = int(flight_id[2:])
        base_seats = 45 - (flight_num % 25)  # 20-45 ghế
        
        # Hệ số theo ngày trong tuần
        if day_of_week in [5, 6]:  # Cuối tuần
            day_factor = 0.6
        elif day_of_week in [0, 4]:  # Đầu/cuối tuần làm việc
            day_factor = 0.8
        else:  # Giữa tuần
            day_factor = 1.0
        
        # Hệ số theo giờ bay
        if 6 <= hour <= 8 or 17 <= hour <= 19:  # Giờ cao điểm
            time_factor = 0.5
        elif 9 <= hour <= 11 or 14 <= hour <= 16:  # Giờ tốt
            time_factor = 0.7
        else:  # Giờ thấp điểm
            time_factor = 0.9
        
        # Hệ số theo thời gian book trước
        if days_ahead >= 30:
            advance_factor = 1.0
        elif days_ahead >= 14:
            advance_factor = 0.8
        elif days_ahead >= 7:
            advance_factor = 0.6
        elif days_ahead >= 3:
            advance_factor = 0.4
        else:
            advance_factor = 0.2
        
        return max(1, int(base_seats * day_factor * time_factor * advance_factor))
    
    def _generate_available_seats(self, aircraft_config: Dict, seats_count: int) -> List[str]:
        """Tạo danh sách ghế còn trống"""
        if aircraft_config["total_seats"] == 180:  # A320
            all_seats = [
                "5A", "5B", "5F", "7C", "7D", "8A", "8E", "9B", "9F", "11A", "11C", "11D",
                "14B", "14C", "14E", "15A", "15F", "17C", "17D", "18B", "18E", "19A", "19F",
                "21C", "21D", "22A", "22B", "23E", "23F", "25B", "25C", "26A", "26D", "27F",
                "28C", "28E", "29A", "29B", "30D", "30F"
            ]
        else:  # A321
            all_seats = [
                "6A", "6B", "6F", "8C", "8D", "9A", "9E", "10B", "10F", "12A", "12C", "12D",
                "16B", "16C", "16E", "17A", "17F", "19C", "19D", "20B", "20E", "21A", "21F",
                "23C", "23D", "24A", "24B", "25E", "25F", "27B", "27C", "28A", "28D", "29F",
                "30C", "30E", "31A", "31B", "32D", "32F", "34A", "34C", "35B", "35E", "36F",
                "37A", "37D", "38B", "38C"
            ]
        
        return all_seats[:min(seats_count, len(all_seats))]
    
    def _get_premium_seats(self, aircraft_config: Dict) -> List[str]:
        """Lấy danh sách ghế premium"""
        premium_seats = []
        for row in aircraft_config["premium_rows"]:
            for letter in ['A', 'B', 'C', 'D', 'E', 'F']:
                premium_seats.append(f"{row}{letter}")
        return premium_seats
    
    def _get_exit_row_seats(self, aircraft_config: Dict) -> List[str]:
        """Lấy danh sách ghế thoát hiểm"""
        exit_seats = []
        for row in aircraft_config["exit_rows"]:
            for letter in ['A', 'B', 'C', 'D', 'E', 'F']:
                exit_seats.append(f"{row}{letter}")
        return exit_seats
    
    def _calculate_arrival_time(self, departure_time: str, duration: str) -> str:
        """Tính giờ đến"""
        dep_hour, dep_min = map(int, departure_time.split(':'))
        
        # Parse duration (e.g., "2h05m", "1h25m", "50m")
        if 'h' in duration:
            parts = duration.replace('m', '').split('h')
            dur_hours = int(parts[0])
            dur_mins = int(parts[1]) if len(parts) > 1 and parts[1] else 0
        else:
            dur_hours = 0
            dur_mins = int(duration.replace('m', ''))
        
        # Calculate arrival
        total_mins = dep_hour * 60 + dep_min + dur_hours * 60 + dur_mins
        arr_hour = (total_mins // 60) % 24
        arr_min = total_mins % 60
        
        return f"{arr_hour:02d}:{arr_min:02d}"
    
    def _get_vietnamese_weekday(self, day_of_week: int) -> str:
        """Chuyển đổi thứ sang tiếng Việt"""
        weekdays = {
            0: "Thứ Hai", 1: "Thứ Ba", 2: "Thứ Tư", 3: "Thứ Năm",
            4: "Thứ Sáu", 5: "Thứ Bảy", 6: "Chủ Nhật"
        }
        return weekdays.get(day_of_week, "Thứ Hai")
    
    def _get_vietnamese_date_display(self, date: datetime) -> str:
        """Hiển thị ngày tiếng Việt"""
        weekday = self._get_vietnamese_weekday(date.weekday())
        return f"{weekday}, {date.strftime('%d/%m/%Y')}"
    
    def _is_holiday(self, date: datetime) -> bool:
        """Kiểm tra ngày lễ"""
        holidays = [(1, 1), (30, 4), (1, 5), (2, 9)]
        return (date.day, date.month) in holidays
    
    def _get_season(self, month: int) -> str:
        """Xác định mùa"""
        if month in [12, 1, 2]:
            return "Mùa đông"
        elif month in [3, 4, 5]:
            return "Mùa xuân"
        elif month in [6, 7, 8]:
            return "Mùa hè"
        else:
            return "Mùa thu"
    
    def generate_full_dataset(self, days_ahead: int = 30) -> Dict:
        """Tạo dataset đầy đủ cho nhiều ngày"""
        dataset = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "base_date": self.base_date.isoformat(),
                "days_covered": days_ahead,
                "total_routes": len(self.flight_schedules),
                "airlines": list(self.airlines.keys()),
                "airports": list(self.airports.keys())
            },
            "airlines": self.airlines,
            "airports": self.airports,
            "routes": self.routes,
            "aircraft_configs": self.aircraft_configs,
            "flights_by_date": {}
        }
        
        # Tạo chuyến bay cho từng ngày
        for day in range(days_ahead + 1):
            current_date = self.base_date + timedelta(days=day)
            date_str = current_date.strftime("%Y-%m-%d")
            
            dataset["flights_by_date"][date_str] = {}
            
            # Tạo chuyến bay cho từng tuyến
            for route_key in self.flight_schedules.keys():
                from_code, to_code = route_key.split('-')
                
                flights = self.generate_flights_for_date(from_code, to_code, current_date)
                dataset["flights_by_date"][date_str][route_key] = flights
        
        return dataset
    
    def save_dataset(self, dataset: Dict, filename: str = None):
        """Lưu dataset ra file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vietjet_mock_data_{timestamp}.json"
        
        # Tạo thư mục nếu chưa có
        os.makedirs("../data/generated", exist_ok=True)
        filepath = os.path.join("../data/generated", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Dataset đã được lưu tại: {filepath}")
        print(f"📊 Tổng số tuyến bay: {len(dataset['routes'])}")
        print(f"📅 Số ngày được tạo: {len(dataset['flights_by_date'])}")
        
        # Thống kê
        total_flights = 0
        for date_data in dataset["flights_by_date"].values():
            for route_flights in date_data.values():
                total_flights += len(route_flights)
        
        print(f"✈️ Tổng số chuyến bay: {total_flights}")
        return filepath

def main():
    """Chạy script tạo mock data"""
    print("🚀 Bắt đầu tạo mock data VietJet...")
    
    generator = MockDataGenerator()
    
    # Tạo dataset cho 30 ngày tới
    print("📝 Đang tạo dataset...")
    dataset = generator.generate_full_dataset(days_ahead=30)
    
    # Lưu file
    print("💾 Đang lưu dataset...")
    filepath = generator.save_dataset(dataset)
    
    print("🎉 Hoàn thành!")
    print(f"📁 File được lưu tại: {filepath}")

if __name__ == "__main__":
    main()