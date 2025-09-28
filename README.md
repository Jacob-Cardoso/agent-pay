# 🚀 AgentPay

A modern payment management platform built with Next.js and FastAPI, featuring Method Financial API integration for seamless credit card and payment processing.

## 📋 Project Structure

```
AgentPay/
├── agent-pay-fe/          # Next.js Frontend (Separate GitHub repo)
├── agent-pay-backend/     # FastAPI Backend
├── setup-database.py     # Database setup script
├── SETUP_GUIDE.md        # Complete setup instructions
└── README.md             # This file
```

## 🔗 Repositories

- **Frontend**: [agent-pay-fe](https://github.com/Jacob-Cardoso/agent-pay-fe) - Next.js application
- **Backend**: Located in `agent-pay-backend/` folder

## ✨ Features

### 💳 Credit Card Management
- Display credit card balances and details
- View payment due dates and minimum amounts
- Beautiful card visualizations with brand-specific styling

### 💰 Payment Processing
- One-click payments from credit cards
- Real-time payment status tracking
- Payment history with detailed transaction records

### 📊 Dashboard Analytics
- Payment statistics and summaries
- Transaction history filtering and sorting
- Responsive design for all devices

### 🔐 Authentication
- Secure JWT-based authentication
- Supabase integration for user management
- Method Financial API for banking data

## 🛠️ Tech Stack

### Frontend (Next.js)
- **Framework**: Next.js 14 with App Router
- **UI**: Tailwind CSS + shadcn/ui components
- **Auth**: NextAuth.js + Supabase
- **State**: React hooks and context

### Backend (FastAPI)
- **Framework**: FastAPI with async support
- **Database**: Supabase (PostgreSQL)
- **Auth**: JWT tokens with bcrypt
- **API Integration**: Method Financial API

### External Services
- **Banking**: Method Financial API
- **Database**: Supabase
- **Hosting**: Ready for Vercel (frontend) + Railway/Heroku (backend)

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.8+
- Method Financial API key
- Supabase account

### Setup Instructions
1. **Clone the repository**
   ```bash
   git clone <this-repo-url>
   cd AgentPay
   ```

2. **Set up the backend**
   ```bash
   cd agent-pay-backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**
   ```bash
   # The frontend is in a separate repository
   git clone https://github.com/Jacob-Cardoso/agent-pay-fe.git
   cd agent-pay-fe
   npm install
   ```

4. **Configure environment variables**
   - Copy `env.template` files in both directories
   - Add your Method API key, Supabase credentials

5. **Run the applications**
   ```bash
   # Backend (Terminal 1)
   cd agent-pay-backend
   source venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000

   # Frontend (Terminal 2)
   cd agent-pay-fe
   npm run dev
   ```

6. **Open your browser**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000

## 🧪 Test Account

For testing the application:
- **Email**: `methoduser@example.com`
- **Password**: `testpass123`

## 📚 Documentation

- [`SETUP_GUIDE.md`](./SETUP_GUIDE.md) - Detailed setup instructions
- [`setup-database.md`](./setup-database.md) - Database schema and setup
- [Frontend README](https://github.com/Jacob-Cardoso/agent-pay-fe) - Frontend-specific docs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔧 Development Status

✅ **Completed Features:**
- Credit card display and management
- Payment processing with Method API
- Payment history and statistics
- JWT authentication
- Responsive UI design

🚧 **In Progress:**
- Bank account integration
- Automated payment scheduling
- Advanced analytics dashboard

📋 **Planned Features:**
- Bill pay integration
- Mobile app (React Native)
- Advanced fraud detection
- Multi-user account management
