#!/usr/bin/env python3
"""
AgentPay Database Setup Script
Automatically sets up the Supabase database schema
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('agent-pay-backend/.env')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Missing SUPABASE_URL or SUPABASE_KEY in environment")
    exit(1)

# Database schema SQL
SCHEMA_SQL = """
-- AgentPay Database Schema (Simplified for Method API Integration)

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  phone_number TEXT,
  method_account_id TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Card Preferences table (user preferences for Method API cards)
CREATE TABLE IF NOT EXISTS public.card_preferences (
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
CREATE TABLE IF NOT EXISTS public.user_settings (
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

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own profile" ON public.users;
DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
DROP POLICY IF EXISTS "Users can insert own profile" ON public.users;
DROP POLICY IF EXISTS "Users can view own card preferences" ON public.card_preferences;
DROP POLICY IF EXISTS "Users can insert own card preferences" ON public.card_preferences;
DROP POLICY IF EXISTS "Users can update own card preferences" ON public.card_preferences;
DROP POLICY IF EXISTS "Users can view own settings" ON public.user_settings;
DROP POLICY IF EXISTS "Users can update own settings" ON public.user_settings;
DROP POLICY IF EXISTS "Users can insert own settings" ON public.user_settings;

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
  INSERT INTO public.users (id, email, full_name, phone_number)
  VALUES (
    NEW.id, 
    NEW.email, 
    NEW.raw_user_meta_data->>'full_name',
    NEW.raw_user_meta_data->>'phone_number'
  );
  
  INSERT INTO public.user_settings (user_id)
  VALUES (NEW.id);
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop existing trigger if it exists
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Trigger for new user creation
CREATE TRIGGER on_auth_user_created
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

-- Drop existing triggers if they exist
DROP TRIGGER IF EXISTS update_users_updated_at ON public.users;
DROP TRIGGER IF EXISTS update_card_preferences_updated_at ON public.card_preferences;
DROP TRIGGER IF EXISTS update_user_settings_updated_at ON public.user_settings;

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
"""

def setup_database():
    """Set up the database schema using Supabase REST API"""
    
    print("🚀 Setting up AgentPay database schema...")
    print(f"📍 Supabase URL: {SUPABASE_URL}")
    
    # Use the Supabase REST API to execute SQL
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # Split SQL into individual statements and execute them
    statements = [stmt.strip() for stmt in SCHEMA_SQL.split(';') if stmt.strip()]
    
    success_count = 0
    error_count = 0
    
    for i, statement in enumerate(statements):
        if not statement:
            continue
            
        try:
            # For CREATE statements, use a different approach
            if statement.upper().startswith(('CREATE', 'ALTER', 'DROP', 'INSERT')):
                # Use the SQL editor endpoint
                sql_url = f"{SUPABASE_URL}/rest/v1/"
                response = requests.post(
                    sql_url,
                    headers=headers,
                    json={'query': statement},
                    timeout=30
                )
            else:
                # Use RPC for other statements
                response = requests.post(
                    url,
                    headers=headers,
                    json={'sql': statement},
                    timeout=30
                )
            
            if response.status_code in [200, 201, 204]:
                success_count += 1
                print(f"✅ Statement {i+1}: Success")
            else:
                error_count += 1
                print(f"❌ Statement {i+1}: Error {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            error_count += 1
            print(f"❌ Statement {i+1}: Exception - {str(e)[:100]}")
    
    print(f"\n📊 Setup Summary:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ❌ Errors: {error_count}")
    
    if error_count == 0:
        print("\n🎉 Database schema setup completed successfully!")
        print("\n📋 Created tables:")
        print("   • users - User profiles and Method account IDs")
        print("   • card_preferences - User preferences for each credit card")
        print("   • user_settings - Global user settings")
        print("\n🔧 Created functions and triggers:")
        print("   • handle_new_user() - Auto-creates user profile on signup")
        print("   • update_updated_at_column() - Auto-updates timestamps")
        print("\n🛡️ Enabled Row Level Security (RLS) policies")
        
        # Test the setup
        test_database()
    else:
        print(f"\n⚠️  Setup completed with {error_count} errors.")
        print("   Some features may not work correctly.")
        print("   Check the Supabase dashboard for details.")

def test_database():
    """Test if the database setup was successful"""
    print("\n🧪 Testing database connection...")
    
    # Test users table
    url = f"{SUPABASE_URL}/rest/v1/users?select=count"
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ Users table: Accessible")
        else:
            print(f"❌ Users table: Error {response.status_code}")
    except Exception as e:
        print(f"❌ Users table: Connection failed - {str(e)[:50]}")
    
    # Test backend health
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            if health_data.get('status') == 'healthy':
                print("✅ Backend health: Healthy")
            else:
                print(f"⚠️  Backend health: {health_data.get('status', 'Unknown')}")
        else:
            print(f"❌ Backend health: Error {response.status_code}")
    except Exception as e:
        print(f"❌ Backend health: Connection failed - {str(e)[:50]}")

if __name__ == "__main__":
    setup_database()

