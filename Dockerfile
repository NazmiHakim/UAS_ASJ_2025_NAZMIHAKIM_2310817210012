# Gunakan image dasar Python
FROM python:3.9-slim

# Tetapkan direktori kerja di dalam container
WORKDIR /app

# Salin file requirements terlebih dahulu untuk caching layer
COPY requirements.txt requirements.txt

# Instal dependensi Python
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode aplikasi ke dalam direktori kerja
COPY ./app /app

# Ekspos port yang akan digunakan oleh aplikasi Flask di dalam container
EXPOSE 5000

# Menggunakan 'flask run' untuk memanfaatkan development server dengan live reload
CMD ["flask", "--app", "app:create_app", "run", "--host=0.0.0.0", "--debugger"]