# 🛫 Smart Booking Agent

AI-powered flight booking assistant với context awareness sử dụng LangChain và Streamlit.

## 🚀 Quick Start

### Docker (Khuyến nghị)

```bash
# 1. Clone và setup
git clone <repo-url>
cd booking-agent

# 2. Tạo file .env
cp .env.example .env
# Điền GOOGLE_API_KEY vào file .env

# 3. Chạy với Docker
docker-compose up --build
```

**Truy cập:**
- Streamlit UI: http://localhost:8501
- FastAPI: http://localhost:8000

### Local Development

```bash
# 1. Cài đặt dependencies
pip install -r requirements.txt

# 2. Setup environment
cp .env.example .env
# Điền API keys

# 3. Chạy Streamlit
streamlit run app.py

# 4. Hoặc chạy API
python main.py
```

## 📁 Cấu trúc Project

```
booking-agent/
├── agents/              # AI agents (booking, search, payment...)
├── langchain_agents/    # LangChain orchestrators
├── models/             # Data models và schemas
├── utils/              # Utilities (NLU, parsers...)
├── data/               # Mock data và contexts
├── app.py              # Streamlit UI
├── main.py             # FastAPI server
└── docker-compose.yml  # Docker setup
```

## ⚙️ Environment Variables

```env
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-1.5-flash
LLM_PROVIDER=gemini
OPENAI_API_KEY=your_openai_api_key_here  # Optional
```

## 🐳 Docker Commands

```bash
# Build và chạy tất cả
docker-compose up --build

# Chỉ chạy Streamlit
docker-compose run booking-agent /app/start.sh streamlit

# Chỉ chạy API
docker-compose run booking-agent /app/start.sh api

# Stop services
docker-compose down
```

## 🔧 Development

```bash
# Cài đặt dev dependencies
pip install -r requirements.txt

# Chạy tests
python -m pytest

# Generate mock data
python scripts/generate_mock_data.py
```

## 📋 Features

- **Multi-Agent System**: Booking, search, payment, upselling agents
- **Context Awareness**: Lưu trữ và theo dõi conversation context
- **Smart Orchestration**: Intelligent routing giữa các agents
- **Streamlit UI**: Giao diện chat thân thiện
- **FastAPI Backend**: RESTful API endpoints
- **Mock Data**: Dữ liệu test cho development

## 🛠️ Tech Stack

- **AI/ML**: LangChain, Google Gemini
- **Backend**: FastAPI, Pydantic
- **Frontend**: Streamlit
- **Data**: JSON-based mock data
- **Deployment**: Docker, Docker Compose
