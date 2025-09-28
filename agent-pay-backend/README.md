# AgentPay FastAPI Backend

## 🚀 Quick Start

### 1. Set up Python Environment
```bash
cd agent-pay-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
```bash
cp env.template .env
# Edit .env with your actual values
```

### 3. Run the Server
```bash
# Development
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📁 Project Structure

```
agent-pay-backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── database.py          # Supabase connection
│   ├── models/              # Pydantic models
│   │   ├── user.py
│   │   ├── card.py
│   │   └── bill.py
│   ├── routers/             # API endpoints
│   │   ├── users.py         # User management
│   │   ├── cards.py         # Credit card operations
│   │   ├── bills.py         # Bill management
│   │   └── payments.py      # Payment history
│   ├── services/            # External API integrations
│   │   └── method_api.py    # Method Financial API
│   └── utils/
│       └── auth.py          # Authentication utilities
├── requirements.txt
├── env.template
└── README.md
```

## 🔌 API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /api/health` - Detailed health check with database status

### Users
- `GET /api/users/me` - Get current user profile
- `PUT /api/users/me` - Update user profile
- `GET /api/users/settings` - Get user settings
- `PUT /api/users/settings` - Update user settings
- `POST /api/users/method-account` - Create Method account

### Credit Cards
- `GET /api/cards/` - Get user's credit cards
- `POST /api/cards/sync` - Sync cards from Method API
- `GET /api/cards/{card_id}` - Get specific card
- `PUT /api/cards/{card_id}` - Update card settings
- `DELETE /api/cards/{card_id}` - Delete card

### Bills
- `GET /api/bills/` - Get user's bills
- `POST /api/bills/` - Create new bill
- `POST /api/bills/process` - Process bill email
- `GET /api/bills/{bill_id}` - Get specific bill
- `PUT /api/bills/{bill_id}` - Update bill
- `DELETE /api/bills/{bill_id}` - Delete bill
- `POST /api/bills/{bill_id}/pay` - Pay bill

### Payments
- `GET /api/payments/` - Get payment history
- `GET /api/payments/sync` - Sync from Method API
- `GET /api/payments/{payment_id}` - Get specific payment

## 🔐 Authentication

The API uses Supabase JWT tokens for authentication. Include the token in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_SUPABASE_JWT_TOKEN" \
     http://localhost:8000/api/users/me
```

## 🗄️ Database

Uses Supabase PostgreSQL with the following tables:
- `users` - User profiles
- `user_settings` - User preferences
- `credit_cards` - Credit card information
- `bills` - Bill records
- `payment_history` - Payment transactions

## 🔧 Environment Variables

Required environment variables:

```env
# Supabase
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_KEY=your-service-key
SUPABASE_ANON_KEY=your-anon-key

# Method API
METHOD_API_KEY=your-method-api-key
METHOD_ENVIRONMENT=sandbox

# FastAPI
SECRET_KEY=your-secret-key
ALLOWED_ORIGINS=http://localhost:3001
ENVIRONMENT=development
```

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Test specific endpoint
curl http://localhost:8000/api/health
```

## 🚀 Deployment

### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

### Render
1. Connect GitHub repository
2. Set environment variables
3. Deploy with: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 🔗 Integration with Frontend

The frontend (Next.js) will call this API with Supabase tokens:

```typescript
// Frontend API call example
const response = await fetch('http://localhost:8000/api/cards', {
  headers: {
    'Authorization': `Bearer ${supabaseToken}`,
    'Content-Type': 'application/json'
  }
})
```

## 📈 Next Steps

1. **Complete Method API integration** - Implement real Method API calls
2. **Add email parsing** - Process bill emails with AI
3. **Implement payment processing** - Actual bill payment logic
4. **Add webhooks** - AgentMail webhook handling
5. **Add monitoring** - Logging, metrics, error tracking

