# Realistic Input/Output Examples

Các test cases thực tế và hợp lý dựa trên logic source code.

## 🎯 Test Case 1: Tìm vé đầy đủ thông tin

**INPUT:**
```
"Tìm vé từ Hà Nội đến Đà Nẵng ngày mai"
```

**EXPECTED OUTPUT:**
```
Response: "🛫 Tìm thấy 4 chuyến bay từ Hà Nội đến Đà Nẵng ngày 31/01:

1. ✈️ VietJet Air VJ456
   ⏰ 06:00 - 💰 800,000đ - 🪑 15 ghế

2. ✈️ Vietnam Airlines VN123  
   ⏰ 08:30 - 💰 1,200,000đ - 🪑 8 ghế

3. ✈️ Jetstar Pacific BL789
   ⏰ 10:15 - 💰 750,000đ - 🪑 22 ghế

... và 1 chuyến khác"

Suggestions: ["💰 Vé rẻ nhất", "✈️ Đặt chuyến 1", "🎁 Xem combo", "🎯 Đặt VJ456"]
```

**Logic:** 
- NLU extract: `from_city="HAN"`, `to_city="DAD"`, `date="2025-01-31"`
- Agent: SearchAgent
- Dynamic flight generation từ mock_data.py
- Context lưu `last_search_results`

---

## 💰 Test Case 2: Hỏi giá (có context)

**INPUT:**
```
"Vé rẻ nhất bao nhiêu?"
```

**EXPECTED OUTPUT:**
```
Response: "💰 Vé rẻ nhất: 750,000đ - Jetstar Pacific BL789 lúc 10:15"

Suggestions: ["🎯 Đặt vé này", "🔍 Xem thêm chuyến", "🏨 + Khách sạn", "📅 Thử ngày khác"]
```

**Logic:**
- Intent: `price_check`
- Sử dụng `last_search_results` từ context
- Agent: PriceAgent tìm cheapest flight
- Không cần route info vì có context

---

## 🎯 Test Case 3: Đặt vé

**INPUT:**
```
"Đặt vé rẻ nhất cho tôi"
```

**EXPECTED OUTPUT:**
```
Response: "🎉 Đặt vé thành công!

🆔 Mã booking: BKGABC123
💳 Mã thanh toán: PMTDEF456
✈️ Jetstar Pacific BL789
🛫 HAN → DAD
📅 2025-01-31 - 10:15
💰 Tổng tiền: 750,000đ
⏰ Hạn thanh toán: 2025-02-01 10:15:00

📞 Vui lòng thanh toán để giữ chỗ!"

Suggestions: ["🏨 + Khách sạn", "🚗 + Xe đưa đón", "🎁 Gói combo", "📋 Xem booking"]
```

**Logic:**
- Intent: `booking`
- Slots: `selection_criteria="cheapest"`
- Agent: BookingAgent tìm cheapest từ context
- Generate booking_id, payment_code
- Update seats_left

---

## ❓ Test Case 4: Thiếu thông tin

**INPUT:**
```
"Tìm vé ngày mai"
```

**EXPECTED OUTPUT:**
```
Response: "😊 Bạn muốn tìm vé máy bay từ đâu đến đâu ạ?"

Suggestions: ["🛫 HN→DN", "🛫 HN→SGN", "🛫 SGN→DN", "💡 Hướng dẫn"]
```

**Logic:**
- Intent: `flight_search`
- Missing: `from_city`, `to_city`
- `_has_sufficient_info()` return False
- `_handle_missing_info()` được gọi

---

## 🎁 Test Case 5: Combo (có context)

**INPUT:**
```
"Có combo nào không?"
```

**EXPECTED OUTPUT:**
```
Response: "Tạo được 2 gói combo phù hợp cho chuyến VJ456 của bạn!"

Suggestions: ["✅ Đặt combo", "🔍 Combo khác", "💰 So sánh", "📞 Tư vấn"]
```

**Logic:**
- Intent: `combo_service`
- Agent: ComboAgent
- Sử dụng `last_search_results[0]` để tạo combo
- Dynamic combo generation với hotel + transfer

---

## 🔄 Conversation Flow Example

**Conversation 1: Thiếu thông tin → Bổ sung → Đặt vé**

```
User: "Ngày mai còn vé không?"
Bot: "😊 Bạn muốn tìm vé máy bay từ đâu đến đâu ạ?"

User: "Từ Hà Nội đến Đà Nẵng"  
Bot: "🛫 Tìm thấy 4 chuyến bay từ Hà Nội đến Đà Nẵng..."

User: "Đặt vé rẻ nhất"
Bot: "🎉 Đặt vé thành công! Mã booking: BKGABC123..."
```

---

## 🧠 Context Awareness Example

**Context Persistence:**

```
Step 1: "Tìm vé HN đi DN ngày mai"
→ Context: {from_city: "HAN", to_city: "DAD", last_search_results: [...]}

Step 2: "Giá bao nhiêu?" (không cần nói lại route)
→ System hiểu dựa vào context

Step 3: "Đặt vé đó"
→ System hiểu "vé đó" = cheapest từ search results
```

---

## ⚠️ Edge Cases

### Route không tồn tại
```
Input: "Tìm vé từ Hà Nội đến Tokyo"
Output: "😔 Không tìm thấy chuyến bay phù hợp. Bạn thử ngày khác nhé!"
```

### Câu hỏi không liên quan
```
Input: "Thời tiết hôm nay thế nào?"
Output: "😊 Tôi có thể giúp gì cho bạn?"
Suggestions: ["🛫 Tìm vé", "💰 Xem giá", "🎁 Combo"]
```

---

## 📊 Key Logic Points

1. **NLU**: `utils/nlu.py` - Extract intent + slots từ Vietnamese text
2. **Context**: Lưu `last_search_results` để reference sau
3. **Agent Selection**: Rule-based mapping intent → agent
4. **Dynamic Data**: Generate flights/hotels/combos on-demand
5. **Smart Suggestions**: Dựa trên intent và context state
6. **Error Handling**: Vietnamize messages, handle missing info
7. **Reference Resolution**: "vé đó", "chuyến này", "rẻ nhất"

---

## 🎯 Realistic vs Unrealistic

### ✅ Realistic:
- User nói thiếu thông tin → Bot hỏi thêm
- Context được nhớ giữa các lượt chat
- Suggestions phù hợp với trạng thái
- Vietnamese natural language
- Error handling graceful

### ❌ Unrealistic:
- Perfect JSON responses mọi lúc
- User luôn cung cấp đầy đủ thông tin
- Không có lỗi network/system
- Context không bao giờ bị mất
- User luôn follow happy path