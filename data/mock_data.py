from datetime import datetime, timedelta
import random
import uuid

# Dynamic Flight Generator
class FlightDataGenerator:
    def __init__(self):
        # Chỉ VietJet - Tập trung Sovico ecosystem
        self.airlines = {
            "VJ": {"name": "VietJet Air", "price_factor": 1.0, "quality": "sovico_premium"}
        }
        
        # Airport codes mapping
        self.airport_codes = {
            "Hanoi": "HAN", "Ho Chi Minh City": "SGN", "Da Nang": "DAD",
            "Phu Quoc": "PQC", "Nha Trang": "CXR", "Da Lat": "DLI",
            "Can Tho": "VCA", "Hai Phong": "HPH", "Hue": "HUI",
            "Vung Tau": "VTG", "Quy Nhon": "UIH", "Vinh": "VII",
            "Pleiku": "PXU", "Buon Ma Thuot": "BMV", "Con Dao": "VCS",
            "Rach Gia": "VKG", "Ca Mau": "CAH"
        }
        
        # Airport full names
        self.airport_names = {
            "HAN": "Sân bay Nội Bài", "SGN": "Sân bay Tân Sơn Nhất", "DAD": "Sân bay Đà Nẵng",
            "PQC": "Sân bay Phú Quốc", "CXR": "Sân bay Cam Ranh", "DLI": "Sân bay Liên Khương",
            "VCA": "Sân bay Cần Thơ", "HPH": "Sân bay Cát Bi", "HUI": "Sân bay Phú Bài",
            "VTG": "Sân bay Vũng Tàu", "UIH": "Sân bay Phù Cát", "VII": "Sân bay Vinh",
            "PXU": "Sân bay Pleiku", "BMV": "Sân bay Buôn Ma Thuột", "VCS": "Sân bay Côn Đảo",
            "VKG": "Sân bay Rạch Giá", "CAH": "Sân bay Cà Mau"
        }
        
        # Real VietJet flight schedules by route (based on actual VietJet timetables)
        self.real_flights = {
            # SGN-HAN (Tuyến chính - 15+ chuyến/ngày)
            ("Ho Chi Minh City", "Hanoi"): [
                {"flight_id": "VJ111", "times": ["05:30", "08:15", "12:45", "16:35", "20:15"], "aircraft": "A321"},
                {"flight_id": "VJ113", "times": ["06:45", "10:30", "14:20", "18:50"], "aircraft": "A320"},
                {"flight_id": "VJ115", "times": ["07:00", "11:15", "15:30", "19:45"], "aircraft": "A321"},
                {"flight_id": "VJ117", "times": ["09:20", "13:40", "17:55", "21:40"], "aircraft": "A320"},
                {"flight_id": "VJ119", "times": ["22:30"], "aircraft": "A320"},
                {"flight_id": "VJ121", "times": ["23:45"], "aircraft": "A321"}
            ],
            # HAN-SGN (Tuyến chính - 15+ chuyến/ngày)
            ("Hanoi", "Ho Chi Minh City"): [
                {"flight_id": "VJ112", "times": ["05:45", "09:30", "13:15", "17:00", "20:45"], "aircraft": "A321"},
                {"flight_id": "VJ114", "times": ["06:30", "10:15", "14:00", "18:30"], "aircraft": "A320"},
                {"flight_id": "VJ116", "times": ["07:45", "11:30", "15:45", "19:15"], "aircraft": "A321"},
                {"flight_id": "VJ118", "times": ["08:00", "12:20", "16:40", "21:00"], "aircraft": "A320"},
                {"flight_id": "VJ120", "times": ["22:15"], "aircraft": "A320"},
                {"flight_id": "VJ122", "times": ["23:30"], "aircraft": "A321"}
            ],
            # SGN-DAD (Tuyến du lịch - 8+ chuyến/ngày)
            ("Ho Chi Minh City", "Da Nang"): [
                {"flight_id": "VJ321", "times": ["06:00", "10:45", "15:20", "19:30"], "aircraft": "A320"},
                {"flight_id": "VJ323", "times": ["07:15", "12:00", "16:35", "20:45"], "aircraft": "A321"},
                {"flight_id": "VJ325", "times": ["08:30", "13:15", "17:50"], "aircraft": "A320"},
                {"flight_id": "VJ327", "times": ["09:45", "14:30", "21:15"], "aircraft": "A320"}
            ],
            # DAD-SGN (Tuyến du lịch - 8+ chuyến/ngày)
            ("Da Nang", "Ho Chi Minh City"): [
                {"flight_id": "VJ322", "times": ["07:30", "12:15", "16:50", "21:00"], "aircraft": "A320"},
                {"flight_id": "VJ324", "times": ["08:45", "13:30", "18:05"], "aircraft": "A321"},
                {"flight_id": "VJ326", "times": ["09:00", "14:45", "19:20"], "aircraft": "A320"},
                {"flight_id": "VJ328", "times": ["11:15", "15:50", "22:30"], "aircraft": "A320"}
            ],
            # HAN-DAD (Tuyến du lịch - 6+ chuyến/ngày)
            ("Hanoi", "Da Nang"): [
                {"flight_id": "VJ541", "times": ["06:15", "11:00", "15:35", "19:50"], "aircraft": "A320"},
                {"flight_id": "VJ543", "times": ["07:30", "12:15", "16:50", "21:05"], "aircraft": "A321"},
                {"flight_id": "VJ545", "times": ["08:45", "13:30", "18:05"], "aircraft": "A320"},
                {"flight_id": "VJ547", "times": ["10:00", "14:45", "22:20"], "aircraft": "A320"}
            ],
            # DAD-HAN (Tuyến du lịch - 6+ chuyến/ngày)
            ("Da Nang", "Hanoi"): [
                {"flight_id": "VJ542", "times": ["08:00", "12:45", "17:20", "21:35"], "aircraft": "A320"},
                {"flight_id": "VJ544", "times": ["09:15", "14:00", "18:35"], "aircraft": "A321"},
                {"flight_id": "VJ546", "times": ["10:30", "15:15", "19:50"], "aircraft": "A320"},
                {"flight_id": "VJ548", "times": ["11:45", "16:30", "23:15"], "aircraft": "A320"}
            ],
            # SGN-PQC (Tuyến biển đảo - 10+ chuyến/ngày)
            ("Ho Chi Minh City", "Phu Quoc"): [
                {"flight_id": "VJ621", "times": ["06:30", "11:15", "16:00", "20:30"], "aircraft": "A320"},
                {"flight_id": "VJ623", "times": ["07:45", "12:30", "17:15"], "aircraft": "A321"},
                {"flight_id": "VJ625", "times": ["09:00", "13:45", "18:30"], "aircraft": "A320"},
                {"flight_id": "VJ627", "times": ["10:15", "15:00", "19:45"], "aircraft": "A320"},
                {"flight_id": "VJ629", "times": ["21:30", "22:45"], "aircraft": "A320"}
            ],
            # PQC-SGN (Tuyến biển đảo - 10+ chuyến/ngày)
            ("Phu Quoc", "Ho Chi Minh City"): [
                {"flight_id": "VJ622", "times": ["08:15", "13:00", "17:45", "22:15"], "aircraft": "A320"},
                {"flight_id": "VJ624", "times": ["09:30", "14:15", "19:00"], "aircraft": "A321"},
                {"flight_id": "VJ626", "times": ["10:45", "15:30", "20:15"], "aircraft": "A320"},
                {"flight_id": "VJ628", "times": ["12:00", "16:45", "21:30"], "aircraft": "A320"},
                {"flight_id": "VJ630", "times": ["23:15"], "aircraft": "A320"}
            ],
            # HAN-PQC (Tuyến xa - 4 chuyến/ngày)
            ("Hanoi", "Phu Quoc"): [
                {"flight_id": "VJ631", "times": ["07:00", "13:30", "19:15"], "aircraft": "A321"},
                {"flight_id": "VJ633", "times": ["10:15", "16:45"], "aircraft": "A320"},
                {"flight_id": "VJ635", "times": ["22:00"], "aircraft": "A321"}
            ],
            # PQC-HAN (Tuyến xa - 4 chuyến/ngày)
            ("Phu Quoc", "Hanoi"): [
                {"flight_id": "VJ632", "times": ["11:30", "18:00"], "aircraft": "A321"},
                {"flight_id": "VJ634", "times": ["14:45", "21:15"], "aircraft": "A320"},
                {"flight_id": "VJ636", "times": ["23:45"], "aircraft": "A321"}
            ],
            # SGN-CXR (Nha Trang - 6 chuyến/ngày)
            ("Ho Chi Minh City", "Nha Trang"): [
                {"flight_id": "VJ431", "times": ["06:45", "12:30", "18:15"], "aircraft": "A320"},
                {"flight_id": "VJ433", "times": ["08:00", "14:45", "20:30"], "aircraft": "A320"},
                {"flight_id": "VJ435", "times": ["10:15", "16:00"], "aircraft": "A321"}
            ],
            # CXR-SGN (Nha Trang - 6 chuyến/ngày)
            ("Nha Trang", "Ho Chi Minh City"): [
                {"flight_id": "VJ432", "times": ["08:30", "14:15", "20:00"], "aircraft": "A320"},
                {"flight_id": "VJ434", "times": ["09:45", "16:30", "22:15"], "aircraft": "A320"},
                {"flight_id": "VJ436", "times": ["12:00", "17:45"], "aircraft": "A321"}
            ],
            # HAN-CXR (Nha Trang - 4 chuyến/ngày)
            ("Hanoi", "Nha Trang"): [
                {"flight_id": "VJ451", "times": ["07:15", "14:00"], "aircraft": "A320"},
                {"flight_id": "VJ453", "times": ["11:30", "18:45"], "aircraft": "A321"}
            ],
            # CXR-HAN (Nha Trang - 4 chuyến/ngày)
            ("Nha Trang", "Hanoi"): [
                {"flight_id": "VJ452", "times": ["10:00", "16:45"], "aircraft": "A320"},
                {"flight_id": "VJ454", "times": ["14:15", "21:30"], "aircraft": "A321"}
            ],
            # SGN-DLI (Đà Lạt - 4 chuyến/ngày)
            ("Ho Chi Minh City", "Da Lat"): [
                {"flight_id": "VJ361", "times": ["07:30", "14:15"], "aircraft": "A320"},
                {"flight_id": "VJ363", "times": ["10:45", "17:30"], "aircraft": "A320"}
            ],
            # DLI-SGN (Đà Lạt - 4 chuyến/ngày)
            ("Da Lat", "Ho Chi Minh City"): [
                {"flight_id": "VJ362", "times": ["09:15", "16:00"], "aircraft": "A320"},
                {"flight_id": "VJ364", "times": ["12:30", "19:15"], "aircraft": "A320"}
            ]
        }
        
        self.routes = {
            # Tuyến chính (Main routes)
            ("Hanoi", "Ho Chi Minh City"): {"distance": 1166, "base_price": 1299000, "popular": True, "flight_time": "2h05m"},
            ("Ho Chi Minh City", "Hanoi"): {"distance": 1166, "base_price": 1299000, "popular": True, "flight_time": "2h05m"},
            ("Hanoi", "Da Nang"): {"distance": 608, "base_price": 899000, "popular": True, "flight_time": "1h20m"},
            ("Da Nang", "Hanoi"): {"distance": 608, "base_price": 899000, "popular": True, "flight_time": "1h20m"},
            ("Ho Chi Minh City", "Da Nang"): {"distance": 647, "base_price": 999000, "popular": True, "flight_time": "1h25m"},
            ("Da Nang", "Ho Chi Minh City"): {"distance": 647, "base_price": 999000, "popular": True, "flight_time": "1h25m"},
            
            # Tuyến du lịch biển đảo (Beach & Island routes)
            ("Hanoi", "Phu Quoc"): {"distance": 1542, "base_price": 1799000, "popular": True, "flight_time": "2h35m"},
            ("Phu Quoc", "Hanoi"): {"distance": 1542, "base_price": 1799000, "popular": True, "flight_time": "2h35m"},
            ("Ho Chi Minh City", "Phu Quoc"): {"distance": 289, "base_price": 699000, "popular": True, "flight_time": "50m"},
            ("Phu Quoc", "Ho Chi Minh City"): {"distance": 289, "base_price": 699000, "popular": True, "flight_time": "50m"},
            ("Hanoi", "Nha Trang"): {"distance": 1078, "base_price": 1399000, "popular": True, "flight_time": "2h00m"},
            ("Nha Trang", "Hanoi"): {"distance": 1078, "base_price": 1399000, "popular": True, "flight_time": "2h00m"},
            ("Ho Chi Minh City", "Nha Trang"): {"distance": 448, "base_price": 799000, "popular": True, "flight_time": "1h10m"},
            ("Nha Trang", "Ho Chi Minh City"): {"distance": 448, "base_price": 799000, "popular": True, "flight_time": "1h10m"},
            
            # Tuyến đà lạt (Highland routes)
            ("Ho Chi Minh City", "Da Lat"): {"distance": 308, "base_price": 599000, "popular": True, "flight_time": "55m"},
            ("Da Lat", "Ho Chi Minh City"): {"distance": 308, "base_price": 599000, "popular": True, "flight_time": "55m"},
            
            # Tuyến khác (Other routes)
            ("Hanoi", "Can Tho"): {"distance": 1365, "base_price": 1599000, "popular": False, "flight_time": "2h20m"},
            ("Can Tho", "Hanoi"): {"distance": 1365, "base_price": 1599000, "popular": False, "flight_time": "2h20m"},
            ("Ho Chi Minh City", "Can Tho"): {"distance": 189, "base_price": 499000, "popular": True, "flight_time": "45m"},
            ("Can Tho", "Ho Chi Minh City"): {"distance": 189, "base_price": 499000, "popular": True, "flight_time": "45m"},
            
            # Tuyến miền trung (Central routes)
            ("Hanoi", "Hue"): {"distance": 540, "base_price": 999000, "popular": True, "flight_time": "1h15m"},
            ("Hue", "Hanoi"): {"distance": 540, "base_price": 999000, "popular": True, "flight_time": "1h15m"},
            ("Ho Chi Minh City", "Hue"): {"distance": 1017, "base_price": 1299000, "popular": False, "flight_time": "1h50m"},
            ("Hue", "Ho Chi Minh City"): {"distance": 1017, "base_price": 1299000, "popular": False, "flight_time": "1h50m"},
            ("Da Nang", "Hue"): {"distance": 108, "base_price": 399000, "popular": True, "flight_time": "30m"},
            ("Hue", "Da Nang"): {"distance": 108, "base_price": 399000, "popular": True, "flight_time": "30m"},
            
            # Tuyến biển đông (Eastern coastal routes)
            ("Ho Chi Minh City", "Vung Tau"): {"distance": 125, "base_price": 399000, "popular": True, "flight_time": "35m"},
            ("Vung Tau", "Ho Chi Minh City"): {"distance": 125, "base_price": 399000, "popular": True, "flight_time": "35m"},
            ("Hanoi", "Quy Nhon"): {"distance": 853, "base_price": 1199000, "popular": False, "flight_time": "1h35m"},
            ("Quy Nhon", "Hanoi"): {"distance": 853, "base_price": 1199000, "popular": False, "flight_time": "1h35m"},
            ("Ho Chi Minh City", "Quy Nhon"): {"distance": 622, "base_price": 899000, "popular": False, "flight_time": "1h20m"},
            ("Quy Nhon", "Ho Chi Minh City"): {"distance": 622, "base_price": 899000, "popular": False, "flight_time": "1h20m"}
        }
    
    def generate_flights(self, from_city: str, to_city: str, date: str, count: int = None) -> list:
        """Sinh chuyến bay động dựa trên route và ngày"""
        route_key = (from_city, to_city)
        
        if route_key not in self.routes:
            return []  # Không có route
        
        route_info = self.routes[route_key]
        flights = []
        
        # Số lượng chuyến bay dựa trên độ phổ biến
        if count is None:
            count = random.randint(3, 6) if route_info["popular"] else random.randint(1, 3)
        
        # Lấy ngày hiện tại từ hệ thống
        base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        try:
            if date in ["hôm nay", "today"]:
                flight_date = base_date
                days_ahead = 0
            elif date in ["ngày mai", "tomorrow"]:
                flight_date = base_date + timedelta(days=1)
                days_ahead = 1
            elif "/" in date:  # Format dd/mm/yyyy
                flight_date = datetime.strptime(date, "%d/%m/%Y")
                days_ahead = (flight_date - base_date).days
            else:  # Format yyyy-mm-dd
                flight_date = datetime.strptime(date, "%Y-%m-%d")
                days_ahead = (flight_date - base_date).days
        except:
            days_ahead = 1
            flight_date = base_date + timedelta(days=1)
        
        # Lấy real flights cho route này
        real_route_flights = self.real_flights.get(route_key, [])
        if not real_route_flights:
            return []  # Không có chuyến bay thực cho route này
        
        airline_code = "VJ"
        airline_info = self.airlines["VJ"]
        
        # Tạo flights từ real data
        for flight_schedule in real_route_flights:
            flight_id = flight_schedule["flight_id"]
            available_times = flight_schedule["times"]
            
            # Chọn giờ bay dựa trên ngày cụ thể
            flight_num = int(flight_id[2:])  # VJ111 -> 111
            day_of_week = flight_date.weekday()  # 0=Monday, 6=Sunday
            
            # Số chuyến bay theo ngày trong tuần
            if day_of_week in [5, 6]:  # Thứ 7, Chủ nhật - nhiều chuyến hơn
                num_times = min(len(available_times), 4)
            elif day_of_week in [0, 4]:  # Thứ 2, Thứ 6 - trung bình
                num_times = min(len(available_times), 3)
            else:  # Thứ 3, 4, 5 - ít chuyến hơn
                num_times = min(len(available_times), 2)
            
            # Chọn giờ bay cố định dựa trên flight_num
            start_idx = flight_num % max(1, len(available_times) - num_times + 1)
            selected_times = available_times[start_idx:start_idx + num_times]
            
            for flight_time in selected_times:
                # Tính giá động
                base_price = route_info["base_price"]
                price = self._calculate_dynamic_price(
                    base_price, airline_info["price_factor"], days_ahead, flight_time
                )
            

            
                # Số ghế dựa trên ngày cụ thể và giờ bay
                flight_num = int(flight_id[2:])  # VJ111 -> 111
                time_hour = int(flight_time.split(':')[0])
                day_of_week = flight_date.weekday()
                
                # Base seats dựa trên flight number
                base_seats = 45 - (flight_num % 25)  # 20-45 ghế
                
                # Hệ số theo ngày trong tuần
                if day_of_week in [5, 6]:  # Cuối tuần - ít ghế hơn
                    day_factor = 0.6
                elif day_of_week in [0, 4]:  # Đầu/cuối tuần làm việc
                    day_factor = 0.8
                else:  # Giữa tuần - nhiều ghế hơn
                    day_factor = 1.0
                
                # Hệ số theo giờ bay
                if 6 <= time_hour <= 8 or 17 <= time_hour <= 19:  # Giờ cao điểm
                    time_factor = 0.5
                elif 9 <= time_hour <= 11 or 14 <= time_hour <= 16:  # Giờ tốt
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
                
                seats_left = max(1, int(base_seats * day_factor * time_factor * advance_factor))
                
                # Airport codes và tên
                from_code = self.airport_codes.get(from_city, from_city[:3].upper())
                to_code = self.airport_codes.get(to_city, to_city[:3].upper())
                from_airport = self.airport_names.get(from_code, f"Sân bay {from_city}")
                to_airport = self.airport_names.get(to_code, f"Sân bay {to_city}")
                
                # Chi tiết máy bay và ghế ngồi
                aircraft_type = flight_schedule["aircraft"]
                seat_config = self._get_aircraft_config(aircraft_type)
                
                # Danh sách ghế còn trống thực tế
                available_seats = self._generate_available_seats(seat_config, seats_left)
                
                # Thông tin hành lý
                baggage_info = self._get_baggage_allowance()
                
                # Thông tin dịch vụ
                services = self._get_flight_services()
                
                flight = {
                    "service_id": f"F{flight_id[2:]}{time_hour:02d}",  # F11105, F11308...
                    "flight_id": flight_id,
                    "airline": airline_info["name"],
                    "airline_code": airline_code,
                    "from_city": from_city,
                    "to_city": to_city,
                    "from_code": from_code,
                    "to_code": to_code,
                    "from_airport": from_airport,
                    "to_airport": to_airport,
                    "route": f"{from_code} → {to_code}",
                    "route_detail": f"{from_airport} → {to_airport}",
                    "date": flight_date.strftime("%d/%m/%Y"),
                    "date_display": self._get_vietnamese_date_display(flight_date),
                    "weekday": self._get_vietnamese_weekday(flight_date.weekday()),
                    "day_of_week": flight_date.weekday(),
                    "is_weekend": flight_date.weekday() >= 5,
                    "is_holiday": self._is_holiday(flight_date),
                    "season": self._get_season(flight_date.month),
                    "time": flight_time,
                    "price": int(price),
                    "seats_left": seats_left,
                    "class_type": "Economy",
                    "quality": airline_info["quality"],
                    "duration": self._calculate_duration(route_info["distance"], route_key),
                    
                    # Chi tiết máy bay
                    "aircraft": {
                        "type": aircraft_type,
                        "manufacturer": "Airbus" if aircraft_type.startswith("A") else "Boeing",
                        "total_seats": seat_config["total_seats"],
                        "seat_config": seat_config["layout"],
                        "wifi": True,
                        "entertainment": aircraft_type == "A321"
                    },
                    
                    # Thông tin ghế ngồi
                    "seating": {
                        "available_seats": available_seats,
                        "seat_map": seat_config["seat_map"],
                        "premium_seats": seat_config["premium_seats"],
                        "exit_row_seats": seat_config["exit_row_seats"]
                    },
                    
                    # Thông tin hành lý
                    "baggage": baggage_info,
                    
                    # Dịch vụ bổ sung
                    "services": services,
                    
                    # Thông tin giá vé chi tiết
                    "pricing": {
                        "base_fare": int(price * 0.7),
                        "taxes_fees": int(price * 0.2),
                        "service_fee": int(price * 0.1),
                        "total": int(price),
                        "currency": "VND"
                    },
                    
                    # Chính sách
                    "policies": {
                        "cancellation": "Có thể hủy với phí 500,000 VND",
                        "change": "Có thể đổi với phí 300,000 VND",
                        "refund": "Hoàn tiền 70% nếu hủy trước 24h",
                        "check_in": "Mở check-in online 24h trước giờ bay"
                    }
                }
                flights.append(flight)
        
        return sorted(flights, key=lambda x: x["price"])
    
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
        # Các ngày lễ cố định trong năm
        holidays = [
            (1, 1),   # Tết Dương lịch
            (30, 4),  # Giải phóng miền Nam
            (1, 5),   # Quốc tế lao động
            (2, 9),   # Quốc khánh
        ]
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
    
    def _get_aircraft_config(self, aircraft_type: str) -> dict:
        """Lấy cấu hình máy bay thực tế của VietJet"""
        configs = {
            "A320": {
                "total_seats": 180,
                "layout": "3-3",
                "rows": 30,
                "seat_map": "A-B-C | D-E-F",
                "premium_seats": ["1A", "1B", "1C", "1D", "1E", "1F", "2A", "2B", "2C", "2D", "2E", "2F"],
                "exit_row_seats": ["12A", "12B", "12C", "12D", "12E", "12F", "13A", "13B", "13C", "13D", "13E", "13F"]
            },
            "A321": {
                "total_seats": 230,
                "layout": "3-3",
                "rows": 38,
                "seat_map": "A-B-C | D-E-F",
                "premium_seats": ["1A", "1B", "1C", "1D", "1E", "1F", "2A", "2B", "2C", "2D", "2E", "2F", "3A", "3B", "3C", "3D", "3E", "3F"],
                "exit_row_seats": ["14A", "14B", "14C", "14D", "14E", "14F", "15A", "15B", "15C", "15D", "15E", "15F"]
            }
        }
        return configs.get(aircraft_type, configs["A320"])
    
    def _generate_available_seats(self, seat_config: dict, seats_left: int) -> list:
        """Danh sách ghế còn trống thực tế"""
        # Ghế còn trống thực tế cho A320/A321
        if seat_config["total_seats"] == 180:  # A320
            available_seats = [
                "5A", "5B", "5F", "7C", "7D", "8A", "8E", "9B", "9F", "11A", "11C", "11D",
                "14B", "14C", "14E", "15A", "15F", "17C", "17D", "18B", "18E", "19A", "19F",
                "21C", "21D", "22A", "22B", "23E", "23F", "25B", "25C", "26A", "26D", "27F",
                "28C", "28E", "29A", "29B", "30D", "30F"
            ]
        else:  # A321
            available_seats = [
                "6A", "6B", "6F", "8C", "8D", "9A", "9E", "10B", "10F", "12A", "12C", "12D",
                "16B", "16C", "16E", "17A", "17F", "19C", "19D", "20B", "20E", "21A", "21F",
                "23C", "23D", "24A", "24B", "25E", "25F", "27B", "27C", "28A", "28D", "29F",
                "30C", "30E", "31A", "31B", "32D", "32F", "34A", "34C", "35B", "35E", "36F",
                "37A", "37D", "38B", "38C"
            ]
        
        return available_seats[:min(seats_left, len(available_seats))]
    
    def _get_baggage_allowance(self) -> dict:
        """Thông tin hành lý VietJet thực tế"""
        return {
            "cabin": {
                "weight": "7kg",
                "dimensions": "56cm x 36cm x 23cm",
                "pieces": 1
            },
            "checked": {
                "included": "20kg",
                "max_weight": "32kg",
                "excess_fee": "200,000 VND/kg",
                "additional_bag": "500,000 VND"
            },
            "special_items": {
                "sports_equipment": "Có phí bổ sung",
                "musical_instruments": "Cần đăng ký trước",
                "fragile_items": "Có bảo hiểm riêng"
            }
        }
    
    def _get_flight_services(self) -> dict:
        """Dịch vụ trên chuyến bay VietJet"""
        return {
            "meals": {
                "available": True,
                "options": ["Cơm gà teriyaki", "Mì Ý sốt bò", "Cháo tôm", "Bánh mì pate"],
                "price_range": "80,000 - 150,000 VND",
                "pre_order": "Có thể đặt trước online"
            },
            "beverages": {
                "complimentary": ["Nước lọc", "Trà", "Cà phê"],
                "premium": ["Nước ngọt", "Bia", "Rượu vang"],
                "price_range": "30,000 - 100,000 VND"
            },
            "entertainment": {
                "wifi": "Có sẵn (có phí)",
                "streaming": "VieON miễn phí",
                "magazines": "Tạp chí VietJet",
                "games": "Trò chơi trên app"
            },
            "comfort": {
                "blanket": "Có sẵn (có phí)",
                "pillow": "Có sẵn (có phí)",
                "seat_selection": "Miễn phí ghế thường, có phí ghế đặc biệt",
                "priority_boarding": "Có sẵn với phí bổ sung"
            }
        }
    
    def _generate_flight_times(self, count: int) -> list:
        """Sinh giờ bay VietJet thực tế"""
        vietjet_times = ["05:30", "06:45", "08:15", "10:30", "12:45", "14:20", "16:35", "18:50", "20:15", "21:40"]
        selected_times = random.sample(vietjet_times, min(count, len(vietjet_times)))
        return sorted(selected_times)
    
    def find_flight_by_id(self, flight_id: str, route_key: tuple) -> dict:
        """Tìm chuyến bay theo mã chính xác"""
        real_route_flights = self.real_flights.get(route_key, [])
        
        for flight_schedule in real_route_flights:
            if flight_schedule["flight_id"] == flight_id:
                return flight_schedule
        return None
    
    def _calculate_duration(self, distance: int, route_key: tuple = None) -> str:
        """Tính thời gian bay dựa trên route thực tế"""
        # Sử dụng flight_time thực tế nếu có
        if route_key and route_key in self.routes:
            return self.routes[route_key].get("flight_time", "1h30m")
        
        # Fallback: Tính toán dựa trên khoảng cách
        # Tốc độ trung bình ~550km/h (bao gồm thời gian cất hạ cánh)
        hours = distance / 550
        total_minutes = int(hours * 60)
        flight_hours = total_minutes // 60
        flight_minutes = total_minutes % 60
        return f"{flight_hours}h{flight_minutes:02d}m" if flight_hours > 0 else f"{flight_minutes}m"
    
    def _calculate_dynamic_price(self, base_price: int, airline_factor: float, days_ahead: int, flight_time: str) -> float:
        """Tính giá động dựa trên nhiều yếu tố"""
        price = base_price * airline_factor
        
        # Giá tăng khi gần ngày bay
        if days_ahead <= 3:
            price *= 1.5
        elif days_ahead <= 7:
            price *= 1.2
        elif days_ahead >= 30:
            price *= 0.8  # Giảm giá book sớm
        
        # Giá theo giờ bay (giờ vàng đắt hơn)
        hour = int(flight_time.split(":")[0])
        if 7 <= hour <= 9 or 17 <= hour <= 19:  # Giờ cao điểm
            price *= 1.1
        elif 12 <= hour <= 14:  # Giờ trưa
            price *= 0.95
        
        # Biến động giá cố định dựa trên giờ bay
        hour = int(flight_time.split(":")[0])
        minute = int(flight_time.split(":")[1])
        
        # Công thức cố định cho biến động giá
        time_seed = (hour * 60 + minute) % 100
        fluctuation = 0.9 + (time_seed % 21) / 100  # 0.9 - 1.1
        price *= fluctuation
        
        return price

# Global generator instance
flight_generator = FlightDataGenerator()

# Dynamic Hotel Generator
class HotelDataGenerator:
    def __init__(self):
        self.hotels_by_city = {
            "Da Nang": [
                {"name": "Vinpearl Resort Da Nang", "rating": 5, "base_price": 2500000, "type": "resort"},
                {"name": "Pullman Da Nang Beach Resort", "rating": 5, "base_price": 2200000, "type": "hotel"},
                {"name": "Novotel Da Nang Premier Han River", "rating": 4, "base_price": 1800000, "type": "hotel"},
                {"name": "Fusion Maia Da Nang", "rating": 5, "base_price": 3000000, "type": "spa_resort"}
            ],
            "Hanoi": [
                {"name": "Lotte Hotel Hanoi", "rating": 5, "base_price": 3500000, "type": "luxury"},
                {"name": "JW Marriott Hotel Hanoi", "rating": 5, "base_price": 3200000, "type": "business"},
                {"name": "Hilton Hanoi Opera", "rating": 5, "base_price": 2800000, "type": "heritage"}
            ],
            "Ho Chi Minh City": [
                {"name": "Park Hyatt Saigon", "rating": 5, "base_price": 4000000, "type": "luxury"},
                {"name": "Caravelle Saigon", "rating": 5, "base_price": 3500000, "type": "heritage"},
                {"name": "Renaissance Riverside Hotel Saigon", "rating": 4, "base_price": 2500000, "type": "business"}
            ],
            "Phu Quoc": [
                {"name": "JW Marriott Phu Quoc Emerald Bay", "rating": 5, "base_price": 4500000, "type": "luxury_resort"},
                {"name": "InterContinental Phu Quoc Long Beach", "rating": 5, "base_price": 3800000, "type": "beach_resort"},
                {"name": "Vinpearl Resort Phu Quoc", "rating": 5, "base_price": 3200000, "type": "resort"}
            ],
            "Nha Trang": [
                {"name": "Vinpearl Resort Nha Trang", "rating": 5, "base_price": 2800000, "type": "resort"},
                {"name": "Sheraton Nha Trang Hotel", "rating": 5, "base_price": 2500000, "type": "hotel"},
                {"name": "Amiana Resort Nha Trang", "rating": 4, "base_price": 2000000, "type": "beach_resort"}
            ],
            "Da Lat": [
                {"name": "Ana Mandara Villas Dalat", "rating": 5, "base_price": 3000000, "type": "villa_resort"},
                {"name": "Dalat Palace Heritage Hotel", "rating": 5, "base_price": 2500000, "type": "heritage"},
                {"name": "Swiss-Belresort Tuyen Lam Dalat", "rating": 4, "base_price": 1800000, "type": "resort"}
            ]
        }
    
    def generate_hotels(self, city: str, date: str = None, nights: int = 1) -> list:
        """Sinh khách sạn động theo thành phố"""
        if city not in self.hotels_by_city:
            return []
        
        hotels = []
        for i, hotel_info in enumerate(self.hotels_by_city[city]):
            # Tính giá động
            price = self._calculate_hotel_price(hotel_info["base_price"], date, hotel_info["rating"])
            
            hotel = {
                "service_id": f"H{uuid.uuid4().hex[:6].upper()}",
                "name": hotel_info["name"],
                "location": self._get_city_name(city),
                "rating": hotel_info["rating"],
                "price_per_night": int(price),
                "rooms_left": random.randint(3, 15),
                "type": hotel_info["type"]
            }
            hotels.append(hotel)
        
        return hotels
    
    def _calculate_hotel_price(self, base_price: int, date: str, rating: int) -> float:
        """Tính giá khách sạn động"""
        price = base_price
        
        if date:
            try:
                check_date = datetime.strptime(date, "%Y-%m-%d")
                # Cuối tuần đắt hơn
                if check_date.weekday() >= 5:
                    price *= 1.3
            except:
                pass
        
        # Biến động giá khách sạn cố định
        rating_factor = rating * 17  # 5 sao -> 85
        date_factor = len(date or 'default') * 3  # Độ dài string
        
        fluctuation_seed = (rating_factor + date_factor) % 100
        fluctuation = 0.85 + (fluctuation_seed % 31) / 100  # 0.85 - 1.15
        price *= fluctuation
        return price
    
    def _get_city_name(self, code: str) -> str:
        names = {
            "Hanoi": "Hà Nội", "Ho Chi Minh City": "TP.HCM", "Da Nang": "Đà Nẵng",
            "Phu Quoc": "Phú Quốc", "Nha Trang": "Nha Trang", "Da Lat": "Đà Lạt",
            "Can Tho": "Cần Thơ", "Hai Phong": "Hải Phòng", "Hue": "Huế",
            "Vung Tau": "Vũng Tàu", "Quy Nhon": "Quy Nhon"
        }
        return names.get(code, code)

hotel_generator = HotelDataGenerator()
HOTELS_DATA = []  # Deprecated, use generator

# Dynamic Transfer Generator  
class TransferDataGenerator:
    def __init__(self):
        self.transfers_by_city = {
            "Da Nang": [
                {"type": "Airport Transfer", "from": "Sân bay Đà Nẵng", "to": "Trung tâm thành phố", "price": 300000, "vehicle": "Xe riêng"},
                {"type": "Hotel Transfer", "from": "Sân bay Đà Nẵng", "to": "Khu resort", "price": 400000, "vehicle": "Xe 7 chỗ"}
            ],
            "Hanoi": [
                {"type": "Airport Transfer", "from": "Sân bay Nội Bài", "to": "Trung tâm Hà Nội", "price": 500000, "vehicle": "Xe riêng"},
                {"type": "Train Station Transfer", "from": "Ga Hà Nội", "to": "Khách sạn", "price": 200000, "vehicle": "Taxi"}
            ],
            "Ho Chi Minh City": [
                {"type": "Airport Transfer", "from": "Sân bay Tân Sơn Nhất", "to": "Quận 1", "price": 400000, "vehicle": "Xe riêng"},
                {"type": "City Transfer", "from": "Khách sạn", "to": "Địa điểm tham quan", "price": 300000, "vehicle": "Xe 4 chỗ"}
            ],
            "Phu Quoc": [
                {"type": "Airport Transfer", "from": "Sân bay Phú Quốc", "to": "Khu resort", "price": 200000, "vehicle": "Xe riêng"},
                {"type": "Island Tour", "from": "Khách sạn", "to": "Tour đảo", "price": 800000, "vehicle": "Xe + thuyền"}
            ],
            "Nha Trang": [
                {"type": "Airport Transfer", "from": "Sân bay Cam Ranh", "to": "Trung tâm Nha Trang", "price": 350000, "vehicle": "Xe riêng"},
                {"type": "Beach Transfer", "from": "Khách sạn", "to": "Bãi biển", "price": 150000, "vehicle": "Xe 4 chỗ"}
            ]
        }
    
    def generate_transfers(self, city: str) -> list:
        """Sinh dịch vụ transfer theo thành phố"""
        if city not in self.transfers_by_city:
            return []
        
        transfers = []
        for transfer_info in self.transfers_by_city[city]:
            transfer = {
                "service_id": f"T{uuid.uuid4().hex[:6].upper()}",
                "type": transfer_info["type"],
                "from_location": transfer_info["from"],
                "to_location": transfer_info["to"],
                "price": transfer_info["price"],
                "vehicle": transfer_info["vehicle"]
            }
            transfers.append(transfer)
        
        return transfers

transfer_generator = TransferDataGenerator()
TRANSFERS_DATA = []  # Deprecated

# Dynamic Combo Generator
class ComboDataGenerator:
    def generate_combo(self, flight_data: dict, destination: str) -> dict:
        """Sinh combo động dựa trên chuyến bay đã chọn"""
        hotels = hotel_generator.generate_hotels(destination)
        transfers = transfer_generator.generate_transfers(destination)
        
        if not hotels:
            return None
        
        # Chọn khách sạn phù hợp với mức giá vé
        suitable_hotel = self._select_suitable_hotel(hotels, flight_data["price"])
        
        combo_items = [
            {
                "type": "flight",
                "service_id": flight_data["service_id"],
                "name": f"{flight_data['airline']} {flight_data['flight_id']}",
                "price": flight_data["price"]
            },
            {
                "type": "hotel",
                "service_id": suitable_hotel["service_id"],
                "name": suitable_hotel["name"],
                "price": suitable_hotel["price_per_night"]
            }
        ]
        
        # Thêm transfer nếu có
        if transfers:
            combo_items.append({
                "type": "transfer",
                "service_id": transfers[0]["service_id"],
                "name": transfers[0]["type"],
                "price": transfers[0]["price"]
            })
        
        total_price = sum(item["price"] for item in combo_items)
        discount = int(total_price * random.uniform(0.05, 0.15))  # 5-15% discount
        
        return {
            "combo_id": f"CB{uuid.uuid4().hex[:6].upper()}",
            "name": f"Combo {flight_data['airline']} + {suitable_hotel['name']}",
            "items": combo_items,
            "total_price": total_price,
            "discount": discount,
            "final_price": total_price - discount
        }
    
    def _select_suitable_hotel(self, hotels: list, flight_price: int) -> dict:
        """Chọn khách sạn phù hợp với mức giá vé"""
        if flight_price < 1000000:  # Vé rẻ -> khách sạn bình dân
            return min(hotels, key=lambda h: h["price_per_night"])
        elif flight_price > 2000000:  # Vé đắt -> khách sạn cao cấp
            return max(hotels, key=lambda h: h["price_per_night"])
        else:  # Vé trung bình -> khách sạn trung cấp
            return sorted(hotels, key=lambda h: h["price_per_night"])[len(hotels)//2]

combo_generator = ComboDataGenerator()
COMBOS_DATA = []  # Deprecated

def get_flights_by_route(from_city: str, to_city: str, date: str = None):
    """Get flights by route and date - Use generated data"""
    try:
        from data.mock_data_loader import get_flights_by_route as get_flights_new
        return get_flights_new(from_city, to_city, date)
    except ImportError:
        # Fallback to old generator
        if not date:
            date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        print(f"DEBUG: get_flights_by_route called with from_city={from_city}, to_city={to_city}, date={date}")
        flights = flight_generator.generate_flights(from_city, to_city, date)
        print(f"DEBUG: Generated {len(flights)} flights")
        return flights

def get_cheapest_flight(from_city: str, to_city: str, date: str = None):
    """Get cheapest flight for route"""
    try:
        from data.mock_data_loader import get_cheapest_flight as get_cheapest_new
        return get_cheapest_new(from_city, to_city, date)
    except ImportError:
        # Fallback to old method
        flights = get_flights_by_route(from_city, to_city, date)
        if flights:
            return min(flights, key=lambda x: x["price"])
        return None

def get_flight_by_id(service_id: str):
    """Get flight by service ID - Generate on demand"""
    # Tạm thời return None, sẽ cần context để generate
    return None

def get_flight_by_flight_code(flight_code: str, from_city: str = None, to_city: str = None, date: str = None):
    """Get flight by flight code - Use generated data"""
    try:
        from data.mock_data_loader import get_flight_by_flight_code as get_flight_new
        return get_flight_new(flight_code, from_city, to_city, date)
    except ImportError:
        # Fallback to old method
        if not flight_code.startswith("VJ"):
            return None
        return None  # Simplified fallback