FROM agrigorev/zoomcamp-model:mlops-2024-3.10.13-slim

WORKDIR /app

COPY hw_4.py .

RUN pip install --no-cache-dir pandas numpy pyarrow scikit-learn

CMD ["python", "hw_4.py", "--year", "2023", "--month", "5"]