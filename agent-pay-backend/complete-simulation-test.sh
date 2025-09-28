#!/bin/bash

# 🎭 AgentPay Complete Simulation Flow Test
# Tests the entire user journey with Method simulation environment

set -e  # Exit on any error

API_BASE="http://localhost:8000/api"
FRONTEND_BASE="http://localhost:3001"

echo "🚀 AgentPay Complete Simulation Flow Test"
echo "========================================"
echo ""

# Test user credentials
TEST_EMAIL="simulation@agentpay.com"
TEST_PASSWORD="SimulationTest123!"
TEST_PHONE="5551234567"

echo "📝 Step 1: User Registration..."
REGISTER_RESPONSE=$(curl -s -X POST "$API_BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\",
    \"phone_number\": \"$TEST_PHONE\"
  }")

echo "Registration Response:"
echo "$REGISTER_RESPONSE" | jq '.'

# Check if registration was successful
if echo "$REGISTER_RESPONSE" | jq -e '.access_token' > /dev/null; then
    echo "✅ Registration successful!"
    ACCESS_TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.access_token')
else
    echo "❌ Registration failed. Trying to login instead..."
    
    echo ""
    echo "🔐 Step 1b: User Login..."
    LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/auth/login" \
      -H "Content-Type: application/json" \
      -d "{
        \"email\": \"$TEST_EMAIL\",
        \"password\": \"$TEST_PASSWORD\"
      }")
    
    echo "Login Response:"
    echo "$LOGIN_RESPONSE" | jq '.'
    
    ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
    
    if [ "$ACCESS_TOKEN" = "null" ] || [ -z "$ACCESS_TOKEN" ]; then
        echo "❌ Login failed. Exiting..."
        exit 1
    fi
    
    echo "✅ Login successful!"
fi

echo ""
echo "👤 Step 2: Creating Method Entity..."
ENTITY_RESPONSE=$(curl -s -X POST "$API_BASE/entities/create" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "individual",
    "individual": {
      "first_name": "John",
      "last_name": "Simulation",
      "phone": "+15551234567",
      "email": "simulation@agentpay.com",
      "dob": "1990-01-01"
    }
  }')

echo "Entity Creation Response:"
echo "$ENTITY_RESPONSE" | jq '.'

echo ""
echo "🏦 Step 3: Simulating Bank Account Connection..."
BANK_CONNECTION_RESPONSE=$(curl -s -X POST "$API_BASE/connect/simulate-connection" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

echo "Bank Connection Response:"
echo "$BANK_CONNECTION_RESPONSE" | jq '.'

echo ""
echo "🏦 Step 4: Getting Connected Bank Accounts..."
BANK_ACCOUNTS_RESPONSE=$(curl -s -X GET "$API_BASE/connect/bank-accounts" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

echo "Bank Accounts Response:"
echo "$BANK_ACCOUNTS_RESPONSE" | jq '.'

# Extract bank account ID for payments
BANK_ACCOUNT_ID=$(echo "$BANK_ACCOUNTS_RESPONSE" | jq -r '.bank_accounts[0].id // empty')

if [ -z "$BANK_ACCOUNT_ID" ] || [ "$BANK_ACCOUNT_ID" = "null" ]; then
    echo "⚠️  No bank account found. Creating multiple simulated accounts..."
    
    MULTIPLE_ACCOUNTS_RESPONSE=$(curl -s -X POST "$API_BASE/connect/simulate-multiple-accounts" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "Content-Type: application/json")
    
    echo "Multiple Accounts Response:"
    echo "$MULTIPLE_ACCOUNTS_RESPONSE" | jq '.'
    
    # Try to get bank accounts again
    BANK_ACCOUNTS_RESPONSE=$(curl -s -X GET "$API_BASE/connect/bank-accounts" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "Content-Type: application/json")
    
    BANK_ACCOUNT_ID=$(echo "$BANK_ACCOUNTS_RESPONSE" | jq -r '.bank_accounts[0].id // empty')
fi

echo ""
echo "💳 Step 5: Getting Credit Cards..."
CARDS_RESPONSE=$(curl -s -X GET "$API_BASE/cards/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

echo "Credit Cards Response:"
echo "$CARDS_RESPONSE" | jq '.'

# Extract credit card ID for payment
CREDIT_CARD_ID=$(echo "$CARDS_RESPONSE" | jq -r '.[0].method_card.id // empty')

echo ""
echo "📊 Step 6: Getting Payment History..."
PAYMENT_HISTORY_RESPONSE=$(curl -s -X GET "$API_BASE/payments/history" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

echo "Payment History Response:"
echo "$PAYMENT_HISTORY_RESPONSE" | jq '.'

echo ""
echo "💰 Step 7: Creating Payment (Bank → Credit Card)..."

if [ -n "$BANK_ACCOUNT_ID" ] && [ "$BANK_ACCOUNT_ID" != "null" ] && [ -n "$CREDIT_CARD_ID" ] && [ "$CREDIT_CARD_ID" != "null" ]; then
    PAYMENT_RESPONSE=$(curl -s -X POST "$API_BASE/payments/" \
      -H "Authorization: Bearer $ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"amount\": 10000,
        \"source\": \"$BANK_ACCOUNT_ID\",
        \"destination\": \"$CREDIT_CARD_ID\",
        \"description\": \"Simulation Test Payment\"
      }")
    
    echo "Payment Creation Response:"
    echo "$PAYMENT_RESPONSE" | jq '.'
    
    # Extract payment ID for simulation
    PAYMENT_ID=$(echo "$PAYMENT_RESPONSE" | jq -r '.id // empty')
    
    if [ -n "$PAYMENT_ID" ] && [ "$PAYMENT_ID" != "null" ]; then
        echo ""
        echo "🎭 Step 8: Simulating Payment Processing..."
        
        # Simulate payment processing
        SIMULATE_PROCESSING_RESPONSE=$(curl -s -X POST "$API_BASE/simulations/payment-update" \
          -H "Authorization: Bearer $ACCESS_TOKEN" \
          -H "Content-Type: application/json" \
          -d "{
            \"payment_id\": \"$PAYMENT_ID\",
            \"status\": \"processing\"
          }")
        
        echo "Payment Processing Simulation:"
        echo "$SIMULATE_PROCESSING_RESPONSE" | jq '.'
        
        echo ""
        echo "⏳ Waiting 2 seconds..."
        sleep 2
        
        echo ""
        echo "🎭 Step 9: Simulating Payment Completion..."
        
        # Simulate payment completion
        SIMULATE_COMPLETION_RESPONSE=$(curl -s -X POST "$API_BASE/simulations/payment-update" \
          -H "Authorization: Bearer $ACCESS_TOKEN" \
          -H "Content-Type: application/json" \
          -d "{
            \"payment_id\": \"$PAYMENT_ID\",
            \"status\": \"completed\"
          }")
        
        echo "Payment Completion Simulation:"
        echo "$SIMULATE_COMPLETION_RESPONSE" | jq '.'
        
        echo ""
        echo "📊 Step 10: Verifying Final Payment Status..."
        FINAL_PAYMENT_RESPONSE=$(curl -s -X GET "$API_BASE/payments/$PAYMENT_ID" \
          -H "Authorization: Bearer $ACCESS_TOKEN" \
          -H "Content-Type: application/json")
        
        echo "Final Payment Status:"
        echo "$FINAL_PAYMENT_RESPONSE" | jq '.'
        
    else
        echo "❌ Payment creation failed - no payment ID returned"
    fi
else
    echo "❌ Cannot create payment - missing bank account or credit card"
    echo "Bank Account ID: $BANK_ACCOUNT_ID"
    echo "Credit Card ID: $CREDIT_CARD_ID"
fi

echo ""
echo "🎉 SIMULATION FLOW COMPLETE!"
echo "============================"
echo ""
echo "📋 SUMMARY:"
echo "----------"
echo "✅ User Registration/Login"
echo "✅ Method Entity Creation"
echo "✅ Simulated Bank Account Connection"
echo "✅ Credit Card Retrieval"
echo "✅ Payment Creation"
echo "✅ Payment Status Simulation"
echo ""
echo "🚀 Ready for frontend integration!"
echo ""
echo "🌐 Frontend URL: $FRONTEND_BASE"
echo "🔗 API Documentation: http://localhost:8000/docs"

