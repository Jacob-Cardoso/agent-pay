// Method Connect Frontend Integration Example
// This shows how to integrate Method Connect in your React dashboard

import { useState, useEffect } from 'react';

const BankConnectionModal = ({ isOpen, onClose, onSuccess }) => {
  const [elementToken, setElementToken] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Step 1: Get element token from backend
  const createElementToken = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/connect/element-token', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userToken}`, // User's JWT token
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to create element token');
      }
      
      const data = await response.json();
      setElementToken(data.element_token);
      
      // Step 2: Initialize Method Connect
      initializeMethodConnect(data.element_token);
      
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Step 2: Initialize Method Connect component
  const initializeMethodConnect = (token) => {
    // Load Method Connect SDK
    const script = document.createElement('script');
    script.src = 'https://js.methodfi.com/connect.js';
    script.onload = () => {
      // Initialize Method Connect
      const methodConnect = new window.MethodConnect({
        token: token,
        env: 'dev', // Use 'production' for live
        
        // Styling options
        theme: {
          primaryColor: '#6366f1', // Your brand color
          borderRadius: '8px'
        },
        
        // Success callback
        onSuccess: async (account) => {
          console.log('Bank account connected:', account);
          
          // Step 3: Get account details from backend
          try {
            const response = await fetch(`/api/connect/element-results/${token}`, {
              headers: {
                'Authorization': `Bearer ${userToken}`
              }
            });
            
            const accountDetails = await response.json();
            
            // Notify parent component
            onSuccess(accountDetails);
            onClose();
            
            // Show success message
            alert('Bank account connected successfully!');
            
          } catch (err) {
            console.error('Failed to get account details:', err);
          }
        },
        
        // Error callback
        onError: (error) => {
          console.error('Method Connect error:', error);
          setError('Failed to connect bank account. Please try again.');
        },
        
        // Exit callback
        onExit: () => {
          console.log('User closed Method Connect');
          onClose();
        }
      });
      
      // Open Method Connect
      methodConnect.open();
    };
    
    document.head.appendChild(script);
  };

  useEffect(() => {
    if (isOpen && !elementToken) {
      createElementToken();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Connect Your Bank Account</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>
        
        {isLoading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">Preparing secure connection...</p>
          </div>
        )}
        
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-4">
            <p className="text-red-600">{error}</p>
            <button 
              onClick={createElementToken}
              className="mt-2 text-red-600 underline hover:no-underline"
            >
              Try Again
            </button>
          </div>
        )}
        
        {elementToken && (
          <div className="text-center py-4">
            <p className="text-gray-600">
              Method Connect will open in a new window to securely connect your bank account.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

// Usage in Dashboard Component
const Dashboard = () => {
  const [showBankConnection, setShowBankConnection] = useState(false);
  const [bankAccounts, setBankAccounts] = useState([]);
  const [creditCards, setCreditCards] = useState([]);

  // Load user's connected accounts
  const loadAccounts = async () => {
    try {
      // Get bank accounts
      const bankResponse = await fetch('/api/connect/bank-accounts', {
        headers: { 'Authorization': `Bearer ${userToken}` }
      });
      const bankData = await bankResponse.json();
      setBankAccounts(bankData.bank_accounts);
      
      // Get credit cards
      const cardResponse = await fetch('/api/cards/', {
        headers: { 'Authorization': `Bearer ${userToken}` }
      });
      const cardData = await cardResponse.json();
      setCreditCards(cardData);
      
    } catch (err) {
      console.error('Failed to load accounts:', err);
    }
  };

  // Handle successful bank connection
  const handleBankConnectionSuccess = (accountDetails) => {
    console.log('New bank account connected:', accountDetails);
    loadAccounts(); // Refresh accounts list
  };

  // Make a payment
  const makePayment = async (creditCardId, amount) => {
    if (bankAccounts.length === 0) {
      setShowBankConnection(true);
      return;
    }

    try {
      const response = await fetch('/api/payments/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          amount: amount * 100, // Convert to cents
          source: bankAccounts[0].id, // Use first bank account
          destination: creditCardId,
          description: 'Credit Card Payment'
        })
      });

      const payment = await response.json();
      console.log('Payment created:', payment);
      
      // Show success message and refresh data
      alert('Payment initiated successfully!');
      loadAccounts();
      
    } catch (err) {
      console.error('Payment failed:', err);
      alert('Payment failed. Please try again.');
    }
  };

  useEffect(() => {
    loadAccounts();
  }, []);

  return (
    <div className="dashboard">
      {/* Bank Accounts Section */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Bank Accounts</h2>
          <button 
            onClick={() => setShowBankConnection(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            + Connect Bank Account
          </button>
        </div>
        
        {bankAccounts.length === 0 ? (
          <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <p className="text-gray-600 mb-4">No bank accounts connected</p>
            <button 
              onClick={() => setShowBankConnection(true)}
              className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700"
            >
              Connect Your First Bank Account
            </button>
          </div>
        ) : (
          <div className="grid gap-4">
            {bankAccounts.map(account => (
              <div key={account.id} className="bg-white border rounded-lg p-4">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-medium">{account.bank_name}</h3>
                    <p className="text-gray-600">{account.type} ****{account.last_four}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-sm ${
                    account.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {account.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Credit Cards Section */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Credit Cards</h2>
        <div className="grid gap-4">
          {creditCards.map(card => (
            <div key={card.method_card.id} className="bg-white border rounded-lg p-4">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-medium">{card.method_card.brand} ****{card.method_card.last_four}</h3>
                  <p className="text-gray-600">Balance: ${(card.method_card.balance / 100).toFixed(2)}</p>
                </div>
                <button 
                  onClick={() => makePayment(card.method_card.id, 100)} // Pay $100
                  className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
                  disabled={bankAccounts.length === 0}
                >
                  {bankAccounts.length === 0 ? 'Connect Bank First' : 'Pay $100'}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Method Connect Modal */}
      <BankConnectionModal
        isOpen={showBankConnection}
        onClose={() => setShowBankConnection(false)}
        onSuccess={handleBankConnectionSuccess}
      />
    </div>
  );
};

export default Dashboard;

