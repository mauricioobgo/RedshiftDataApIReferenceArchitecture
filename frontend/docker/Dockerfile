FROM --platform=linux/amd64 python:3.12-slim

WORKDIR /app

COPY frontend/requirements_streamlit.txt .
RUN pip install --no-cache-dir -r requirements_streamlit.txt

COPY frontend/streamlit/streamlit_app.py .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
