# Hafif bir Python imajı kullanıyoruz
FROM python:3.11-slim

# Logların anlık olarak Coolify terminaline düşmesi için (ÖNEMLİ)
ENV PYTHONUNBUFFERED=1

# Çalışma dizinini oluştur
WORKDIR /app

# Önce requirements dosyasını kopyala (Cache optimizasyonu için)
COPY requirements.txt .

# Kütüphaneleri yükle
RUN pip install --no-cache-dir -r requirements.txt

# Kalan tüm dosyaları kopyala
COPY . .

# Botu başlat
CMD ["python", "main.py"]