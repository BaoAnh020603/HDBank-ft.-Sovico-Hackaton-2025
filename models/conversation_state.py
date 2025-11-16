from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class TrangThaiHoiThoai(str, Enum):
    BAN_DAU = "ban_dau"           # Chưa có thông tin
    THU_THAP = "thu_thap"         # Đang thu thập thông tin
    TIM_KIEM = "tim_kiem"         # Đang tìm kiếm
    SO_SANH = "so_sanh"          # Đang so sánh
    QUYET_DINH = "quyet_dinh"    # Sắp quyết định
    DAT_VE = "dat_ve"            # Đang đặt vé
    HOAN_THANH = "hoan_thanh"    # Hoàn thành

class NguyenVongKhachHang(BaseModel):
    """Nguyện vọng tích lũy của khách hàng"""
    from_city: Optional[str] = None
    to_city: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    time_range: Optional[str] = None
    class_type: Optional[str] = None
    preferences: List[str] = []
    max_price: Optional[int] = None
    
    def update(self, new_slots: Dict[str, Any]):
        """Cập nhật nguyện vọng với thông tin mới"""
        for key, value in new_slots.items():
            if hasattr(self, key) and value:
                if key == "preferences" and isinstance(value, list):
                    # Merge preferences
                    existing = getattr(self, key) or []
                    setattr(self, key, list(set(existing + value)))
                else:
                    setattr(self, key, value)
    
    def is_complete_for_search(self) -> bool:
        """Kiểm tra đủ thông tin để tìm kiếm"""
        return bool(self.from_city and self.to_city)
    
    def get_missing_info(self) -> List[str]:
        """Lấy danh sách thông tin còn thiếu"""
        missing = []
        if not self.from_city:
            missing.append("điểm đi")
        if not self.to_city:
            missing.append("điểm đến")
        if not self.date:
            missing.append("ngày bay")
        return missing

class ThamChieu(BaseModel):
    """Xử lý tham chiếu trong hội thoại"""
    last_mentioned_flight: Optional[Dict[str, Any]] = None
    last_search_results: List[Dict[str, Any]] = []
    last_price_check: Optional[Dict[str, Any]] = None
    current_selection: Optional[Dict[str, Any]] = None
    
    def resolve_reference(self, ref_text: str) -> Optional[Dict[str, Any]]:
        """Giải quyết tham chiếu như 'vé đó', 'chuyến này'"""
        ref_lower = ref_text.lower()
        
        if any(word in ref_lower for word in ["đó", "này", "vé đó", "chuyến này"]):
            return self.current_selection or self.last_mentioned_flight
        elif "rẻ nhất" in ref_lower and self.last_search_results:
            return min(self.last_search_results, key=lambda x: x["price"])
        elif "đắt nhất" in ref_lower and self.last_search_results:
            return max(self.last_search_results, key=lambda x: x["price"])
        elif "đầu tiên" in ref_lower and self.last_search_results:
            return self.last_search_results[0]
        elif "cuối" in ref_lower and self.last_search_results:
            return self.last_search_results[-1]
        
        return None

class ConversationStateManager(BaseModel):
    """Quản lý trạng thái hội thoại nâng cao"""
    user_id: str
    trang_thai: TrangThaiHoiThoai = TrangThaiHoiThoai.BAN_DAU
    nguyen_vong: NguyenVongKhachHang = NguyenVongKhachHang()
    tham_chieu: ThamChieu = ThamChieu()
    lich_su_y_dinh: List[str] = []
    last_updated: datetime = datetime.now()
    
    def update_state(self, intent: str, slots: Dict[str, Any], agent_response: Dict[str, Any]):
        """Cập nhật trạng thái dựa trên intent và kết quả"""
        # Cập nhật nguyện vọng
        self.nguyen_vong.update(slots)
        
        # Cập nhật lịch sử ý định
        if intent not in self.lich_su_y_dinh[-3:]:  # Chỉ giữ 3 intent gần nhất
            self.lich_su_y_dinh.append(intent)
            if len(self.lich_su_y_dinh) > 3:
                self.lich_su_y_dinh.pop(0)
        
        # Cập nhật tham chiếu
        if intent == "flight_search" and agent_response.get("success"):
            flights = agent_response.get("data", {}).get("flights", [])
            self.tham_chieu.last_search_results = flights
            if flights:
                self.tham_chieu.last_mentioned_flight = flights[0]
        
        elif intent == "price_check" and agent_response.get("success"):
            self.tham_chieu.last_price_check = agent_response.get("data", {})
        
        # Cập nhật trạng thái hội thoại
        self._update_conversation_state(intent, agent_response)
        
        self.last_updated = datetime.now()
    
    def _update_conversation_state(self, intent: str, agent_response: Dict[str, Any]):
        """Cập nhật trạng thái hội thoại"""
        if self.trang_thai == TrangThaiHoiThoai.BAN_DAU:
            if not self.nguyen_vong.is_complete_for_search():
                self.trang_thai = TrangThaiHoiThoai.THU_THAP
            elif intent == "flight_search":
                self.trang_thai = TrangThaiHoiThoai.TIM_KIEM
        
        elif self.trang_thai == TrangThaiHoiThoai.THU_THAP:
            if self.nguyen_vong.is_complete_for_search():
                if intent == "flight_search":
                    self.trang_thai = TrangThaiHoiThoai.TIM_KIEM
        
        elif self.trang_thai == TrangThaiHoiThoai.TIM_KIEM:
            if intent == "price_check":
                self.trang_thai = TrangThaiHoiThoai.SO_SANH
            elif intent == "booking":
                self.trang_thai = TrangThaiHoiThoai.DAT_VE
        
        elif self.trang_thai == TrangThaiHoiThoai.SO_SANH:
            if intent == "booking":
                self.trang_thai = TrangThaiHoiThoai.DAT_VE
            elif intent == "flight_search":
                self.trang_thai = TrangThaiHoiThoai.TIM_KIEM
        
        elif self.trang_thai == TrangThaiHoiThoai.DAT_VE:
            if agent_response.get("success") and "booking_id" in agent_response.get("data", {}):
                self.trang_thai = TrangThaiHoiThoai.HOAN_THANH
    
    def get_next_action_suggestion(self) -> str:
        """Gợi ý hành động tiếp theo"""
        if self.trang_thai == TrangThaiHoiThoai.BAN_DAU:
            return "Bạn muốn tìm vé máy bay từ đâu đến đâu?"
        
        elif self.trang_thai == TrangThaiHoiThoai.THU_THAP:
            missing = self.nguyen_vong.get_missing_info()
            if missing:
                return f"Bạn có thể cho biết thêm {', '.join(missing)} không?"
        
        elif self.trang_thai == TrangThaiHoiThoai.TIM_KIEM:
            if self.tham_chieu.last_search_results:
                return "Bạn có muốn xem giá chi tiết hoặc đặt vé không?"
        
        elif self.trang_thai == TrangThaiHoiThoai.SO_SANH:
            return "Bạn có muốn đặt vé nào không? Tôi có thể hỗ trợ đặt ngay."
        
        return ""
    
    def should_ask_for_booking(self) -> bool:
        """Kiểm tra có nên hỏi đặt vé không"""
        return (self.trang_thai in [TrangThaiHoiThoai.SO_SANH, TrangThaiHoiThoai.QUYET_DINH] 
                and len(self.lich_su_y_dinh) >= 2 
                and "booking" not in self.lich_su_y_dinh)