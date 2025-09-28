#!/bin/bash

# 🎭 Working AgentPay Simulation Test
# Tests the bank account simulation functionality

set -e  # Exit on any error

API_BASE="http://localhost:8000/api"

echo "🎭 AgentPay Bank Account Simulation Test"
echo "========================================"
echo ""

# Generate unique test email
TIMESTAMP=$(date +%s)
TEST_EMAIL="test${TIMESTAMP}@agentpay.com"
TEST_PASSWORD="Test123!"
TEST_PHONE="555${TIMESTAMP: -7}"

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

ACCESS_TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.access_token')

if [ "$ACCESS_TOKEN" = "null" ] || [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ Registration failed. Exiting..."
    exit 1
fi

echo "✅ Registration successful!"
echo "User ID: $(echo "$REGISTER_RESPONSE" | jq -r '.user.id')"
echo "Access Token: ${ACCESS_TOKEN:0:20}..."

echo ""
echo "🏦 Step 2: Simulating Bank Account Connection..."
BANK_CONNECTION_RESPONSE=$(curl -s -X POST "$API_BASE/connect/simulate-connection" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

echo "Bank Connection Response:"
echo "$BANK_CONNECTION_RESPONSE" | jq '.'

# Check if simulation was successful
if echo "$BANK_CONNECTION_RESPONSE" | jq -e '.success' > /dev/null; then
    echo "✅ Bank account simulation successful!"
    
    ENTITY_ID=$(echo "$BANK_CONNECTION_RESPONSE" | jq -r '.entity_id')
    ACCOUNT_ID=$(echo "$BANK_CONNECTION_RESPONSE" | jq -r '.account.id')
    
    echo "Entity ID: $ENTITY_ID"
    echo "Account ID: $ACCOUNT_ID"
else
    echo "❌ Bank account simulation failed"
    exit 1
fi

echo ""
echo "📋 Step 3: Getting Connected Bank Accounts..."
BANK_ACCOUNTS_RESPONSE=$(curl -s -X GET "$API_BASE/connect/bank-accounts" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

echo "Bank Accounts Response:"
echo "$BANK_ACCOUNTS_RESPONSE" | jq '.'

# Extract bank account details
BANK_ACCOUNT_COUNT=$(echo "$BANK_ACCOUNTS_RESPONSE" | jq '.total // 0')
echo "Total Bank Accounts: $BANK_ACCOUNT_COUNT"

if [ "$BANK_ACCOUNT_COUNT" -gt 0 ]; then
    echo "✅ Bank accounts retrieved successfully!"
    
    echo ""
    echo "📊 Bank Account Details:"
    echo "$BANK_ACCOUNTS_RESPONSE" | jq '.bank_accounts[0] | {
        id: .id,
        bank_name: .bank_name,
        type: .type,
        last_four: .last_four,
        status: .status,
        balance: (.balance / 100 | tostring + " USD"),
        routing_number: .routing_number
    }'
else
    echo "❌ No bank accounts found"
    exit 1
fi

echo ""
echo "🎭 Step 4: Creating Multiple Simulated Accounts..."
MULTIPLE_ACCOUNTS_RESPONSE=$(curl -s -X POST "$API_BASE/connect/simulate-multiple-accounts" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

echo "Multiple Accounts Response:"
echo "$MULTIPLE_ACCOUNTS_RESPONSE" | jq '.'

echo ""
echo "📋 Step 5: Getting All Bank Accounts (After Multiple Creation)..."
FINAL_ACCOUNTS_RESPONSE=$(curl -s -X GET "$API_BASE/connect/bank-accounts" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json")

FINAL_ACCOUNT_COUNT=$(echo "$FINAL_ACCOUNTS_RESPONSE" | jq '.total // 0')
echo "Final Total Bank Accounts: $FINAL_ACCOUNT_COUNT"

echo ""
echo "📊 All Bank Accounts:"
echo "$FINAL_ACCOUNTS_RESPONSE" | jq '.bank_accounts[] | {
    id: .id,
    bank_name: .bank_name,
    type: .type,
    status: .status,
    balance: (.balance / 100 | tostring + " USD")
}'

echo ""
echo "🎉 SIMULATION TEST COMPLETE!"
echo "============================"
echo ""
echo "📋 SUMMARY:"
echo "----------"
echo "✅ User Registration: $TEST_EMAIL"
echo "✅ Bank Account Simulation: $BANK_ACCOUNT_COUNT initial account(s)"
echo "✅ Multiple Account Creation: $FINAL_ACCOUNT_COUNT total account(s)"
echo "✅ Account Retrieval: Working"
echo ""
echo "🎭 All simulated accounts are stored in memory and can be used for payments!"
echo ""
echo "🌐 Next Steps:"
echo "- Integrate with frontend dashboard"
echo "- Test payment creation using simulated accounts"
echo "- Add credit card simulation for complete flow"

