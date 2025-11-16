FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements*.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
EXPOSE 8501 8000

# Create startup script
RUN echo '#!/bin/bash\n\
if [ "$1" = "streamlit" ]; then\n\
    streamlit run app.py --server.port=8501 --server.address=0.0.0.0\n\
elif [ "$1" = "api" ]; then\n\
    python main.py\n\
else\n\
    streamlit run app.py --server.port=8501 --server.address=0.0.0.0 &\n\
    python main.py\n\
fi' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]