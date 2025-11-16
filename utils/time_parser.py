import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

class FlexibleTimeParser:
    """Parser thời gian linh hoạt cho nhiều format"""
    
    def __init__(self):
        # Mapping các từ thời gian
        self.time_keywords = {
            # Ngày cụ thể
            'hôm nay': 0, 'today': 0,
            'ngày mai': 1, 'tomorrow': 1, 'mai': 1,
            'ngày kia': 2, 'kia': 2, 'mốt': 2,
            'ngày mốt': 3,
            
            # Tuần
            'tuần này': 0, 'this week': 0,
            'tuần sau': 7, 'next week': 7, 'tuần tới': 7,
            'tuần kia': 14, '2 tuần nữa': 14,
            
            # Tháng
            'tháng này': 0, 'this month': 0,
            'tháng sau': 30, 'next month': 30, 'tháng tới': 30,
            'tháng kia': 60, '2 tháng nữa': 60,
            
            # Thứ trong tuần
            'thứ hai': 0, 'monday': 0, 't2': 0,
            'thứ ba': 1, 'tuesday': 1, 't3': 1,
            'thứ tư': 2, 'wednesday': 2, 't4': 2,
            'thứ năm': 3, 'thursday': 3, 't5': 3,
            'thứ sáu': 4, 'friday': 4, 't6': 4,
            'thứ bảy': 5, 'saturday': 5, 't7': 5,
            'chủ nhật': 6, 'sunday': 6, 'cn': 6,
            
            # Cuối tuần
            'cuối tuần': 'weekend', 'weekend': 'weekend',
            'cuối tuần này': 'this_weekend',
            'cuối tuần sau': 'next_weekend'
        }
        
        # Pattern cho số + đơn vị thời gian
        self.number_patterns = {
            'ngày': 'days',
            'tuần': 'weeks', 
            'tháng': 'months',
            'năm': 'years'
        }
    
    def parse_time_expression(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse biểu thức thời gian từ text"""
        text_lower = text.lower().strip()
        
        # 1. Kiểm tra các từ khóa cố định
        for keyword, offset in self.time_keywords.items():
            if keyword in text_lower:
                return self._calculate_date_from_keyword(keyword, offset)
        
        # 2. Kiểm tra pattern số + đơn vị (VD: "3 ngày nữa", "2 tuần sau")
        number_match = self._parse_number_expression(text_lower)
        if number_match:
            return number_match
        
        # 3. Kiểm tra format ngày tháng (dd/mm, dd-mm, dd/mm/yyyy)
        date_match = self._parse_date_format(text_lower)
        if date_match:
            return date_match
        
        # 4. Kiểm tra thời gian trong ngày (12h, 1h chiều, 8h sáng)
        time_match = self._parse_time_format(text_lower)
        if time_match:
            return time_match
        
        return None
    
    def _calculate_date_from_keyword(self, keyword: str, offset) -> Dict[str, Any]:
        """Tính toán ngày từ keyword"""
        today = datetime.now()
        
        if isinstance(offset, int):
            if 'tuần' in keyword:
                target_date = today + timedelta(weeks=offset//7 if offset >= 7 else 0, days=offset%7)
            elif 'tháng' in keyword:
                # Xấp xỉ tháng = 30 ngày
                target_date = today + timedelta(days=offset)
            else:
                target_date = today + timedelta(days=offset)
            
            return {
                'date': target_date.strftime('%Y-%m-%d'),
                'type': 'relative_date',
                'original': keyword
            }
        
        elif offset == 'weekend':
            # Tìm cuối tuần gần nhất
            days_until_saturday = (5 - today.weekday()) % 7
            if days_until_saturday == 0 and today.weekday() == 5:  # Hôm nay là thứ 7
                days_until_saturday = 0
            elif days_until_saturday == 0:  # Hôm nay là chủ nhật
                days_until_saturday = 6
            
            weekend_date = today + timedelta(days=days_until_saturday)
            return {
                'date': weekend_date.strftime('%Y-%m-%d'),
                'type': 'weekend',
                'original': keyword
            }
        
        elif offset in ['this_weekend', 'next_weekend']:
            days_until_saturday = (5 - today.weekday()) % 7
            if offset == 'next_weekend':
                days_until_saturday += 7
            
            weekend_date = today + timedelta(days=days_until_saturday)
            return {
                'date': weekend_date.strftime('%Y-%m-%d'),
                'type': 'weekend',
                'original': keyword
            }
        
        # Xử lý thứ trong tuần
        elif isinstance(offset, int) and 0 <= offset <= 6:
            days_ahead = offset - today.weekday()
            if days_ahead <= 0:  # Nếu đã qua thứ đó trong tuần
                days_ahead += 7
            
            target_date = today + timedelta(days=days_ahead)
            return {
                'date': target_date.strftime('%Y-%m-%d'),
                'type': 'weekday',
                'original': keyword
            }
        
        return None
    
    def _parse_number_expression(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse biểu thức số + đơn vị thời gian"""
        # Pattern: "3 ngày nữa", "2 tuần sau", "1 tháng tới"
        pattern = r'(\d+)\s*(ngày|tuần|tháng|năm)\s*(nữa|sau|tới|kia)?'
        match = re.search(pattern, text)
        
        if match:
            number = int(match.group(1))
            unit = match.group(2)
            
            today = datetime.now()
            
            if unit == 'ngày':
                target_date = today + timedelta(days=number)
            elif unit == 'tuần':
                target_date = today + timedelta(weeks=number)
            elif unit == 'tháng':
                target_date = today + timedelta(days=number * 30)  # Xấp xỉ
            elif unit == 'năm':
                target_date = today + timedelta(days=number * 365)  # Xấp xỉ
            else:
                return None
            
            return {
                'date': target_date.strftime('%Y-%m-%d'),
                'type': 'relative_number',
                'original': match.group(0),
                'number': number,
                'unit': unit
            }
        
        return None
    
    def _parse_date_format(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse format ngày tháng cụ thể"""
        # Patterns: dd/mm, dd-mm, dd/mm/yyyy, dd-mm-yyyy
        patterns = [
            r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # dd/mm/yyyy
            r'(\d{1,2})[/-](\d{1,2})'              # dd/mm
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                day = int(match.group(1))
                month = int(match.group(2))
                year = int(match.group(3)) if len(match.groups()) > 2 else datetime.now().year
                
                try:
                    target_date = datetime(year, month, day)
                    return {
                        'date': target_date.strftime('%Y-%m-%d'),
                        'type': 'specific_date',
                        'original': match.group(0)
                    }
                except ValueError:
                    continue
        
        return None
    
    def _parse_time_format(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse thời gian trong ngày"""
        # Patterns: 12h, 1h chiều, 8h sáng, 14:30, 2:30 PM
        time_patterns = [
            r'(\d{1,2}):(\d{2})\s*(am|pm)?',           # 14:30, 2:30 PM
            r'(\d{1,2})h(\d{2})?\s*(sáng|chiều|tối)?', # 12h30 sáng
            r'(\d{1,2})\s*giờ\s*(\d{2})?\s*(sáng|chiều|tối)?', # 12 giờ 30 sáng
            r'(\d{1,2})\s*(sáng|chiều|tối|trưa)',      # 12 chiều
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if match.group(2) else 0
                period = match.group(3) if len(match.groups()) > 2 else None
                
                # Xử lý AM/PM và sáng/chiều/tối
                if period:
                    if period in ['pm', 'chiều', 'tối'] and hour < 12:
                        hour += 12
                    elif period in ['am', 'sáng'] and hour == 12:
                        hour = 0
                    elif period == 'trưa' and hour < 12:
                        hour = 12
                
                if 0 <= hour <= 23 and 0 <= minute <= 59:
                    return {
                        'time': f"{hour:02d}:{minute:02d}",
                        'type': 'specific_time',
                        'original': match.group(0),
                        'hour': hour,
                        'minute': minute,
                        'period': period
                    }
        
        return None