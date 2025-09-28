import os
import httpx
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

# In-memory storage for simulated accounts (for dev environment only)
_simulated_accounts = {}

class MethodAPIService:
    """Service to interact with Method Financial API"""
    
    def __init__(self):
        self.api_key = os.getenv("METHOD_API_KEY")
        self.environment = os.getenv("METHOD_ENVIRONMENT", "dev")
        
        # Set base URL based on environment (using correct Method API URLs)
        if self.environment == "dev":
            self.base_url = "https://dev.methodfi.com"
        elif self.environment == "sandbox":
            self.base_url = "https://sandbox.methodfi.com"
        else:  # production
            self.base_url = "https://production.methodfi.com"
        
        if not self.api_key:
            raise ValueError("METHOD_API_KEY is required")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Method API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Method-Version": "2025-07-04"  # Required by Method API
        }
    
    async def create_entity(self, email: str, full_name: str, phone: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new entity (user) in Method
        
        Args:
            email: User's email address
            full_name: User's full name
            phone: User's phone number (optional)
            
        Returns:
            Method entity object
        """
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "type": "individual",
                    "individual": {
                        "first_name": full_name.split()[0] if full_name else "Unknown",
                        "last_name": " ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else "User",
                        "email": email,
                        "phone": phone
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/entities",
                    json=payload,
                    headers=self._get_headers()
                )
                
                if response.status_code == 201:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Method API error: {response.text}"
                    )
                    
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Method API: {str(e)}")
    
    async def simulate_credit_card_connection(self, entity_id: str, card_brand: str = "visa") -> Dict[str, Any]:
        """
        Simulate connecting a credit card (dev environment only)
        
        This bypasses Method Connect and creates a simulated credit card
        that can be used for payments in the dev environment.
        
        Args:
            entity_id: Method entity ID
            card_brand: Brand of credit card (visa, mastercard, amex, discover)
            
        Returns:
            Simulated credit card data
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            import uuid
            import random
            from datetime import datetime, timedelta
            
            account_id = f"acc_cc_{str(uuid.uuid4())[:8]}"
            
            # Define card brand specifics
            brand_configs = {
                "visa": {
                    "brand": "visa",
                    "name": "Chase Sapphire Preferred",
                    "last_four": "4242",
                    "color": "blue"
                },
                "mastercard": {
                    "brand": "mastercard", 
                    "name": "Capital One Venture",
                    "last_four": "5555",
                    "color": "red"
                },
                "amex": {
                    "brand": "amex",
                    "name": "American Express Gold",
                    "last_four": "1005",
                    "color": "green"
                },
                "discover": {
                    "brand": "discover",
                    "name": "Discover it Cash Back",
                    "last_four": "1117",
                    "color": "orange"
                }
            }
            
            config = brand_configs.get(card_brand, brand_configs["visa"])
            
            # Generate realistic credit card data
            balance = random.randint(50000, 500000)  # $500 - $5000 in cents
            credit_limit = balance + random.randint(100000, 1000000)  # Additional available credit
            minimum_payment = max(2500, int(balance * 0.02))  # At least $25 or 2% of balance
            
            # Generate due date (15-45 days from now)
            due_date = datetime.now() + timedelta(days=random.randint(15, 45))
            last_payment_date = datetime.now() - timedelta(days=random.randint(5, 30))
            
            simulated_credit_card = {
                "id": account_id,
                "entity_id": entity_id,
                "type": "liability",
                "brand": config["brand"],
                "last_four": config["last_four"],
                "name": config["name"],
                "status": "active",
                "balance": balance,
                "exp_month": random.randint(1, 12),
                "exp_year": datetime.now().year + random.randint(1, 5),
                "liability": {
                    "mch": config["last_four"],
                    "mask": config["last_four"],
                    "name": config["name"],
                    "type": "credit_card",
                    "balance": balance,
                    "credit_limit": credit_limit,
                    "available_credit": credit_limit - balance,
                    "last_payment_date": last_payment_date.isoformat(),
                    "last_payment_amount": random.randint(5000, minimum_payment),
                    "next_payment_due_date": due_date.isoformat(),
                    "next_payment_minimum_amount": minimum_payment,
                    "apr": round(random.uniform(15.99, 29.99), 2),
                    "statement_balance": balance
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": datetime.now().isoformat()
            }
            
            # Add simulation metadata
            simulated_credit_card["_simulation"] = True
            simulated_credit_card["_simulation_note"] = f"This is a simulated {config['brand']} credit card for development testing"
            
            # Store in simulated accounts for retrieval
            if entity_id not in _simulated_accounts:
                _simulated_accounts[entity_id] = []
            _simulated_accounts[entity_id].append(simulated_credit_card)
            
            return simulated_credit_card
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate credit card connection: {str(e)}")
    
    async def simulate_multiple_credit_cards(self, entity_id: str) -> Dict[str, Any]:
        """
        Simulate connecting multiple credit cards for comprehensive testing
        
        Args:
            entity_id: Method entity ID
            
        Returns:
            List of simulated credit cards
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            cards = []
            brands = ["visa", "mastercard", "amex", "discover"]
            
            # Create 2-3 credit cards with different brands
            for brand in brands[:3]:  # Create 3 cards
                credit_card = await self.simulate_credit_card_connection(entity_id, brand)
                cards.append(credit_card)
            
            return {
                "cards": cards,
                "total": len(cards),
                "_simulation": True,
                "_simulation_note": "These are simulated credit cards for development testing"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate multiple credit cards: {str(e)}")
    
    async def get_entity(self, entity_id: str) -> Dict[str, Any]:
        """
        Get an entity by ID
        
        Args:
            entity_id: Method entity ID
            
        Returns:
            Method entity object
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/entities/{entity_id}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Method API error: {response.text}"
                    )
                    
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Method API: {str(e)}")
    
    async def simulate_credit_card_connection(self, entity_id: str, card_brand: str = "visa") -> Dict[str, Any]:
        """
        Simulate connecting a credit card (dev environment only)
        
        This bypasses Method Connect and creates a simulated credit card
        that can be used for payments in the dev environment.
        
        Args:
            entity_id: Method entity ID
            card_brand: Brand of credit card (visa, mastercard, amex, discover)
            
        Returns:
            Simulated credit card data
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            import uuid
            import random
            from datetime import datetime, timedelta
            
            account_id = f"acc_cc_{str(uuid.uuid4())[:8]}"
            
            # Define card brand specifics
            brand_configs = {
                "visa": {
                    "brand": "visa",
                    "name": "Chase Sapphire Preferred",
                    "last_four": "4242",
                    "color": "blue"
                },
                "mastercard": {
                    "brand": "mastercard", 
                    "name": "Capital One Venture",
                    "last_four": "5555",
                    "color": "red"
                },
                "amex": {
                    "brand": "amex",
                    "name": "American Express Gold",
                    "last_four": "1005",
                    "color": "green"
                },
                "discover": {
                    "brand": "discover",
                    "name": "Discover it Cash Back",
                    "last_four": "1117",
                    "color": "orange"
                }
            }
            
            config = brand_configs.get(card_brand, brand_configs["visa"])
            
            # Generate realistic credit card data
            balance = random.randint(50000, 500000)  # $500 - $5000 in cents
            credit_limit = balance + random.randint(100000, 1000000)  # Additional available credit
            minimum_payment = max(2500, int(balance * 0.02))  # At least $25 or 2% of balance
            
            # Generate due date (15-45 days from now)
            due_date = datetime.now() + timedelta(days=random.randint(15, 45))
            last_payment_date = datetime.now() - timedelta(days=random.randint(5, 30))
            
            simulated_credit_card = {
                "id": account_id,
                "entity_id": entity_id,
                "type": "liability",
                "brand": config["brand"],
                "last_four": config["last_four"],
                "name": config["name"],
                "status": "active",
                "balance": balance,
                "exp_month": random.randint(1, 12),
                "exp_year": datetime.now().year + random.randint(1, 5),
                "liability": {
                    "mch": config["last_four"],
                    "mask": config["last_four"],
                    "name": config["name"],
                    "type": "credit_card",
                    "balance": balance,
                    "credit_limit": credit_limit,
                    "available_credit": credit_limit - balance,
                    "last_payment_date": last_payment_date.isoformat(),
                    "last_payment_amount": random.randint(5000, minimum_payment),
                    "next_payment_due_date": due_date.isoformat(),
                    "next_payment_minimum_amount": minimum_payment,
                    "apr": round(random.uniform(15.99, 29.99), 2),
                    "statement_balance": balance
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": datetime.now().isoformat()
            }
            
            # Add simulation metadata
            simulated_credit_card["_simulation"] = True
            simulated_credit_card["_simulation_note"] = f"This is a simulated {config['brand']} credit card for development testing"
            
            # Store in simulated accounts for retrieval
            if entity_id not in _simulated_accounts:
                _simulated_accounts[entity_id] = []
            _simulated_accounts[entity_id].append(simulated_credit_card)
            
            return simulated_credit_card
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate credit card connection: {str(e)}")
    
    async def simulate_multiple_credit_cards(self, entity_id: str) -> Dict[str, Any]:
        """
        Simulate connecting multiple credit cards for comprehensive testing
        
        Args:
            entity_id: Method entity ID
            
        Returns:
            List of simulated credit cards
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            cards = []
            brands = ["visa", "mastercard", "amex", "discover"]
            
            # Create 2-3 credit cards with different brands
            for brand in brands[:3]:  # Create 3 cards
                credit_card = await self.simulate_credit_card_connection(entity_id, brand)
                cards.append(credit_card)
            
            return {
                "cards": cards,
                "total": len(cards),
                "_simulation": True,
                "_simulation_note": "These are simulated credit cards for development testing"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate multiple credit cards: {str(e)}")
    
    async def update_entity(self, entity_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an entity
        
        Args:
            entity_id: Method entity ID
            update_data: Data to update
            
        Returns:
            Updated Method entity object
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.base_url}/entities/{entity_id}",
                    json=update_data,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Method API error: {response.text}"
                    )
                    
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Method API: {str(e)}")
    
    async def simulate_credit_card_connection(self, entity_id: str, card_brand: str = "visa") -> Dict[str, Any]:
        """
        Simulate connecting a credit card (dev environment only)
        
        This bypasses Method Connect and creates a simulated credit card
        that can be used for payments in the dev environment.
        
        Args:
            entity_id: Method entity ID
            card_brand: Brand of credit card (visa, mastercard, amex, discover)
            
        Returns:
            Simulated credit card data
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            import uuid
            import random
            from datetime import datetime, timedelta
            
            account_id = f"acc_cc_{str(uuid.uuid4())[:8]}"
            
            # Define card brand specifics
            brand_configs = {
                "visa": {
                    "brand": "visa",
                    "name": "Chase Sapphire Preferred",
                    "last_four": "4242",
                    "color": "blue"
                },
                "mastercard": {
                    "brand": "mastercard", 
                    "name": "Capital One Venture",
                    "last_four": "5555",
                    "color": "red"
                },
                "amex": {
                    "brand": "amex",
                    "name": "American Express Gold",
                    "last_four": "1005",
                    "color": "green"
                },
                "discover": {
                    "brand": "discover",
                    "name": "Discover it Cash Back",
                    "last_four": "1117",
                    "color": "orange"
                }
            }
            
            config = brand_configs.get(card_brand, brand_configs["visa"])
            
            # Generate realistic credit card data
            balance = random.randint(50000, 500000)  # $500 - $5000 in cents
            credit_limit = balance + random.randint(100000, 1000000)  # Additional available credit
            minimum_payment = max(2500, int(balance * 0.02))  # At least $25 or 2% of balance
            
            # Generate due date (15-45 days from now)
            due_date = datetime.now() + timedelta(days=random.randint(15, 45))
            last_payment_date = datetime.now() - timedelta(days=random.randint(5, 30))
            
            simulated_credit_card = {
                "id": account_id,
                "entity_id": entity_id,
                "type": "liability",
                "brand": config["brand"],
                "last_four": config["last_four"],
                "name": config["name"],
                "status": "active",
                "balance": balance,
                "exp_month": random.randint(1, 12),
                "exp_year": datetime.now().year + random.randint(1, 5),
                "liability": {
                    "mch": config["last_four"],
                    "mask": config["last_four"],
                    "name": config["name"],
                    "type": "credit_card",
                    "balance": balance,
                    "credit_limit": credit_limit,
                    "available_credit": credit_limit - balance,
                    "last_payment_date": last_payment_date.isoformat(),
                    "last_payment_amount": random.randint(5000, minimum_payment),
                    "next_payment_due_date": due_date.isoformat(),
                    "next_payment_minimum_amount": minimum_payment,
                    "apr": round(random.uniform(15.99, 29.99), 2),
                    "statement_balance": balance
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": datetime.now().isoformat()
            }
            
            # Add simulation metadata
            simulated_credit_card["_simulation"] = True
            simulated_credit_card["_simulation_note"] = f"This is a simulated {config['brand']} credit card for development testing"
            
            # Store in simulated accounts for retrieval
            if entity_id not in _simulated_accounts:
                _simulated_accounts[entity_id] = []
            _simulated_accounts[entity_id].append(simulated_credit_card)
            
            return simulated_credit_card
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate credit card connection: {str(e)}")
    
    async def simulate_multiple_credit_cards(self, entity_id: str) -> Dict[str, Any]:
        """
        Simulate connecting multiple credit cards for comprehensive testing
        
        Args:
            entity_id: Method entity ID
            
        Returns:
            List of simulated credit cards
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            cards = []
            brands = ["visa", "mastercard", "amex", "discover"]
            
            # Create 2-3 credit cards with different brands
            for brand in brands[:3]:  # Create 3 cards
                credit_card = await self.simulate_credit_card_connection(entity_id, brand)
                cards.append(credit_card)
            
            return {
                "cards": cards,
                "total": len(cards),
                "_simulation": True,
                "_simulation_note": "These are simulated credit cards for development testing"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate multiple credit cards: {str(e)}")
    
    async def list_entities(self, page: int = 1, page_limit: int = 100) -> Dict[str, Any]:
        """
        List all entities
        
        Args:
            page: Page number
            page_limit: Number of entities per page
            
        Returns:
            List of Method entity objects
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/entities",
                    params={"page": page, "page_limit": page_limit},
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Method API error: {response.text}"
                    )
                    
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Method API: {str(e)}")
    
    async def simulate_credit_card_connection(self, entity_id: str, card_brand: str = "visa") -> Dict[str, Any]:
        """
        Simulate connecting a credit card (dev environment only)
        
        This bypasses Method Connect and creates a simulated credit card
        that can be used for payments in the dev environment.
        
        Args:
            entity_id: Method entity ID
            card_brand: Brand of credit card (visa, mastercard, amex, discover)
            
        Returns:
            Simulated credit card data
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            import uuid
            import random
            from datetime import datetime, timedelta
            
            account_id = f"acc_cc_{str(uuid.uuid4())[:8]}"
            
            # Define card brand specifics
            brand_configs = {
                "visa": {
                    "brand": "visa",
                    "name": "Chase Sapphire Preferred",
                    "last_four": "4242",
                    "color": "blue"
                },
                "mastercard": {
                    "brand": "mastercard", 
                    "name": "Capital One Venture",
                    "last_four": "5555",
                    "color": "red"
                },
                "amex": {
                    "brand": "amex",
                    "name": "American Express Gold",
                    "last_four": "1005",
                    "color": "green"
                },
                "discover": {
                    "brand": "discover",
                    "name": "Discover it Cash Back",
                    "last_four": "1117",
                    "color": "orange"
                }
            }
            
            config = brand_configs.get(card_brand, brand_configs["visa"])
            
            # Generate realistic credit card data
            balance = random.randint(50000, 500000)  # $500 - $5000 in cents
            credit_limit = balance + random.randint(100000, 1000000)  # Additional available credit
            minimum_payment = max(2500, int(balance * 0.02))  # At least $25 or 2% of balance
            
            # Generate due date (15-45 days from now)
            due_date = datetime.now() + timedelta(days=random.randint(15, 45))
            last_payment_date = datetime.now() - timedelta(days=random.randint(5, 30))
            
            simulated_credit_card = {
                "id": account_id,
                "entity_id": entity_id,
                "type": "liability",
                "brand": config["brand"],
                "last_four": config["last_four"],
                "name": config["name"],
                "status": "active",
                "balance": balance,
                "exp_month": random.randint(1, 12),
                "exp_year": datetime.now().year + random.randint(1, 5),
                "liability": {
                    "mch": config["last_four"],
                    "mask": config["last_four"],
                    "name": config["name"],
                    "type": "credit_card",
                    "balance": balance,
                    "credit_limit": credit_limit,
                    "available_credit": credit_limit - balance,
                    "last_payment_date": last_payment_date.isoformat(),
                    "last_payment_amount": random.randint(5000, minimum_payment),
                    "next_payment_due_date": due_date.isoformat(),
                    "next_payment_minimum_amount": minimum_payment,
                    "apr": round(random.uniform(15.99, 29.99), 2),
                    "statement_balance": balance
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": datetime.now().isoformat()
            }
            
            # Add simulation metadata
            simulated_credit_card["_simulation"] = True
            simulated_credit_card["_simulation_note"] = f"This is a simulated {config['brand']} credit card for development testing"
            
            # Store in simulated accounts for retrieval
            if entity_id not in _simulated_accounts:
                _simulated_accounts[entity_id] = []
            _simulated_accounts[entity_id].append(simulated_credit_card)
            
            return simulated_credit_card
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate credit card connection: {str(e)}")
    
    async def simulate_multiple_credit_cards(self, entity_id: str) -> Dict[str, Any]:
        """
        Simulate connecting multiple credit cards for comprehensive testing
        
        Args:
            entity_id: Method entity ID
            
        Returns:
            List of simulated credit cards
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            cards = []
            brands = ["visa", "mastercard", "amex", "discover"]
            
            # Create 2-3 credit cards with different brands
            for brand in brands[:3]:  # Create 3 cards
                credit_card = await self.simulate_credit_card_connection(entity_id, brand)
                cards.append(credit_card)
            
            return {
                "cards": cards,
                "total": len(cards),
                "_simulation": True,
                "_simulation_note": "These are simulated credit cards for development testing"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate multiple credit cards: {str(e)}")
    
    async def get_accounts(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get all accounts (credit cards, bank accounts) for an entity
        
        Args:
            entity_id: Method entity ID
            
        Returns:
            List of Method account objects
        """
        try:
            # In dev environment, return simulated accounts if they exist
            if self.environment == "dev" and entity_id in _simulated_accounts:
                simulated_data = _simulated_accounts[entity_id]
                return {
                    "data": simulated_data,
                    "total": len(simulated_data),
                    "_simulation": True
                }
            
            # Otherwise, call the real Method API
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/accounts",
                    params={"entity_id": entity_id},
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Method API error: {response.text}"
                    )
                    
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Method API: {str(e)}")
    
    async def simulate_credit_card_connection(self, entity_id: str, card_brand: str = "visa") -> Dict[str, Any]:
        """
        Simulate connecting a credit card (dev environment only)
        
        This bypasses Method Connect and creates a simulated credit card
        that can be used for payments in the dev environment.
        
        Args:
            entity_id: Method entity ID
            card_brand: Brand of credit card (visa, mastercard, amex, discover)
            
        Returns:
            Simulated credit card data
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            import uuid
            import random
            from datetime import datetime, timedelta
            
            account_id = f"acc_cc_{str(uuid.uuid4())[:8]}"
            
            # Define card brand specifics
            brand_configs = {
                "visa": {
                    "brand": "visa",
                    "name": "Chase Sapphire Preferred",
                    "last_four": "4242",
                    "color": "blue"
                },
                "mastercard": {
                    "brand": "mastercard", 
                    "name": "Capital One Venture",
                    "last_four": "5555",
                    "color": "red"
                },
                "amex": {
                    "brand": "amex",
                    "name": "American Express Gold",
                    "last_four": "1005",
                    "color": "green"
                },
                "discover": {
                    "brand": "discover",
                    "name": "Discover it Cash Back",
                    "last_four": "1117",
                    "color": "orange"
                }
            }
            
            config = brand_configs.get(card_brand, brand_configs["visa"])
            
            # Generate realistic credit card data
            balance = random.randint(50000, 500000)  # $500 - $5000 in cents
            credit_limit = balance + random.randint(100000, 1000000)  # Additional available credit
            minimum_payment = max(2500, int(balance * 0.02))  # At least $25 or 2% of balance
            
            # Generate due date (15-45 days from now)
            due_date = datetime.now() + timedelta(days=random.randint(15, 45))
            last_payment_date = datetime.now() - timedelta(days=random.randint(5, 30))
            
            simulated_credit_card = {
                "id": account_id,
                "entity_id": entity_id,
                "type": "liability",
                "brand": config["brand"],
                "last_four": config["last_four"],
                "name": config["name"],
                "status": "active",
                "balance": balance,
                "exp_month": random.randint(1, 12),
                "exp_year": datetime.now().year + random.randint(1, 5),
                "liability": {
                    "mch": config["last_four"],
                    "mask": config["last_four"],
                    "name": config["name"],
                    "type": "credit_card",
                    "balance": balance,
                    "credit_limit": credit_limit,
                    "available_credit": credit_limit - balance,
                    "last_payment_date": last_payment_date.isoformat(),
                    "last_payment_amount": random.randint(5000, minimum_payment),
                    "next_payment_due_date": due_date.isoformat(),
                    "next_payment_minimum_amount": minimum_payment,
                    "apr": round(random.uniform(15.99, 29.99), 2),
                    "statement_balance": balance
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": datetime.now().isoformat()
            }
            
            # Add simulation metadata
            simulated_credit_card["_simulation"] = True
            simulated_credit_card["_simulation_note"] = f"This is a simulated {config['brand']} credit card for development testing"
            
            # Store in simulated accounts for retrieval
            if entity_id not in _simulated_accounts:
                _simulated_accounts[entity_id] = []
            _simulated_accounts[entity_id].append(simulated_credit_card)
            
            return simulated_credit_card
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate credit card connection: {str(e)}")
    
    async def simulate_multiple_credit_cards(self, entity_id: str) -> Dict[str, Any]:
        """
        Simulate connecting multiple credit cards for comprehensive testing
        
        Args:
            entity_id: Method entity ID
            
        Returns:
            List of simulated credit cards
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            cards = []
            brands = ["visa", "mastercard", "amex", "discover"]
            
            # Create 2-3 credit cards with different brands
            for brand in brands[:3]:  # Create 3 cards
                credit_card = await self.simulate_credit_card_connection(entity_id, brand)
                cards.append(credit_card)
            
            return {
                "cards": cards,
                "total": len(cards),
                "_simulation": True,
                "_simulation_note": "These are simulated credit cards for development testing"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate multiple credit cards: {str(e)}")
    
    async def create_payment(
        self,
        source_account_id: str,
        destination_account_id: str,
        amount: int,  # Amount in cents
        description: str = "AgentPay bill payment"
    ) -> Dict[str, Any]:
        """
        Create a payment between accounts
        
        Args:
            source_account_id: Source account (bank account)
            destination_account_id: Destination account (credit card)
            amount: Payment amount in cents
            description: Payment description
            
        Returns:
            Method payment object
        """
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "amount": amount,
                    "source": source_account_id,
                    "destination": destination_account_id,
                    "description": description
                }
                
                response = await client.post(
                    f"{self.base_url}/payments",
                    json=payload,
                    headers=self._get_headers()
                )
                
                if response.status_code == 201:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Method API error: {response.text}"
                    )
                    
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Method API: {str(e)}")
    
    async def simulate_credit_card_connection(self, entity_id: str, card_brand: str = "visa") -> Dict[str, Any]:
        """
        Simulate connecting a credit card (dev environment only)
        
        This bypasses Method Connect and creates a simulated credit card
        that can be used for payments in the dev environment.
        
        Args:
            entity_id: Method entity ID
            card_brand: Brand of credit card (visa, mastercard, amex, discover)
            
        Returns:
            Simulated credit card data
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            import uuid
            import random
            from datetime import datetime, timedelta
            
            account_id = f"acc_cc_{str(uuid.uuid4())[:8]}"
            
            # Define card brand specifics
            brand_configs = {
                "visa": {
                    "brand": "visa",
                    "name": "Chase Sapphire Preferred",
                    "last_four": "4242",
                    "color": "blue"
                },
                "mastercard": {
                    "brand": "mastercard", 
                    "name": "Capital One Venture",
                    "last_four": "5555",
                    "color": "red"
                },
                "amex": {
                    "brand": "amex",
                    "name": "American Express Gold",
                    "last_four": "1005",
                    "color": "green"
                },
                "discover": {
                    "brand": "discover",
                    "name": "Discover it Cash Back",
                    "last_four": "1117",
                    "color": "orange"
                }
            }
            
            config = brand_configs.get(card_brand, brand_configs["visa"])
            
            # Generate realistic credit card data
            balance = random.randint(50000, 500000)  # $500 - $5000 in cents
            credit_limit = balance + random.randint(100000, 1000000)  # Additional available credit
            minimum_payment = max(2500, int(balance * 0.02))  # At least $25 or 2% of balance
            
            # Generate due date (15-45 days from now)
            due_date = datetime.now() + timedelta(days=random.randint(15, 45))
            last_payment_date = datetime.now() - timedelta(days=random.randint(5, 30))
            
            simulated_credit_card = {
                "id": account_id,
                "entity_id": entity_id,
                "type": "liability",
                "brand": config["brand"],
                "last_four": config["last_four"],
                "name": config["name"],
                "status": "active",
                "balance": balance,
                "exp_month": random.randint(1, 12),
                "exp_year": datetime.now().year + random.randint(1, 5),
                "liability": {
                    "mch": config["last_four"],
                    "mask": config["last_four"],
                    "name": config["name"],
                    "type": "credit_card",
                    "balance": balance,
                    "credit_limit": credit_limit,
                    "available_credit": credit_limit - balance,
                    "last_payment_date": last_payment_date.isoformat(),
                    "last_payment_amount": random.randint(5000, minimum_payment),
                    "next_payment_due_date": due_date.isoformat(),
                    "next_payment_minimum_amount": minimum_payment,
                    "apr": round(random.uniform(15.99, 29.99), 2),
                    "statement_balance": balance
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": datetime.now().isoformat()
            }
            
            # Add simulation metadata
            simulated_credit_card["_simulation"] = True
            simulated_credit_card["_simulation_note"] = f"This is a simulated {config['brand']} credit card for development testing"
            
            # Store in simulated accounts for retrieval
            if entity_id not in _simulated_accounts:
                _simulated_accounts[entity_id] = []
            _simulated_accounts[entity_id].append(simulated_credit_card)
            
            return simulated_credit_card
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate credit card connection: {str(e)}")
    
    async def simulate_multiple_credit_cards(self, entity_id: str) -> Dict[str, Any]:
        """
        Simulate connecting multiple credit cards for comprehensive testing
        
        Args:
            entity_id: Method entity ID
            
        Returns:
            List of simulated credit cards
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            cards = []
            brands = ["visa", "mastercard", "amex", "discover"]
            
            # Create 2-3 credit cards with different brands
            for brand in brands[:3]:  # Create 3 cards
                credit_card = await self.simulate_credit_card_connection(entity_id, brand)
                cards.append(credit_card)
            
            return {
                "cards": cards,
                "total": len(cards),
                "_simulation": True,
                "_simulation_note": "These are simulated credit cards for development testing"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate multiple credit cards: {str(e)}")
    
    async def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Get payment details
        
        Args:
            payment_id: Method payment ID
            
        Returns:
            Method payment object
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/payments/{payment_id}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Method API error: {response.text}"
                    )
                    
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Method API: {str(e)}")
    
    async def simulate_credit_card_connection(self, entity_id: str, card_brand: str = "visa") -> Dict[str, Any]:
        """
        Simulate connecting a credit card (dev environment only)
        
        This bypasses Method Connect and creates a simulated credit card
        that can be used for payments in the dev environment.
        
        Args:
            entity_id: Method entity ID
            card_brand: Brand of credit card (visa, mastercard, amex, discover)
            
        Returns:
            Simulated credit card data
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            import uuid
            import random
            from datetime import datetime, timedelta
            
            account_id = f"acc_cc_{str(uuid.uuid4())[:8]}"
            
            # Define card brand specifics
            brand_configs = {
                "visa": {
                    "brand": "visa",
                    "name": "Chase Sapphire Preferred",
                    "last_four": "4242",
                    "color": "blue"
                },
                "mastercard": {
                    "brand": "mastercard", 
                    "name": "Capital One Venture",
                    "last_four": "5555",
                    "color": "red"
                },
                "amex": {
                    "brand": "amex",
                    "name": "American Express Gold",
                    "last_four": "1005",
                    "color": "green"
                },
                "discover": {
                    "brand": "discover",
                    "name": "Discover it Cash Back",
                    "last_four": "1117",
                    "color": "orange"
                }
            }
            
            config = brand_configs.get(card_brand, brand_configs["visa"])
            
            # Generate realistic credit card data
            balance = random.randint(50000, 500000)  # $500 - $5000 in cents
            credit_limit = balance + random.randint(100000, 1000000)  # Additional available credit
            minimum_payment = max(2500, int(balance * 0.02))  # At least $25 or 2% of balance
            
            # Generate due date (15-45 days from now)
            due_date = datetime.now() + timedelta(days=random.randint(15, 45))
            last_payment_date = datetime.now() - timedelta(days=random.randint(5, 30))
            
            simulated_credit_card = {
                "id": account_id,
                "entity_id": entity_id,
                "type": "liability",
                "brand": config["brand"],
                "last_four": config["last_four"],
                "name": config["name"],
                "status": "active",
                "balance": balance,
                "exp_month": random.randint(1, 12),
                "exp_year": datetime.now().year + random.randint(1, 5),
                "liability": {
                    "mch": config["last_four"],
                    "mask": config["last_four"],
                    "name": config["name"],
                    "type": "credit_card",
                    "balance": balance,
                    "credit_limit": credit_limit,
                    "available_credit": credit_limit - balance,
                    "last_payment_date": last_payment_date.isoformat(),
                    "last_payment_amount": random.randint(5000, minimum_payment),
                    "next_payment_due_date": due_date.isoformat(),
                    "next_payment_minimum_amount": minimum_payment,
                    "apr": round(random.uniform(15.99, 29.99), 2),
                    "statement_balance": balance
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": datetime.now().isoformat()
            }
            
            # Add simulation metadata
            simulated_credit_card["_simulation"] = True
            simulated_credit_card["_simulation_note"] = f"This is a simulated {config['brand']} credit card for development testing"
            
            # Store in simulated accounts for retrieval
            if entity_id not in _simulated_accounts:
                _simulated_accounts[entity_id] = []
            _simulated_accounts[entity_id].append(simulated_credit_card)
            
            return simulated_credit_card
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate credit card connection: {str(e)}")
    
    async def simulate_multiple_credit_cards(self, entity_id: str) -> Dict[str, Any]:
        """
        Simulate connecting multiple credit cards for comprehensive testing
        
        Args:
            entity_id: Method entity ID
            
        Returns:
            List of simulated credit cards
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            cards = []
            brands = ["visa", "mastercard", "amex", "discover"]
            
            # Create 2-3 credit cards with different brands
            for brand in brands[:3]:  # Create 3 cards
                credit_card = await self.simulate_credit_card_connection(entity_id, brand)
                cards.append(credit_card)
            
            return {
                "cards": cards,
                "total": len(cards),
                "_simulation": True,
                "_simulation_note": "These are simulated credit cards for development testing"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate multiple credit cards: {str(e)}")
    
    async def get_payments(
        self, 
        source: Optional[str] = None,
        destination: Optional[str] = None,
        acc_id: Optional[str] = None,
        source_holder_id: Optional[str] = None,
        destination_holder_id: Optional[str] = None,
        holder_id: Optional[str] = None,
        status: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: Optional[str] = None,
        page_cursor: Optional[str] = None,
        page_limit: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all payments with Method API query parameters
        
        Args:
            source: The ID of the Payment's source
            destination: The ID of the Payment's destination  
            acc_id: The ID of either the Payment's source or destination
            source_holder_id: The ID of the Payment's source holder (Entity)
            destination_holder_id: The ID of the Payment's destination holder (Entity)
            holder_id: The ID of either source or destination holder (Entity)
            status: The Payment's status
            from_date: ISO 8601 date (YYYY-MM-DD) to filter payments created on/after
            to_date: ISO 8601 date (YYYY-MM-DD) to filter payments created on/before
            page: The number of the page to return
            page_cursor: The ID of a resource from which a page should start/end
            page_limit: Number of Payments per page (default/max 100)
            
        Returns:
            Method payments response with data array
        """
        try:
            async with httpx.AsyncClient() as client:
                params = {}
                
                # Add all non-None parameters
                if source: params["source"] = source
                if destination: params["destination"] = destination
                if acc_id: params["acc_id"] = acc_id
                if source_holder_id: params["source_holder_id"] = source_holder_id
                if destination_holder_id: params["destination_holder_id"] = destination_holder_id
                if holder_id: params["holder_id"] = holder_id
                if status: params["status"] = status
                if from_date: params["from_date"] = from_date
                if to_date: params["to_date"] = to_date
                if page: params["page"] = page
                if page_cursor: params["page_cursor"] = page_cursor
                if page_limit: params["page_limit"] = page_limit
                    
                response = await client.get(
                    f"{self.base_url}/payments",
                    params=params,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Method API error: {response.text}"
                    )
                    
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Method API: {str(e)}")
    
    async def simulate_credit_card_connection(self, entity_id: str, card_brand: str = "visa") -> Dict[str, Any]:
        """
        Simulate connecting a credit card (dev environment only)
        
        This bypasses Method Connect and creates a simulated credit card
        that can be used for payments in the dev environment.
        
        Args:
            entity_id: Method entity ID
            card_brand: Brand of credit card (visa, mastercard, amex, discover)
            
        Returns:
            Simulated credit card data
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            import uuid
            import random
            from datetime import datetime, timedelta
            
            account_id = f"acc_cc_{str(uuid.uuid4())[:8]}"
            
            # Define card brand specifics
            brand_configs = {
                "visa": {
                    "brand": "visa",
                    "name": "Chase Sapphire Preferred",
                    "last_four": "4242",
                    "color": "blue"
                },
                "mastercard": {
                    "brand": "mastercard", 
                    "name": "Capital One Venture",
                    "last_four": "5555",
                    "color": "red"
                },
                "amex": {
                    "brand": "amex",
                    "name": "American Express Gold",
                    "last_four": "1005",
                    "color": "green"
                },
                "discover": {
                    "brand": "discover",
                    "name": "Discover it Cash Back",
                    "last_four": "1117",
                    "color": "orange"
                }
            }
            
            config = brand_configs.get(card_brand, brand_configs["visa"])
            
            # Generate realistic credit card data
            balance = random.randint(50000, 500000)  # $500 - $5000 in cents
            credit_limit = balance + random.randint(100000, 1000000)  # Additional available credit
            minimum_payment = max(2500, int(balance * 0.02))  # At least $25 or 2% of balance
            
            # Generate due date (15-45 days from now)
            due_date = datetime.now() + timedelta(days=random.randint(15, 45))
            last_payment_date = datetime.now() - timedelta(days=random.randint(5, 30))
            
            simulated_credit_card = {
                "id": account_id,
                "entity_id": entity_id,
                "type": "liability",
                "brand": config["brand"],
                "last_four": config["last_four"],
                "name": config["name"],
                "status": "active",
                "balance": balance,
                "exp_month": random.randint(1, 12),
                "exp_year": datetime.now().year + random.randint(1, 5),
                "liability": {
                    "mch": config["last_four"],
                    "mask": config["last_four"],
                    "name": config["name"],
                    "type": "credit_card",
                    "balance": balance,
                    "credit_limit": credit_limit,
                    "available_credit": credit_limit - balance,
                    "last_payment_date": last_payment_date.isoformat(),
                    "last_payment_amount": random.randint(5000, minimum_payment),
                    "next_payment_due_date": due_date.isoformat(),
                    "next_payment_minimum_amount": minimum_payment,
                    "apr": round(random.uniform(15.99, 29.99), 2),
                    "statement_balance": balance
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": datetime.now().isoformat()
            }
            
            # Add simulation metadata
            simulated_credit_card["_simulation"] = True
            simulated_credit_card["_simulation_note"] = f"This is a simulated {config['brand']} credit card for development testing"
            
            # Store in simulated accounts for retrieval
            if entity_id not in _simulated_accounts:
                _simulated_accounts[entity_id] = []
            _simulated_accounts[entity_id].append(simulated_credit_card)
            
            return simulated_credit_card
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate credit card connection: {str(e)}")
    
    async def simulate_multiple_credit_cards(self, entity_id: str) -> Dict[str, Any]:
        """
        Simulate connecting multiple credit cards for comprehensive testing
        
        Args:
            entity_id: Method entity ID
            
        Returns:
            List of simulated credit cards
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            cards = []
            brands = ["visa", "mastercard", "amex", "discover"]
            
            # Create 2-3 credit cards with different brands
            for brand in brands[:3]:  # Create 3 cards
                credit_card = await self.simulate_credit_card_connection(entity_id, brand)
                cards.append(credit_card)
            
            return {
                "cards": cards,
                "total": len(cards),
                "_simulation": True,
                "_simulation_note": "These are simulated credit cards for development testing"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate multiple credit cards: {str(e)}")
    
    async def delete_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Delete a payment
        
        Args:
            payment_id: Method payment ID
            
        Returns:
            Method API response
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/payments/{payment_id}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Method API error: {response.text}"
                    )
                    
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Method API: {str(e)}")
    
    async def simulate_credit_card_connection(self, entity_id: str, card_brand: str = "visa") -> Dict[str, Any]:
        """
        Simulate connecting a credit card (dev environment only)
        
        This bypasses Method Connect and creates a simulated credit card
        that can be used for payments in the dev environment.
        
        Args:
            entity_id: Method entity ID
            card_brand: Brand of credit card (visa, mastercard, amex, discover)
            
        Returns:
            Simulated credit card data
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            import uuid
            import random
            from datetime import datetime, timedelta
            
            account_id = f"acc_cc_{str(uuid.uuid4())[:8]}"
            
            # Define card brand specifics
            brand_configs = {
                "visa": {
                    "brand": "visa",
                    "name": "Chase Sapphire Preferred",
                    "last_four": "4242",
                    "color": "blue"
                },
                "mastercard": {
                    "brand": "mastercard", 
                    "name": "Capital One Venture",
                    "last_four": "5555",
                    "color": "red"
                },
                "amex": {
                    "brand": "amex",
                    "name": "American Express Gold",
                    "last_four": "1005",
                    "color": "green"
                },
                "discover": {
                    "brand": "discover",
                    "name": "Discover it Cash Back",
                    "last_four": "1117",
                    "color": "orange"
                }
            }
            
            config = brand_configs.get(card_brand, brand_configs["visa"])
            
            # Generate realistic credit card data
            balance = random.randint(50000, 500000)  # $500 - $5000 in cents
            credit_limit = balance + random.randint(100000, 1000000)  # Additional available credit
            minimum_payment = max(2500, int(balance * 0.02))  # At least $25 or 2% of balance
            
            # Generate due date (15-45 days from now)
            due_date = datetime.now() + timedelta(days=random.randint(15, 45))
            last_payment_date = datetime.now() - timedelta(days=random.randint(5, 30))
            
            simulated_credit_card = {
                "id": account_id,
                "entity_id": entity_id,
                "type": "liability",
                "brand": config["brand"],
                "last_four": config["last_four"],
                "name": config["name"],
                "status": "active",
                "balance": balance,
                "exp_month": random.randint(1, 12),
                "exp_year": datetime.now().year + random.randint(1, 5),
                "liability": {
                    "mch": config["last_four"],
                    "mask": config["last_four"],
                    "name": config["name"],
                    "type": "credit_card",
                    "balance": balance,
                    "credit_limit": credit_limit,
                    "available_credit": credit_limit - balance,
                    "last_payment_date": last_payment_date.isoformat(),
                    "last_payment_amount": random.randint(5000, minimum_payment),
                    "next_payment_due_date": due_date.isoformat(),
                    "next_payment_minimum_amount": minimum_payment,
                    "apr": round(random.uniform(15.99, 29.99), 2),
                    "statement_balance": balance
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": datetime.now().isoformat()
            }
            
            # Add simulation metadata
            simulated_credit_card["_simulation"] = True
            simulated_credit_card["_simulation_note"] = f"This is a simulated {config['brand']} credit card for development testing"
            
            # Store in simulated accounts for retrieval
            if entity_id not in _simulated_accounts:
                _simulated_accounts[entity_id] = []
            _simulated_accounts[entity_id].append(simulated_credit_card)
            
            return simulated_credit_card
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate credit card connection: {str(e)}")
    
    async def simulate_multiple_credit_cards(self, entity_id: str) -> Dict[str, Any]:
        """
        Simulate connecting multiple credit cards for comprehensive testing
        
        Args:
            entity_id: Method entity ID
            
        Returns:
            List of simulated credit cards
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            cards = []
            brands = ["visa", "mastercard", "amex", "discover"]
            
            # Create 2-3 credit cards with different brands
            for brand in brands[:3]:  # Create 3 cards
                credit_card = await self.simulate_credit_card_connection(entity_id, brand)
                cards.append(credit_card)
            
            return {
                "cards": cards,
                "total": len(cards),
                "_simulation": True,
                "_simulation_note": "These are simulated credit cards for development testing"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate multiple credit cards: {str(e)}")
    
    # ELEMENTS (Method Connect for bank account connection)
    async def create_element_token(self, entity_id: str, element_type: str = "connect") -> Dict[str, Any]:
        """
        Create an element token for Method Connect
        
        Args:
            entity_id: Method entity ID
            element_type: Type of element (usually 'connect')
            
        Returns:
            Element token response
        """
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "entity_id": entity_id,
                    "type": element_type
                }
                
                response = await client.post(
                    f"{self.base_url}/elements",
                    json=payload,
                    headers=self._get_headers()
                )
                
                if response.status_code == 201:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Method API error: {response.text}"
                    )
                    
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Method API: {str(e)}")
    
    async def simulate_credit_card_connection(self, entity_id: str, card_brand: str = "visa") -> Dict[str, Any]:
        """
        Simulate connecting a credit card (dev environment only)
        
        This bypasses Method Connect and creates a simulated credit card
        that can be used for payments in the dev environment.
        
        Args:
            entity_id: Method entity ID
            card_brand: Brand of credit card (visa, mastercard, amex, discover)
            
        Returns:
            Simulated credit card data
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            import uuid
            import random
            from datetime import datetime, timedelta
            
            account_id = f"acc_cc_{str(uuid.uuid4())[:8]}"
            
            # Define card brand specifics
            brand_configs = {
                "visa": {
                    "brand": "visa",
                    "name": "Chase Sapphire Preferred",
                    "last_four": "4242",
                    "color": "blue"
                },
                "mastercard": {
                    "brand": "mastercard", 
                    "name": "Capital One Venture",
                    "last_four": "5555",
                    "color": "red"
                },
                "amex": {
                    "brand": "amex",
                    "name": "American Express Gold",
                    "last_four": "1005",
                    "color": "green"
                },
                "discover": {
                    "brand": "discover",
                    "name": "Discover it Cash Back",
                    "last_four": "1117",
                    "color": "orange"
                }
            }
            
            config = brand_configs.get(card_brand, brand_configs["visa"])
            
            # Generate realistic credit card data
            balance = random.randint(50000, 500000)  # $500 - $5000 in cents
            credit_limit = balance + random.randint(100000, 1000000)  # Additional available credit
            minimum_payment = max(2500, int(balance * 0.02))  # At least $25 or 2% of balance
            
            # Generate due date (15-45 days from now)
            due_date = datetime.now() + timedelta(days=random.randint(15, 45))
            last_payment_date = datetime.now() - timedelta(days=random.randint(5, 30))
            
            simulated_credit_card = {
                "id": account_id,
                "entity_id": entity_id,
                "type": "liability",
                "brand": config["brand"],
                "last_four": config["last_four"],
                "name": config["name"],
                "status": "active",
                "balance": balance,
                "exp_month": random.randint(1, 12),
                "exp_year": datetime.now().year + random.randint(1, 5),
                "liability": {
                    "mch": config["last_four"],
                    "mask": config["last_four"],
                    "name": config["name"],
                    "type": "credit_card",
                    "balance": balance,
                    "credit_limit": credit_limit,
                    "available_credit": credit_limit - balance,
                    "last_payment_date": last_payment_date.isoformat(),
                    "last_payment_amount": random.randint(5000, minimum_payment),
                    "next_payment_due_date": due_date.isoformat(),
                    "next_payment_minimum_amount": minimum_payment,
                    "apr": round(random.uniform(15.99, 29.99), 2),
                    "statement_balance": balance
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": datetime.now().isoformat()
            }
            
            # Add simulation metadata
            simulated_credit_card["_simulation"] = True
            simulated_credit_card["_simulation_note"] = f"This is a simulated {config['brand']} credit card for development testing"
            
            # Store in simulated accounts for retrieval
            if entity_id not in _simulated_accounts:
                _simulated_accounts[entity_id] = []
            _simulated_accounts[entity_id].append(simulated_credit_card)
            
            return simulated_credit_card
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate credit card connection: {str(e)}")
    
    async def simulate_multiple_credit_cards(self, entity_id: str) -> Dict[str, Any]:
        """
        Simulate connecting multiple credit cards for comprehensive testing
        
        Args:
            entity_id: Method entity ID
            
        Returns:
            List of simulated credit cards
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            cards = []
            brands = ["visa", "mastercard", "amex", "discover"]
            
            # Create 2-3 credit cards with different brands
            for brand in brands[:3]:  # Create 3 cards
                credit_card = await self.simulate_credit_card_connection(entity_id, brand)
                cards.append(credit_card)
            
            return {
                "cards": cards,
                "total": len(cards),
                "_simulation": True,
                "_simulation_note": "These are simulated credit cards for development testing"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate multiple credit cards: {str(e)}")
    
    async def get_element_results(self, element_token: str) -> Dict[str, Any]:
        """
        Get results from Method Connect element
        
        Args:
            element_token: Element token from create_element_token
            
        Returns:
            Connected account information
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/elements/{element_token}",
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Method API error: {response.text}"
                    )
                    
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Method API: {str(e)}")
    
    async def simulate_credit_card_connection(self, entity_id: str, card_brand: str = "visa") -> Dict[str, Any]:
        """
        Simulate connecting a credit card (dev environment only)
        
        This bypasses Method Connect and creates a simulated credit card
        that can be used for payments in the dev environment.
        
        Args:
            entity_id: Method entity ID
            card_brand: Brand of credit card (visa, mastercard, amex, discover)
            
        Returns:
            Simulated credit card data
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            import uuid
            import random
            from datetime import datetime, timedelta
            
            account_id = f"acc_cc_{str(uuid.uuid4())[:8]}"
            
            # Define card brand specifics
            brand_configs = {
                "visa": {
                    "brand": "visa",
                    "name": "Chase Sapphire Preferred",
                    "last_four": "4242",
                    "color": "blue"
                },
                "mastercard": {
                    "brand": "mastercard", 
                    "name": "Capital One Venture",
                    "last_four": "5555",
                    "color": "red"
                },
                "amex": {
                    "brand": "amex",
                    "name": "American Express Gold",
                    "last_four": "1005",
                    "color": "green"
                },
                "discover": {
                    "brand": "discover",
                    "name": "Discover it Cash Back",
                    "last_four": "1117",
                    "color": "orange"
                }
            }
            
            config = brand_configs.get(card_brand, brand_configs["visa"])
            
            # Generate realistic credit card data
            balance = random.randint(50000, 500000)  # $500 - $5000 in cents
            credit_limit = balance + random.randint(100000, 1000000)  # Additional available credit
            minimum_payment = max(2500, int(balance * 0.02))  # At least $25 or 2% of balance
            
            # Generate due date (15-45 days from now)
            due_date = datetime.now() + timedelta(days=random.randint(15, 45))
            last_payment_date = datetime.now() - timedelta(days=random.randint(5, 30))
            
            simulated_credit_card = {
                "id": account_id,
                "entity_id": entity_id,
                "type": "liability",
                "brand": config["brand"],
                "last_four": config["last_four"],
                "name": config["name"],
                "status": "active",
                "balance": balance,
                "exp_month": random.randint(1, 12),
                "exp_year": datetime.now().year + random.randint(1, 5),
                "liability": {
                    "mch": config["last_four"],
                    "mask": config["last_four"],
                    "name": config["name"],
                    "type": "credit_card",
                    "balance": balance,
                    "credit_limit": credit_limit,
                    "available_credit": credit_limit - balance,
                    "last_payment_date": last_payment_date.isoformat(),
                    "last_payment_amount": random.randint(5000, minimum_payment),
                    "next_payment_due_date": due_date.isoformat(),
                    "next_payment_minimum_amount": minimum_payment,
                    "apr": round(random.uniform(15.99, 29.99), 2),
                    "statement_balance": balance
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": datetime.now().isoformat()
            }
            
            # Add simulation metadata
            simulated_credit_card["_simulation"] = True
            simulated_credit_card["_simulation_note"] = f"This is a simulated {config['brand']} credit card for development testing"
            
            # Store in simulated accounts for retrieval
            if entity_id not in _simulated_accounts:
                _simulated_accounts[entity_id] = []
            _simulated_accounts[entity_id].append(simulated_credit_card)
            
            return simulated_credit_card
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate credit card connection: {str(e)}")
    
    async def simulate_multiple_credit_cards(self, entity_id: str) -> Dict[str, Any]:
        """
        Simulate connecting multiple credit cards for comprehensive testing
        
        Args:
            entity_id: Method entity ID
            
        Returns:
            List of simulated credit cards
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            cards = []
            brands = ["visa", "mastercard", "amex", "discover"]
            
            # Create 2-3 credit cards with different brands
            for brand in brands[:3]:  # Create 3 cards
                credit_card = await self.simulate_credit_card_connection(entity_id, brand)
                cards.append(credit_card)
            
            return {
                "cards": cards,
                "total": len(cards),
                "_simulation": True,
                "_simulation_note": "These are simulated credit cards for development testing"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate multiple credit cards: {str(e)}")
    
    async def create_account(self, account_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a bank account manually (alternative to Method Connect)
        
        Args:
            account_data: Account creation data
            
        Returns:
            Created account information
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/accounts",
                    json=account_data,
                    headers=self._get_headers()
                )
                
                if response.status_code == 201:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Method API error: {response.text}"
                    )
                    
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Method API: {str(e)}")
    
    async def simulate_credit_card_connection(self, entity_id: str, card_brand: str = "visa") -> Dict[str, Any]:
        """
        Simulate connecting a credit card (dev environment only)
        
        This bypasses Method Connect and creates a simulated credit card
        that can be used for payments in the dev environment.
        
        Args:
            entity_id: Method entity ID
            card_brand: Brand of credit card (visa, mastercard, amex, discover)
            
        Returns:
            Simulated credit card data
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            import uuid
            import random
            from datetime import datetime, timedelta
            
            account_id = f"acc_cc_{str(uuid.uuid4())[:8]}"
            
            # Define card brand specifics
            brand_configs = {
                "visa": {
                    "brand": "visa",
                    "name": "Chase Sapphire Preferred",
                    "last_four": "4242",
                    "color": "blue"
                },
                "mastercard": {
                    "brand": "mastercard", 
                    "name": "Capital One Venture",
                    "last_four": "5555",
                    "color": "red"
                },
                "amex": {
                    "brand": "amex",
                    "name": "American Express Gold",
                    "last_four": "1005",
                    "color": "green"
                },
                "discover": {
                    "brand": "discover",
                    "name": "Discover it Cash Back",
                    "last_four": "1117",
                    "color": "orange"
                }
            }
            
            config = brand_configs.get(card_brand, brand_configs["visa"])
            
            # Generate realistic credit card data
            balance = random.randint(50000, 500000)  # $500 - $5000 in cents
            credit_limit = balance + random.randint(100000, 1000000)  # Additional available credit
            minimum_payment = max(2500, int(balance * 0.02))  # At least $25 or 2% of balance
            
            # Generate due date (15-45 days from now)
            due_date = datetime.now() + timedelta(days=random.randint(15, 45))
            last_payment_date = datetime.now() - timedelta(days=random.randint(5, 30))
            
            simulated_credit_card = {
                "id": account_id,
                "entity_id": entity_id,
                "type": "liability",
                "brand": config["brand"],
                "last_four": config["last_four"],
                "name": config["name"],
                "status": "active",
                "balance": balance,
                "exp_month": random.randint(1, 12),
                "exp_year": datetime.now().year + random.randint(1, 5),
                "liability": {
                    "mch": config["last_four"],
                    "mask": config["last_four"],
                    "name": config["name"],
                    "type": "credit_card",
                    "balance": balance,
                    "credit_limit": credit_limit,
                    "available_credit": credit_limit - balance,
                    "last_payment_date": last_payment_date.isoformat(),
                    "last_payment_amount": random.randint(5000, minimum_payment),
                    "next_payment_due_date": due_date.isoformat(),
                    "next_payment_minimum_amount": minimum_payment,
                    "apr": round(random.uniform(15.99, 29.99), 2),
                    "statement_balance": balance
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": datetime.now().isoformat()
            }
            
            # Add simulation metadata
            simulated_credit_card["_simulation"] = True
            simulated_credit_card["_simulation_note"] = f"This is a simulated {config['brand']} credit card for development testing"
            
            # Store in simulated accounts for retrieval
            if entity_id not in _simulated_accounts:
                _simulated_accounts[entity_id] = []
            _simulated_accounts[entity_id].append(simulated_credit_card)
            
            return simulated_credit_card
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate credit card connection: {str(e)}")
    
    async def simulate_multiple_credit_cards(self, entity_id: str) -> Dict[str, Any]:
        """
        Simulate connecting multiple credit cards for comprehensive testing
        
        Args:
            entity_id: Method entity ID
            
        Returns:
            List of simulated credit cards
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            cards = []
            brands = ["visa", "mastercard", "amex", "discover"]
            
            # Create 2-3 credit cards with different brands
            for brand in brands[:3]:  # Create 3 cards
                credit_card = await self.simulate_credit_card_connection(entity_id, brand)
                cards.append(credit_card)
            
            return {
                "cards": cards,
                "total": len(cards),
                "_simulation": True,
                "_simulation_note": "These are simulated credit cards for development testing"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate multiple credit cards: {str(e)}")
    
    # SIMULATION METHODS (DEV ENVIRONMENT ONLY)
    async def simulate_bank_account_connection(self, entity_id: str, account_type: str = "checking") -> Dict[str, Any]:
        """
        Simulate connecting a bank account (dev environment only)
        
        This bypasses Method Connect and creates a simulated bank account
        that can be used for payments in the dev environment.
        
        Args:
            entity_id: Method entity ID
            account_type: Type of account (checking, savings)
            
        Returns:
            Simulated bank account data
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            # For simulation, create a mock account without calling Method API
            import uuid
            account_id = f"acc_sim_{str(uuid.uuid4())[:8]}"
            
            simulated_account = {
                "id": account_id,
                "entity_id": entity_id,
                "type": account_type,
                "routing_number": "021000021",  # Chase Bank routing number for simulation
                "account_number": f"****{str(uuid.uuid4())[:4]}",  # Masked account number
                "last_four": str(uuid.uuid4())[:4],
                "account_name": f"Simulated {account_type.title()} Account",
                "bank_name": "Chase Bank (Simulated)",
                "status": "active",
                "balance": 500000,  # $5000.00 in cents
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
            
            created_account = simulated_account
            
            # Add simulation metadata
            created_account["_simulation"] = True
            created_account["_simulation_note"] = "This is a simulated bank account for development testing"
            
            # Store in simulated accounts for retrieval
            if entity_id not in _simulated_accounts:
                _simulated_accounts[entity_id] = []
            _simulated_accounts[entity_id].append(created_account)
            
            return created_account
            
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate bank account connection: {str(e)}")
    
    async def simulate_multiple_bank_accounts(self, entity_id: str) -> Dict[str, Any]:
        """
        Simulate connecting multiple bank accounts for comprehensive testing
        
        Args:
            entity_id: Method entity ID
            
        Returns:
            List of simulated bank accounts
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            accounts = []
            
            # Create checking account
            checking_account = await self.simulate_bank_account_connection(entity_id, "checking")
            accounts.append(checking_account)
            
            # Create savings account
            savings_account = await self.simulate_bank_account_connection(entity_id, "savings")
            accounts.append(savings_account)
            
            return {
                "accounts": accounts,
                "total": len(accounts),
                "_simulation": True,
                "_simulation_note": "These are simulated bank accounts for development testing"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate multiple bank accounts: {str(e)}")

    async def simulate_payment_update(self, payment_id: str, status: str, error_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Simulate updating a payment's status (dev environment only)
        
        Args:
            payment_id: Method payment ID
            status: New payment status
            error_code: Optional error code for failed payments
            
        Returns:
            Updated Method payment object
        """
        if self.environment != "dev":
            raise HTTPException(
                status_code=403,
                detail="Simulation endpoints are only available in development environment"
            )
        
        try:
            async with httpx.AsyncClient() as client:
                payload = {"status": status}
                if error_code:
                    payload["error_code"] = error_code
                
                response = await client.post(
                    f"{self.base_url}/simulate/payments/{payment_id}",
                    json=payload,
                    headers=self._get_headers()
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Method API error: {response.text}"
                    )
                    
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Method API: {str(e)}")
    
    async def simulate_credit_card_connection(self, entity_id: str, card_brand: str = "visa") -> Dict[str, Any]:
        """
        Simulate connecting a credit card (dev environment only)
        
        This bypasses Method Connect and creates a simulated credit card
        that can be used for payments in the dev environment.
        
        Args:
            entity_id: Method entity ID
            card_brand: Brand of credit card (visa, mastercard, amex, discover)
            
        Returns:
            Simulated credit card data
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            import uuid
            import random
            from datetime import datetime, timedelta
            
            account_id = f"acc_cc_{str(uuid.uuid4())[:8]}"
            
            # Define card brand specifics
            brand_configs = {
                "visa": {
                    "brand": "visa",
                    "name": "Chase Sapphire Preferred",
                    "last_four": "4242",
                    "color": "blue"
                },
                "mastercard": {
                    "brand": "mastercard", 
                    "name": "Capital One Venture",
                    "last_four": "5555",
                    "color": "red"
                },
                "amex": {
                    "brand": "amex",
                    "name": "American Express Gold",
                    "last_four": "1005",
                    "color": "green"
                },
                "discover": {
                    "brand": "discover",
                    "name": "Discover it Cash Back",
                    "last_four": "1117",
                    "color": "orange"
                }
            }
            
            config = brand_configs.get(card_brand, brand_configs["visa"])
            
            # Generate realistic credit card data
            balance = random.randint(50000, 500000)  # $500 - $5000 in cents
            credit_limit = balance + random.randint(100000, 1000000)  # Additional available credit
            minimum_payment = max(2500, int(balance * 0.02))  # At least $25 or 2% of balance
            
            # Generate due date (15-45 days from now)
            due_date = datetime.now() + timedelta(days=random.randint(15, 45))
            last_payment_date = datetime.now() - timedelta(days=random.randint(5, 30))
            
            simulated_credit_card = {
                "id": account_id,
                "entity_id": entity_id,
                "type": "liability",
                "brand": config["brand"],
                "last_four": config["last_four"],
                "name": config["name"],
                "status": "active",
                "balance": balance,
                "exp_month": random.randint(1, 12),
                "exp_year": datetime.now().year + random.randint(1, 5),
                "liability": {
                    "mch": config["last_four"],
                    "mask": config["last_four"],
                    "name": config["name"],
                    "type": "credit_card",
                    "balance": balance,
                    "credit_limit": credit_limit,
                    "available_credit": credit_limit - balance,
                    "last_payment_date": last_payment_date.isoformat(),
                    "last_payment_amount": random.randint(5000, minimum_payment),
                    "next_payment_due_date": due_date.isoformat(),
                    "next_payment_minimum_amount": minimum_payment,
                    "apr": round(random.uniform(15.99, 29.99), 2),
                    "statement_balance": balance
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": datetime.now().isoformat()
            }
            
            # Add simulation metadata
            simulated_credit_card["_simulation"] = True
            simulated_credit_card["_simulation_note"] = f"This is a simulated {config['brand']} credit card for development testing"
            
            # Store in simulated accounts for retrieval
            if entity_id not in _simulated_accounts:
                _simulated_accounts[entity_id] = []
            _simulated_accounts[entity_id].append(simulated_credit_card)
            
            return simulated_credit_card
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate credit card connection: {str(e)}")
    
    async def simulate_multiple_credit_cards(self, entity_id: str) -> Dict[str, Any]:
        """
        Simulate connecting multiple credit cards for comprehensive testing
        
        Args:
            entity_id: Method entity ID
            
        Returns:
            List of simulated credit cards
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            cards = []
            brands = ["visa", "mastercard", "amex", "discover"]
            
            # Create 2-3 credit cards with different brands
            for brand in brands[:3]:  # Create 3 cards
                credit_card = await self.simulate_credit_card_connection(entity_id, brand)
                cards.append(credit_card)
            
            return {
                "cards": cards,
                "total": len(cards),
                "_simulation": True,
                "_simulation_note": "These are simulated credit cards for development testing"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate multiple credit cards: {str(e)}")
    
    async def simulate_create_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate creating a transaction (dev environment only)
        
        Args:
            transaction_data: Transaction data
            
        Returns:
            Method transaction object
        """
        if self.environment != "dev":
            raise HTTPException(
                status_code=403,
                detail="Simulation endpoints are only available in development environment"
            )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/simulate/transactions",
                    json=transaction_data,
                    headers=self._get_headers()
                )
                
                if response.status_code == 201:
                    return response.json()
                else:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Method API error: {response.text}"
                    )
                    
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Failed to connect to Method API: {str(e)}")
    
    async def simulate_credit_card_connection(self, entity_id: str, card_brand: str = "visa") -> Dict[str, Any]:
        """
        Simulate connecting a credit card (dev environment only)
        
        This bypasses Method Connect and creates a simulated credit card
        that can be used for payments in the dev environment.
        
        Args:
            entity_id: Method entity ID
            card_brand: Brand of credit card (visa, mastercard, amex, discover)
            
        Returns:
            Simulated credit card data
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            import uuid
            import random
            from datetime import datetime, timedelta
            
            account_id = f"acc_cc_{str(uuid.uuid4())[:8]}"
            
            # Define card brand specifics
            brand_configs = {
                "visa": {
                    "brand": "visa",
                    "name": "Chase Sapphire Preferred",
                    "last_four": "4242",
                    "color": "blue"
                },
                "mastercard": {
                    "brand": "mastercard", 
                    "name": "Capital One Venture",
                    "last_four": "5555",
                    "color": "red"
                },
                "amex": {
                    "brand": "amex",
                    "name": "American Express Gold",
                    "last_four": "1005",
                    "color": "green"
                },
                "discover": {
                    "brand": "discover",
                    "name": "Discover it Cash Back",
                    "last_four": "1117",
                    "color": "orange"
                }
            }
            
            config = brand_configs.get(card_brand, brand_configs["visa"])
            
            # Generate realistic credit card data
            balance = random.randint(50000, 500000)  # $500 - $5000 in cents
            credit_limit = balance + random.randint(100000, 1000000)  # Additional available credit
            minimum_payment = max(2500, int(balance * 0.02))  # At least $25 or 2% of balance
            
            # Generate due date (15-45 days from now)
            due_date = datetime.now() + timedelta(days=random.randint(15, 45))
            last_payment_date = datetime.now() - timedelta(days=random.randint(5, 30))
            
            simulated_credit_card = {
                "id": account_id,
                "entity_id": entity_id,
                "type": "liability",
                "brand": config["brand"],
                "last_four": config["last_four"],
                "name": config["name"],
                "status": "active",
                "balance": balance,
                "exp_month": random.randint(1, 12),
                "exp_year": datetime.now().year + random.randint(1, 5),
                "liability": {
                    "mch": config["last_four"],
                    "mask": config["last_four"],
                    "name": config["name"],
                    "type": "credit_card",
                    "balance": balance,
                    "credit_limit": credit_limit,
                    "available_credit": credit_limit - balance,
                    "last_payment_date": last_payment_date.isoformat(),
                    "last_payment_amount": random.randint(5000, minimum_payment),
                    "next_payment_due_date": due_date.isoformat(),
                    "next_payment_minimum_amount": minimum_payment,
                    "apr": round(random.uniform(15.99, 29.99), 2),
                    "statement_balance": balance
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": datetime.now().isoformat()
            }
            
            # Add simulation metadata
            simulated_credit_card["_simulation"] = True
            simulated_credit_card["_simulation_note"] = f"This is a simulated {config['brand']} credit card for development testing"
            
            # Store in simulated accounts for retrieval
            if entity_id not in _simulated_accounts:
                _simulated_accounts[entity_id] = []
            _simulated_accounts[entity_id].append(simulated_credit_card)
            
            return simulated_credit_card
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate credit card connection: {str(e)}")
    
    async def simulate_multiple_credit_cards(self, entity_id: str) -> Dict[str, Any]:
        """
        Simulate connecting multiple credit cards for comprehensive testing
        
        Args:
            entity_id: Method entity ID
            
        Returns:
            List of simulated credit cards
        """
        if self.environment != "dev":
            raise HTTPException(status_code=403, detail="Simulation endpoints only available in dev environment")
        
        try:
            cards = []
            brands = ["visa", "mastercard", "amex", "discover"]
            
            # Create 2-3 credit cards with different brands
            for brand in brands[:3]:  # Create 3 cards
                credit_card = await self.simulate_credit_card_connection(entity_id, brand)
                cards.append(credit_card)
            
            return {
                "cards": cards,
                "total": len(cards),
                "_simulation": True,
                "_simulation_note": "These are simulated credit cards for development testing"
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to simulate multiple credit cards: {str(e)}")
