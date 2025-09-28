#!/bin/bash

echo "🚀 Setting up AgentPay environment variables..."

# Frontend .env.local
cat > agent-pay-fe/.env.local << EOF
# NextAuth.js Configuration
NEXTAUTH_URL=http://localhost:3001
NEXTAUTH_SECRET=egSxFrOsBTotMKldSO0Z8XVtdWik9xTh7vPRRpJh2Rk=

# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://xwxshfngcxjrntgxwmzv.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=sb_publishable_wJUkAD3k5TS5EzeTk4IDWg_0EFpmaz2

# FastAPI Backend
NEXT_PUBLIC_FASTAPI_URL=http://localhost:8000

# Google OAuth Configuration (placeholder - set these up later)
GOOGLE_CLIENT_ID=placeholder-google-client-id
GOOGLE_CLIENT_SECRET=placeholder-google-client-secret

# Method API Configuration (placeholder - get from Method dashboard)
METHOD_API_KEY=placeholder-method-api-key
METHOD_ENVIRONMENT=sandbox
EOF

# Backend .env
cat > agent-pay-backend/.env << EOF
# Supabase Configuration
SUPABASE_URL=https://xwxshfngcxjrntgxwmzv.supabase.co
SUPABASE_SERVICE_KEY=sb_secret_Pc9wId9jxG60OH-_cQUK0Q_4Qn0oepP
SUPABASE_ANON_KEY=sb_publishable_wJUkAD3k5TS5EzeTk4IDWg_0EFpmaz2

# Method API Configuration
METHOD_API_KEY=placeholder-method-api-key
METHOD_ENVIRONMENT=sandbox

# AgentMail Configuration
AGENTMAIL_API_KEY=placeholder-agentmail-api-key

# FastAPI Configuration
SECRET_KEY=egSxFrOsBTotMKldSO0Z8XVtdWik9xTh7vPRRpJh2Rk=
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3001,http://localhost:3000

# Environment
ENVIRONMENT=development
EOF

echo "✅ Environment files created successfully!"
echo ""
echo "📁 Files created:"
echo "  - agent-pay-fe/.env.local"
echo "  - agent-pay-backend/.env"
echo ""
echo "🔧 Next steps:"
echo "  1. Set up database schema in Supabase"
echo "  2. Get Method API keys from Method dashboard"
echo "  3. Set up Google OAuth credentials (optional)"
echo "  4. Start both servers and test!"
echo ""
echo "🚀 To start the servers:"
echo "  Terminal 1: cd agent-pay-backend && uvicorn app.main:app --reload --port 8000"
echo "  Terminal 2: cd agent-pay-fe && npm run dev"

