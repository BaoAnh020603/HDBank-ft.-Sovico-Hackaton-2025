# Expected Input/Output Examples

Dựa trên logic thực tế của SmartOrchestrator và các agents trong source code.

## 🛫 Flight Search Scenarios

### 1. Tìm vé đầy đủ thông tin
**Input:** `"Tìm vé máy bay từ Hà Nội đến Đà Nẵng ngày mai"`

**Expected Output:**
```json
{
  "response": "🛫 Tìm thấy 4 chuyến bay từ Hà Nội đến Đà Nẵng ngày 31/01:\n\n1. ✈️ VietJet Air VJ456\n   ⏰ 06:00 - 💰 800,000đ - 🪑 15 ghế\n\n2. ✈️ Vietnam Airlines VN123\n   ⏰ 08:30 - 💰 1,200,000đ - 🪑 8 ghế\n\n3. ✈️ Jetstar Pacific BL789\n   ⏰ 10:15 - 💰 750,000đ - 🪑 22 ghế\n\n... và 1 chuyến khác\n",
  "suggestions": ["💰 Vé rẻ nhất", "✈️ Đặt chuyến 1", "🎁 Xem combo", "🎯 Đặt VJ456"],
  "context": {
    "slots": {
      "from_city": "HAN",
      "to_city": "DAD", 
      "date": "2025-01-31",
      "last_search_results": [...]
    }
  }
}
```

### 2. Thiếu điểm đi
**Input:** `"Tìm vé đến Đà Nẵng ngày mai"`

**Expected Output:**
```json
{
  "response": "Bạn muốn đi từ đâu đến Đà Nẵng?",
  "suggestions": ["🏙️ Từ Hà Nội", "🏙️ Từ TP.HCM", "🏙️ Từ Đà Nẵng"],
  "context": {
    "slots": {
      "to_city": "DAD",
      "date": "2025-01-31"
    }
  }
}
```

### 3. Thiếu cả điểm đi và đến
**Input:** `"Tìm vé máy bay ngày mai"`

**Expected Output:**
```json
{
  "response": "😊 Bạn muốn tìm vé máy bay từ đâu đến đâu ạ?",
  "suggestions": ["🛫 HN→DN", "🛫 HN→SGN", "🛫 SGN→DN", "💡 Hướng dẫn"],
  "context": {
    "slots": {
      "date": "2025-01-31"
    }
  }
}
```

## 💰 Price Check Scenarios

### 1. Kiểm tra giá sau khi có search results
**Input:** `"Vé rẻ nhất bao nhiêu?"` (sau khi đã tìm vé)

**Expected Output:**
```json
{
  "response": "💰 Vé rẻ nhất: 750,000đ - Jetstar Pacific BL789 lúc 10:15",
  "suggestions": ["🎯 Đặt vé này", "🔍 Xem thêm chuyến", "🏨 + Khách sạn", "📅 Thử ngày khác"],
  "context": {
    "slots": {
      "from_city": "HAN",
      "to_city": "DAD",
      "last_search_results": [...]
    }
  }
}
```

### 2. Kiểm tra giá không có context
**Input:** `"Cho tôi biết giá vé từ HN đến SGN"`

**Expected Output:**
```json
{
  "response": "💰 Vé rẻ nhất: 1,200,000đ - VietJet Air VJ789 lúc 07:30",
  "suggestions": ["🎯 Đặt vé này", "🔍 Xem thêm chuyến", "🏨 + Khách sạn", "📅 Thử ngày khác"],
  "context": {
    "slots": {
      "from_city": "HAN",
      "to_city": "SGN",
      "date": "2025-01-31"
    }
  }
}
```

## 🎯 Booking Scenarios

### 1. Đặt vé theo flight ID
**Input:** `"Đặt vé VN123"` (có search results trong context)

**Expected Output:**
```json
{
  "response": "🎉 Đặt vé thành công!\n\n🆔 Mã booking: BKGABC123\n💳 Mã thanh toán: PMTDEF456\n✈️ Vietnam Airlines VN123\n🛫 HAN → DAD\n📅 2025-01-31 - 08:30\n💰 Tổng tiền: 1,200,000đ\n⏰ Hạn thanh toán: 2025-02-01 08:30:00\n\n📞 Vui lòng thanh toán để giữ chỗ!",
  "suggestions": ["🏨 + Khách sạn", "🚗 + Xe đưa đón", "🎁 Gói combo", "📋 Xem booking"],
  "context": {
    "slots": {
      "flight_id": "VN123",
      "last_search_results": [...]
    },
    "booking_state": {
      "booking_id": "BKGABC123",
      "status": "pending_payment"
    }
  }
}
```

### 2. Đặt vé rẻ nhất
**Input:** `"Đặt vé rẻ nhất cho tôi"` (có search results)

**Expected Output:**
```json
{
  "response": "🎉 Đặt vé thành công!\n\n🆔 Mã booking: BKGXYZ789\n💳 Mã thanh toán: PMTUVW012\n✈️ Jetstar Pacific BL789\n🛫 HAN → DAD\n📅 2025-01-31 - 10:15\n💰 Tổng tiền: 750,000đ\n⏰ Hạn thanh toán: 2025-02-01 10:15:00\n\n📞 Vui lòng thanh toán để giữ chỗ!",
  "suggestions": ["🏨 + Khách sạn", "🚗 + Xe đưa đón", "🎁 Gói combo", "📋 Xem booking"],
  "context": {
    "slots": {
      "selection_criteria": "cheapest",
      "last_search_results": [...]
    }
  }
}
```

### 3. Đặt vé không có context
**Input:** `"Đặt vé VN123"` (không có search results)

**Expected Output:**
```json
{
  "response": "😊 Vui lòng tìm chuyến bay trước để tôi có thể hỗ trợ bạn.",
  "suggestions": ["🔍 Tìm chuyến bay", "🛫 HN→DN ngày mai"],
  "context": {
    "slots": {}
  }
}
```

## 🎁 Combo Scenarios

### 1. Xem combo có search results
**Input:** `"Có gói combo nào không?"` (sau khi tìm vé)

**Expected Output:**
```json
{
  "response": "Tạo được 2 gói combo phù hợp cho chuyến VJ456 của bạn!",
  "suggestions": ["✅ Đặt combo", "🔍 Combo khác", "💰 So sánh", "📞 Tư vấn"],
  "context": {
    "slots": {
      "last_search_results": [...],
      "combos": [
        {
          "combo_id": "CB123456",
          "name": "Combo VietJet Air + Vinpearl Resort Da Nang",
          "items": [
            {"type": "flight", "price": 800000},
            {"type": "hotel", "price": 2500000},
            {"type": "transfer", "price": 300000}
          ],
          "total_price": 3600000,
          "discount": 360000,
          "final_price": 3240000
        }
      ]
    }
  }
}
```

## 💬 Conversation Flow Examples

### Conversation 1: Thiếu thông tin -> Bổ sung -> Tìm -> Đặt

**Step 1:**
- Input: `"Ngày mai còn vé không?"`
- Output: `"😊 Bạn muốn tìm vé máy bay từ đâu đến đâu ạ?"`

**Step 2:**
- Input: `"Từ Hà Nội đến Đà Nẵng"`
- Output: `"🛫 Tìm thấy 4 chuyến bay từ Hà Nội đến Đà Nẵng ngày 31/01:..."`

**Step 3:**
- Input: `"Giá vé bao nhiêu?"`
- Output: `"💰 Vé rẻ nhất: 750,000đ - Jetstar Pacific BL789 lúc 10:15"`

**Step 4:**
- Input: `"Đặt vé rẻ nhất"`
- Output: `"🎉 Đặt vé thành công! Mã booking: BKGXYZ789..."`

## 🧠 Context Awareness Examples

### Context Persistence Test

**Step 1:** Tạo context
- Input: `"Tìm vé HN đi DN ngày mai"`
- Context được lưu: `{from_city: "HAN", to_city: "DAD", last_search_results: [...]}`

**Step 2:** Sử dụng context
- Input: `"Giá bao nhiêu?"` (không cần nói lại route)
- System tự hiểu dựa vào context và trả về giá vé HN-DN

**Step 3:** Tham chiếu
- Input: `"Đặt vé đó"` 
- System hiểu "vé đó" là vé rẻ nhất từ search results trước

## ⚠️ Edge Cases

### 1. Route không tồn tại
**Input:** `"Tìm vé từ Hà Nội đến Tokyo"`
**Output:** `"😔 Không tìm thấy chuyến bay phù hợp. Bạn thử ngày khác nhé!"`

### 2. Câu hỏi không liên quan
**Input:** `"Thời tiết hôm nay thế nào?"`
**Output:** `"😊 Tôi có thể giúp gì cho bạn?"` + suggestions: `["🛫 Tìm vé", "💰 Xem giá", "🎁 Combo"]`

### 3. Input rỗng
**Input:** `""`
**Output:** `"😊 Tôi có thể giúp gì cho bạn?"` + default suggestions

## 🇻🇳 Vietnamese Variations

Các cách nói khác nhau cho cùng một intent:

**Flight Search:**
- `"Tìm vé máy bay HN đi DN"`
- `"Tôi muốn bay từ Hà Nội đến Đà Nẵng"`
- `"Có chuyến nào từ HN về DN không?"`
- `"Book vé HN-DN"`
- `"Kiếm vé bay HN -> DN"`

→ Tất cả đều được nhận diện là `flight_search` intent với slots tương tự.

---

## 📊 Key Logic Points từ Source Code

1. **NLU Processing**: `utils/nlu.py` xử lý tiếng Việt với fuzzy matching
2. **Context Management**: Lưu trữ `last_search_results` để tham chiếu sau
3. **Agent Selection**: Rule-based + AI-powered selection
4. **Dynamic Data**: `data/mock_data.py` generate flights theo route/date
5. **Smart Suggestions**: Dựa trên intent và context state
6. **Error Handling**: Vietnamize error messages
7. **Reference Resolution**: Xử lý "vé đó", "chuyến này", "rẻ nhất"