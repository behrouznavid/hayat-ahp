#!/bin/bash

echo "🚀 Starting Hayat AHP System..."

# Start PostgreSQL
sudo service postgresql start

# Start Backend
cd /workspaces/hayat-ahp/backend
echo "📡 Starting Backend API on port 8000..."
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Start Frontend
cd /workspaces/hayat-ahp/frontend
echo "🌐 Starting Frontend on port 3000..."
npm start &

echo "✅ System is running!"
echo "   Frontend: http://localhost:3000"
echo "   API: http://localhost:8000"
echo "   Docs: http://localhost:8000/docs"

wait
