#!/bin/bash
set -e

echo "🚀 شروع نصب سیستم AHP پروژه حیات..."

# نصب PostgreSQL
echo "📦 نصب PostgreSQL..."
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib
sudo service postgresql start

# ساخت دیتابیس
echo "🗄️ ساخت دیتابیس..."
sudo -u postgres psql -c "CREATE USER hayat_user WITH PASSWORD 'hayat_pass_2025';" || true
sudo -u postgres psql -c "CREATE DATABASE hayat_db OWNER hayat_user;" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE hayat_db TO hayat_user;" || true

# نصب وابستگی‌های Python
echo "🐍 نصب وابستگی‌های Backend..."
pip install --upgrade pip
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-jose passlib bcrypt python-multipart openpyxl

# نصب وابستگی‌های Node
echo "📦 نصب وابستگی‌های Frontend..."
cd frontend 2>/dev/null || mkdir -p frontend
npm install --legacy-peer-deps || true

# ساخت فایل شروع
echo "📝 ساخت اسکریپت راه‌اندازی..."
cat > /workspaces/hayat-ahp/start.sh << 'EOF'
#!/bin/bash

echo "🔄 شروع سرویس‌ها..."

# شروع PostgreSQL
sudo service postgresql start

# شروع Backend
cd /workspaces/hayat-ahp/backend
uvicorn main:app --host 0.0.0.0 --port 8000 &

# شروع Frontend
cd /workspaces/hayat-ahp/frontend
npm start &

echo "✅ همه سرویس‌ها آماده هستند!"
echo "🌐 Frontend: http://localhost:300 Backend API: http://localhost:8000"
echo "📚 مسندات API: http://localhost:8000/docs"

wait
EOF

chmod +x /workspaces/hayat-ahp/start.sh

echo "✅ نصب کامل شد! برای شروع: ./start.sh"
