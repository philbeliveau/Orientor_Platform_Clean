#!/bin/bash

# Prisma + Railway Setup Script for Orientor Platform
# This script guides you through setting up Prisma with your Railway database

echo "🚀 Orientor Platform - Prisma + Railway Setup"
echo "=============================================="

# Check if we're in the backend directory
if [ ! -f "prisma/schema.prisma" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    echo "   cd backend && bash scripts/setup_prisma.sh"
    exit 1
fi

echo "✅ Found Prisma schema"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found in backend directory"
    echo "   Please create backend/.env with your Railway DATABASE_URL"
    exit 1
fi

echo "✅ Found .env file"

# Check if DATABASE_URL is set
if ! grep -q "DATABASE_URL=" .env; then
    echo "❌ Error: DATABASE_URL not found in .env file"
    echo "   Please add your Railway DATABASE_URL to backend/.env"
    exit 1
fi

# Load environment variables (safer method)
source .env

if [ -z "$DATABASE_URL" ] || [ "$DATABASE_URL" = "postgresql://postgres:your_password@your_host:5432/railway" ]; then
    echo "❌ Error: Please update DATABASE_URL in .env with your actual Railway credentials"
    echo ""
    echo "To get your Railway DATABASE_URL:"
    echo "1. Go to railway.app dashboard"
    echo "2. Select your project"
    echo "3. Click on your database service"
    echo "4. Go to Variables tab"
    echo "5. Copy the DATABASE_URL value"
    echo "6. Update backend/.env file"
    exit 1
fi

echo "✅ DATABASE_URL configured"

# Test database connection
echo "🔌 Testing database connection..."
if npx prisma db execute --stdin <<< "SELECT 1 as test;" > /dev/null 2>&1; then
    echo "✅ Database connection successful"
else
    echo "❌ Database connection failed"
    echo "   Please check your DATABASE_URL in .env"
    exit 1
fi

# Run database introspection
echo "🔍 Running database introspection..."
if npx prisma db pull; then
    echo "✅ Database introspection completed"
else
    echo "❌ Database introspection failed"
    exit 1
fi

# Generate Prisma clients
echo "⚙️  Generating Prisma clients..."
if npx prisma generate; then
    echo "✅ TypeScript client generated"
else
    echo "❌ Client generation failed"
    exit 1
fi

# Generate Python client
echo "🐍 Generating Python client..."
if python -m prisma generate; then
    echo "✅ Python client generated"
else
    echo "❌ Python client generation failed"
    exit 1
fi

echo ""
echo "🎉 Prisma setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Review generated models in prisma/schema.prisma"
echo "2. Import Prisma client in your Python code:"
echo "   from app.generated.prisma import Prisma"
echo "3. Use type-safe queries in your FastAPI routes"
echo ""
echo "Example usage:"
echo "   prisma = Prisma()"
echo "   await prisma.connect()"
echo "   users = await prisma.user.find_many()"
echo "   await prisma.disconnect()"