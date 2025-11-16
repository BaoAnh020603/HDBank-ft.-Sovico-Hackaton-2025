# 🧪 KỊCH BẢN TEST AI - BOOKING AGENT

## 🎯 Mục Tiêu Test

Đảm bảo hệ thống AI hoạt động trơn tru, hiểu chính xác ý định người dùng Việt Nam, và cung cấp thông tin chuẩn xác trong mọi tình huống thực tế.

## 📋 KỊCH BẢN TEST CHÍNH

### 🔍 **Scenario 1: Flight Search - Basic**

**User Input:** "Tìm vé từ Sài Gòn đi Hà Nội ngày mai"

**Expected AI Behavior:**
- ✅ Nhận diện: from_city="Ho Chi Minh City", to_city="Hanoi", date="ngày mai"
- ✅ Gọi SearchAgent với normalized parameters
- ✅ Trả về 5-8 chuyến bay VietJet với giá 1.2M-2.0M VNĐ
- ✅ Format response: "🛫 Tìm thấy 6 chuyến bay từ TP.HCM đến Hà Nội..."

**Test Questions:**
```
Q: "Tìm vé từ HCM đi HN ngày mai"
Q: "Có vé máy bay từ Sài Gòn về Hà Nội không?"
Q: "Tôi muốn bay từ TP.HCM đến thủ đô ngày mai"
Q: "SGN to HAN tomorrow"
```

### 💰 **Scenario 2: Price Inquiry - Context Aware**

**User Input:** "Vé rẻ nhất bao nhiêu?"

**Expected AI Behavior:**
- ✅ Sử dụng context từ search trước đó
- ✅ Gọi PriceAgent để tìm cheapest flight
- ✅ Highlight vé rẻ nhất với details
- ✅ Suggest booking action

**Test Questions:**
```
Q: "Giá vé bao nhiêu?"
Q: "Vé nào rẻ nhất?"
Q: "Cho tôi biết giá vé rẻ nhất"
Q: "Bao nhiêu tiền một vé?"
```

### 📝 **Scenario 3: Booking Intent Detection**

**User Input:** "Đặt vé rẻ nhất"

**Expected AI Behavior:**
- ✅ SmartIntentAgent detect should_book=true
- ✅ Start BookingIntentAgent workflow
- ✅ Display flight info + request phone number
- ✅ Create booking session

**Test Questions:**
```
Q: "Đặt vé này"
Q: "Tôi muốn book vé rẻ nhất"
Q: "Mua vé VJ112"
Q: "Đặt chuyến 6h sáng"
```

### 📱 **Scenario 4: Booking Flow - Phone Collection**

**User Input:** "0901234567"

**Expected AI Behavior:**
- ✅ Validate phone format (10 digits, starts with 0)
- ✅ Check user database
- ✅ Display user info for confirmation
- ✅ Move to next step

**Test Questions:**
```
Q: "0901234567" (valid)
Q: "901234567" (missing 0)
Q: "090123456" (too short)
Q: "09012345678" (too long)
```

### ✅ **Scenario 5: User Confirmation**

**User Input:** "Đúng"

**Expected AI Behavior:**
- ✅ Accept confirmation
- ✅ Request CCCD + SMS phone
- ✅ Provide clear format example
- ✅ Update session state

**Test Questions:**
```
Q: "Đúng"
Q: "OK"
Q: "Chính xác"
Q: "Sai" (should allow editing)
```

### 🆔 **Scenario 6: CCCD & SMS Collection**

**User Input:** "CCCD: 123456789012, SMS: 0901234567"

**Expected AI Behavior:**
- ✅ Parse CCCD (12-15 digits)
- ✅ Parse SMS phone (10 digits)
- ✅ Generate and send SMS code
- ✅ Display test code for demo

**Test Questions:**
```
Q: "CCCD: 123456789012, SMS: 0901234567"
Q: "123456789012 và 0901234567"
Q: "CCCD 123456789012"
Q: "Chỉ có CCCD thôi: 123456789012"
```

### 📲 **Scenario 7: SMS Verification**

**User Input:** "123456"

**Expected AI Behavior:**
- ✅ Verify SMS code
- ✅ Complete booking
- ✅ Generate confirmation code
- ✅ Show SOVICO upselling

**Test Questions:**
```
Q: "123456" (correct code)
Q: "654321" (wrong code)
Q: "12345" (too short)
Q: "abcdef" (not numbers)
```

### 🏨 **Scenario 8: Upselling Response**

**User Input:** "Khách sạn Hà Nội"

**Expected AI Behavior:**
- ✅ Analyze destination (Hanoi = cultural city)
- ✅ Show Sovico hotels in Hanoi
- ✅ Prioritize heritage tours
- ✅ Include pricing and discounts

**Test Questions:**
```
Q: "Khách sạn Hà Nội"
Q: "Có tour gì ở Hà Nội không?"
Q: "Xe đưa đón sân bay"
Q: "Không cần dịch vụ thêm"
```

## 🧠 ADVANCED TEST SCENARIOS

### 🌟 **Scenario 9: Complex Multi-Intent**

**User Input:** "Tìm vé từ HCM đi Đà Nẵng cuối tuần này cho 2 người, giá dưới 3 triệu, cần khách sạn gần biển"

**Expected AI Behavior:**
- ✅ Parse multiple intents: flight_search + hotel_inquiry
- ✅ Extract: from="HCM", to="Da Nang", passengers=2, budget=3M, hotel_type="beach"
- ✅ Process flight search first
- ✅ Suggest beach hotels in Da Nang

### 🔄 **Scenario 10: Context Switching**

**Conversation Flow:**
```
User: "Tìm vé HCM đi HN ngày mai"
Bot: [Shows flights]
User: "Thôi, tôi muốn đi Đà Nẵng"
Bot: [Should switch to HCM-DAD route]
User: "Vé đó bao nhiêu?"
Bot: [Should refer to Da Nang flights, not Hanoi]
```

### ❌ **Scenario 11: Error Handling**

**Test Cases:**
```
Q: "Tìm vé đi Mỹ" → "Tôi chỉ hỗ trợ VietJet Air - chuyến bay nội địa"
Q: "Đặt vé Vietnam Airlines" → "Về vé máy bay, tôi chỉ hỗ trợ VietJet Air"
Q: "Tôi muốn hủy vé" → "Tính năng hủy vé đang được phát triển"
Q: "Blah blah random text" → "Xin lỗi, tôi không hiểu. Bạn có thể nói rõ hơn?"
```

### 🎭 **Scenario 12: Edge Cases**

**Tricky Inputs:**
```
Q: "HN đi DN" → Should understand Hanoi to Da Nang
Q: "Bay về quê" → Should ask "Quê bạn ở đâu?"
Q: "Vé Tết" → Should handle holiday context
Q: "Chuyến sáng sớm" → Should filter 6-9AM flights
Q: "Ghế cửa sổ" → Should note preference for future
```

## 🎯 VALIDATION CRITERIA

### ✅ **Response Quality Checklist**

**Language & Tone:**
- [ ] Sử dụng tiếng Việt tự nhiên
- [ ] Tone thân thiện, chuyên nghiệp
- [ ] Có emoji phù hợp
- [ ] Không có lỗi chính tả

**Information Accuracy:**
- [ ] Giá vé realistic (1.2M-2.5M VNĐ)
- [ ] Thời gian bay hợp lý (6:00-21:15)
- [ ] Tên chuyến bay đúng format (VJ112, VJ114...)
- [ ] Địa danh chính xác

**Conversation Flow:**
- [ ] Nhớ context từ câu trước
- [ ] Suggestions phù hợp với tình huống
- [ ] Chuyển đổi topic mượt mà
- [ ] Error recovery graceful

**Business Logic:**
- [ ] Chỉ tư vấn VietJet Air
- [ ] Upselling SOVICO services
- [ ] Booking flow 5 steps đúng thứ tự
- [ ] Validation input chặt chẽ

## 🚀 PERFORMANCE BENCHMARKS

**Response Time:**
- [ ] <1s cho fallback mode
- [ ] <3s cho LLM mode
- [ ] <5s cho complex queries

**Accuracy Targets:**
- [ ] Intent detection: >95%
- [ ] Location recognition: >98%
- [ ] Booking completion: >85%
- [ ] Context retention: >90%

## 🔧 DEBUGGING SCENARIOS

### **When AI Fails:**

**Symptom:** AI không hiểu địa danh
**Debug:** Check location_mapping trong VietnameseNLU
**Fix:** Thêm aliases mới

**Symptom:** Booking flow bị stuck
**Debug:** Check session state trong context storage
**Fix:** Reset booking_session

**Symptom:** Response không có emoji
**Debug:** Check _generate_vietnamese_response
**Fix:** Update response templates

**Symptom:** LLM timeout
**Debug:** Check API keys và network
**Fix:** Fallback to custom logic

## 📊 SUCCESS METRICS

**Daily Testing:**
- Run 50+ test scenarios
- 95%+ pass rate required
- <2% regression tolerance
- Document all failures

**User Acceptance:**
- Natural conversation flow
- Accurate information
- Fast response time
- Helpful suggestions

**Business Impact:**
- Booking conversion >75%
- Upselling rate >30%
- User satisfaction >4.0/5
- Time to booking <5 minutes

---

**Kịch bản test này đảm bảo AI hoạt động ổn định, chính xác và thân thiện với người dùng Việt Nam trong mọi tình huống thực tế.**