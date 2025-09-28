# AgentPay Complete Setup Guide

## 🏗️ Architecture Overview

Your AgentPay application now uses this architecture:

```
Next.js Frontend → FastAPI Backend → Supabase Database
     ↓                    ↓              ↓
 - User Interface    - Business Logic  - Data Storage
 - Supabase Auth     - Method API      - PostgreSQL
 - Real-time UI      - Bill Processing - Row Security
```

## 🚀 Complete Setup Instructions

### 1. Set Up Supabase Project

1. **Create Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Click "New Project"
   - Choose organization and create project
   - Wait for project to initialize

2. **Run Database Schema**
   - Go to SQL Editor in Supabase dashboard
   - Copy and paste content from `agent-pay-fe/supabase/schema.sql`
   - Click "Run" to create tables and security policies

3. **Get Supabase Credentials**
   - Go to Settings → API
   - Copy `Project URL` and `anon public` key
   - Copy `service_role secret` key (for backend)

### 2. Set Up FastAPI Backend

```bash
# Navigate to backend
cd agent-pay-backend

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.template .env
# Edit .env with your Supabase credentials and Method API key
```

**Backend .env file:**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key
METHOD_API_KEY=your-method-api-key
METHOD_ENVIRONMENT=sandbox
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=http://localhost:3001,http://localhost:3000
ENVIRONMENT=development
```

### 3. Set Up Next.js Frontend

```bash
# Navigate to frontend
cd agent-pay-fe

# Install dependencies (if not already done)
npm install

# Configure environment
cp env.template .env.local
# Edit .env.local with your credentials
```

**Frontend .env.local file:**
```env
NEXTAUTH_URL=http://localhost:3001
NEXTAUTH_SECRET=your-generated-secret-here
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_FASTAPI_URL=http://localhost:8000
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 4. Start Development Servers

**Terminal 1: FastAPI Backend**
```bash
cd agent-pay-backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2: Next.js Frontend**
```bash
cd agent-pay-fe
npm run dev
```

## 🧪 Testing the Setup

### 1. Test Backend Health
```bash
curl http://localhost:8000/api/health
```

Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "environment": "development"
}
```

### 2. Test Frontend
- Open `http://localhost:3001` (or 3000)
- You should see the AgentPay landing page
- Click "Sign Up" or "Sign In"

### 3. Test Authentication Flow

**Option A: Email/Password (Mock - Development Only)**
- Use any email/password combination
- This will create a temporary session (not persistent)

**Option B: Google OAuth (Production Ready)**
- Set up Google OAuth credentials first
- Click "Continue with Google"
- Complete OAuth flow

### 4. Test API Integration

Once authenticated, the dashboard should:
- Call FastAPI backend for user data
- Show credit cards (empty initially)
- Display user settings

## 🔗 API Integration Testing

You can test the API endpoints directly:

```bash
# Get Supabase token (from browser dev tools after login)
TOKEN="your-supabase-jwt-token"

# Test user endpoint
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/users/me

# Test cards endpoint
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/cards/

# Test bills endpoint
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/bills/
```

## 🔧 Common Issues & Solutions

### Backend Won't Start
- **Check Python version**: Requires Python 3.8+
- **Check dependencies**: Run `pip install -r requirements.txt`
- **Check environment**: Ensure `.env` file exists with valid credentials

### Frontend API Calls Fail
- **Check FastAPI is running**: Visit `http://localhost:8000`
- **Check CORS**: Ensure `ALLOWED_ORIGINS` includes frontend URL
- **Check authentication**: Ensure user is logged in to Supabase

### Database Connection Issues
- **Check Supabase credentials**: Verify URL and keys are correct
- **Check schema**: Ensure database schema is created
- **Check RLS policies**: Row Level Security must be properly configured

### Authentication Issues
- **NextAuth**: Ensure `NEXTAUTH_SECRET` is set
- **Supabase**: Check project is active and credentials are correct
- **Google OAuth**: Verify client ID/secret and redirect URLs

## 📈 Next Development Steps

### Immediate Tasks:
1. **Set up real Supabase project** with your credentials
2. **Configure Google OAuth** for production authentication
3. **Get Method API keys** from Method Financial
4. **Test user registration** and credit card sync

### Feature Development:
1. **Implement Method API** - Real credit card integration
2. **Build bill parsing** - AI email processing
3. **Add payment processing** - Actual bill payments
4. **AgentMail integration** - Email webhook handling

### Production Deployment:
1. **Deploy FastAPI** to Railway/Render/DigitalOcean
2. **Deploy Next.js** to Vercel (already configured)
3. **Set up monitoring** and error tracking
4. **Configure domain** and SSL certificates

## 🎯 Current Status

✅ **Complete FastAPI backend** with all endpoints  
✅ **Supabase database** schema and security  
✅ **Next.js frontend** with API integration  
✅ **Authentication** system (NextAuth + Supabase)  
✅ **Development environment** ready  

🔄 **Next: Configure with real credentials and test end-to-end**

## 🆘 Getting Help

If you run into issues:
1. Check the terminal output for specific error messages
2. Verify all environment variables are set correctly
3. Ensure all services are running on correct ports
4. Test each component individually before full integration

Your AgentPay application is now ready for development and testing! 🚀

