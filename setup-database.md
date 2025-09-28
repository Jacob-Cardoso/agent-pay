# 🗄️ Database Setup Instructions

## Step 1: Open Supabase SQL Editor

1. Go to [supabase.com](https://supabase.com) and sign in
2. Open your **Agent-Pay** project
3. Navigate to **SQL Editor** in the left sidebar
4. Click **New Query**

## Step 2: Run Database Schema

Copy and paste the following SQL into the editor and click **Run**:

```sql
-- AgentPay Database Schema (Simplified for Method API Integration)

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (extends Supabase auth.users)
CREATE TABLE public.users (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  phone_number TEXT,
  method_entity_id TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Card Preferences table (user preferences for Method API cards)
CREATE TABLE public.card_preferences (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL,
  method_card_id TEXT NOT NULL, -- Method API card ID
  autopay_enabled BOOLEAN DEFAULT FALSE,
  reminder_days INTEGER DEFAULT 3, -- days before due date to send reminder
  max_autopay_amount DECIMAL(10,2) DEFAULT 1000.00,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  UNIQUE(user_id, method_card_id)
);

-- User Settings table
CREATE TABLE public.user_settings (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE NOT NULL UNIQUE,
  autopay_enabled BOOLEAN DEFAULT TRUE,
  default_reminder_days INTEGER DEFAULT 3,
  email_notifications BOOLEAN DEFAULT TRUE,
  sms_notifications BOOLEAN DEFAULT FALSE,
  max_autopay_amount DECIMAL(10,2) DEFAULT 1000.00,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security (RLS)
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.card_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_settings ENABLE ROW LEVEL SECURITY;

-- RLS Policies

-- Users can only see/edit their own data
CREATE POLICY "Users can view own profile" ON public.users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.users
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON public.users
  FOR INSERT WITH CHECK (auth.uid() = id);

-- Card preferences policies
CREATE POLICY "Users can view own card preferences" ON public.card_preferences
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own card preferences" ON public.card_preferences
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own card preferences" ON public.card_preferences
  FOR UPDATE USING (auth.uid() = user_id);

-- User settings policies
CREATE POLICY "Users can view own settings" ON public.user_settings
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own settings" ON public.user_settings
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own settings" ON public.user_settings
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Functions

-- Function to handle new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, full_name)
  VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
  
  INSERT INTO public.user_settings (user_id)
  VALUES (NEW.id);
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for new user creation
CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_users_updated_at
  BEFORE UPDATE ON public.users
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_card_preferences_updated_at
  BEFORE UPDATE ON public.card_preferences
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_user_settings_updated_at
  BEFORE UPDATE ON public.user_settings
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
```

## Step 3: Verify Tables

After running the SQL, you should see these tables in your **Database** → **Tables** section:

- ✅ `users` - User profiles and Method account IDs
- ✅ `card_preferences` - User preferences for each credit card  
- ✅ `user_settings` - Global user settings

## Step 4: Test Database Connection

Your database is now ready! The FastAPI backend will:
- ✅ Store user profiles and preferences in Supabase
- ✅ Query Method API for live credit card data
- ✅ Query Method API for payment history
- ✅ Automatically create user records when someone signs up

## What's Stored vs. What's Queried

### 📊 **Stored in Supabase:**
- User profiles (email, name, phone)
- Method account IDs (linking users to Method)
- Card preferences (autopay settings, reminder days)
- User settings (notification preferences)

### 🔄 **Queried from Method API:**
- Credit card details (balance, brand, last 4 digits)
- Payment history and transactions
- Bill statements and due dates
- Account balances and status

This gives you the best of both worlds: fast user preferences and always up-to-date financial data!
