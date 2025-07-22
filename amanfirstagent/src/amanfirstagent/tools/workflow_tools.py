"""
Specialized tools for agentic workflow automation
"""

import json
import requests
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

try:
    from utils.logger import setup_logger, log_api_call
    from utils.security import SecurityManager
except ImportError:
    # Fallback for when running from different directory
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
    try:
        from utils.logger import setup_logger, log_api_call
        from utils.security import SecurityManager
    except ImportError:
        # Create basic logger if utils not available
        import logging
        def setup_logger(name):
            logger = logging.getLogger(name)
            logger.setLevel(logging.INFO)
            if not logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                handler.setFormatter(formatter)
                logger.addHandler(handler)
            return logger
        
        def log_api_call(logger, service, url, status_code, response_time):
            logger.info(f"API call to {service}: {url} - {status_code} ({response_time}s)")
        
        class SecurityManager:
            def validate_message(self, message):
                return True
            def mask_sensitive_data(self, data):
                return data[:4] + "***" if len(data) > 4 else "***"

class TripAPITool(BaseTool):
    name: str = "trip_api"
    description: str = "Create and manage trips using external API"
    
    def __init__(self):
        super().__init__()
        self.logger = setup_logger("trip_api_tool")
        self.security_manager = SecurityManager()
        try:
            from config import get_config
            self.config = get_config()
        except ImportError:
            try:
                from amanfirstagent.config.config import get_config
                self.config = get_config()
            except ImportError:
                # Create a mock config
                class MockConfig:
                    def __init__(self):
                        self.api = type('obj', (object,), {
                            'trip_api_url': None,
                            'api_authentication_token': None
                        })
                self.config = MockConfig()
    
    def _run(self, action: str, trip_data: Dict = None, trip_id: str = None) -> str:
        """
        Perform trip-related operations
        
        Args:
            action: Action to perform (create, get, update, delete)
            trip_data: Trip data for creation/updates
            trip_id: Trip ID for get/update/delete operations
        """
        try:
            if action == "create":
                return self._create_trip(trip_data or {})
            elif action == "get":
                return self._get_trip(trip_id)
            elif action == "update":
                return self._update_trip(trip_id, trip_data or {})
            elif action == "delete":
                return self._delete_trip(trip_id)
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Unknown action: {action}"
                })
                
        except Exception as e:
            self.logger.error(f"Trip API operation failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    def _create_trip(self, trip_data: Dict) -> str:
        """Create a new trip"""
        # Validate trip data
        required_fields = ["destination", "start_date", "end_date", "travelers"]
        for field in required_fields:
            if field not in trip_data:
                return json.dumps({
                    "success": False,
                    "error": f"Missing required field: {field}"
                })
        
        # Security validation
        for key, value in trip_data.items():
            if isinstance(value, str) and not self.security_manager.validate_message(value):
                return json.dumps({
                    "success": False,
                    "error": f"Invalid content in field: {key}"
                })
        
        # Prepare API payload
        payload = {
            "destination": trip_data.get("destination"),
            "start_date": trip_data.get("start_date"),
            "end_date": trip_data.get("end_date"),
            "travelers": trip_data.get("travelers"),
            "budget": trip_data.get("budget"),
            "preferences": trip_data.get("preferences", {}),
            "user_id": trip_data.get("user_id"),
            "created_via": "agentic_workflow"
        }
        
        # If API URL is configured, make real API call
        if self.config.api.trip_api_url:
            try:
                api_tool = APIIntegrationTool()
                result = api_tool._run(
                    url=self.config.api.trip_api_url,
                    method="POST",
                    headers={
                        "Authorization": f"Bearer {self.config.api.api_authentication_token}",
                        "Content-Type": "application/json"
                    },
                    data=payload
                )
                return result
            except Exception as e:
                self.logger.error(f"API call failed: {e}")
                return json.dumps({
                    "success": False,
                    "error": f"API call failed: {str(e)}"
                })
        else:
            # Simulate trip creation
            trip_id = f"trip_{hash(str(payload)) % 100000}"
            return json.dumps({
                "success": True,
                "trip_id": trip_id,
                "message": "Trip created successfully",
                "trip_details": payload,
                "confirmation_code": f"CONF{hash(str(payload)) % 10000}",
                "estimated_total": payload.get("budget", 0),
                "api_note": "Simulated - configure TRIP_API_URL for real API calls"
            })
    
    def _get_trip(self, trip_id: str) -> str:
        """Get trip details"""
        if not trip_id:
            return json.dumps({
                "success": False,
                "error": "Trip ID is required"
            })
        
        # Simulate trip retrieval
        return json.dumps({
            "success": True,
            "trip_id": trip_id,
            "trip_details": {
                "destination": "Sample Destination",
                "start_date": "2025-08-01",
                "end_date": "2025-08-07",
                "travelers": 2,
                "status": "confirmed"
            },
            "api_note": "Simulated - configure TRIP_API_URL for real API calls"
        })
    
    def _update_trip(self, trip_id: str, update_data: Dict) -> str:
        """Update trip details"""
        if not trip_id:
            return json.dumps({
                "success": False,
                "error": "Trip ID is required"
            })
        
        return json.dumps({
            "success": True,
            "trip_id": trip_id,
            "updated_fields": list(update_data.keys()),
            "message": "Trip updated successfully",
            "api_note": "Simulated - configure TRIP_API_URL for real API calls"
        })
    
    def _delete_trip(self, trip_id: str) -> str:
        """Delete/cancel a trip"""
        if not trip_id:
            return json.dumps({
                "success": False,
                "error": "Trip ID is required"
            })
        
        return json.dumps({
            "success": True,
            "trip_id": trip_id,
            "message": "Trip cancelled successfully",
            "api_note": "Simulated - configure TRIP_API_URL for real API calls"
        })

class APIIntegrationTool(BaseTool):
    name: str = "api_integration"
    description: str = "Make HTTP requests to external APIs"
    
    def __init__(self):
        super().__init__()
        self.logger = setup_logger("api_tool")
        self.security_manager = SecurityManager()
    
    def _run(self, url: str, method: str = "GET", headers: Dict = None, 
             data: Dict = None, timeout: int = 30) -> str:
        """
        Make HTTP request to external API
        
        Args:
            url: API endpoint URL
            method: HTTP method (GET, POST, PUT, DELETE)
            headers: Request headers
            data: Request payload
            timeout: Request timeout in seconds
        """
        start_time = datetime.now()
        
        try:
            # Security validation
            if not self.security_manager.validate_message(url):
                return json.dumps({
                    "success": False,
                    "error": "URL contains potentially unsafe content"
                })
            
            # Default headers
            if not headers:
                headers = {'Content-Type': 'application/json'}
            
            # Make request
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                json=data if data else None,
                timeout=timeout
            )
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Log API call
            log_api_call(
                self.logger, 
                "external_api", 
                url, 
                response.status_code, 
                response_time
            )
            
            # Process response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = response.text
            
            return json.dumps({
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response_data": response_data,
                "response_time": response_time
            })
            
        except requests.exceptions.Timeout:
            return json.dumps({
                "success": False,
                "error": "Request timed out"
            })
        except requests.exceptions.ConnectionError:
            return json.dumps({
                "success": False,
                "error": "Connection error"
            })
        except Exception as e:
            self.logger.error(f"API request failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class DataValidationTool(BaseTool):
    name: str = "data_validation"
    description: str = "Validate data formats, types, and business rules"
    
    def __init__(self):
        super().__init__()
        self.logger = setup_logger("validation_tool")
    
    def _run(self, data: Dict, validation_rules: Dict) -> str:
        """
        Validate data against specified rules
        
        Args:
            data: Data to validate
            validation_rules: Validation rules to apply
        """
        try:
            validation_results = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            # Required fields validation
            required_fields = validation_rules.get("required_fields", [])
            for field in required_fields:
                if field not in data or not data[field]:
                    validation_results["valid"] = False
                    validation_results["errors"].append(f"Required field '{field}' is missing or empty")
            
            # Data type validation
            field_types = validation_rules.get("field_types", {})
            for field, expected_type in field_types.items():
                if field in data:
                    if expected_type == "email":
                        if not self._validate_email(data[field]):
                            validation_results["valid"] = False
                            validation_results["errors"].append(f"Invalid email format for field '{field}'")
                    elif expected_type == "phone":
                        if not self._validate_phone(data[field]):
                            validation_results["valid"] = False
                            validation_results["errors"].append(f"Invalid phone format for field '{field}'")
                    elif expected_type == "number":
                        try:
                            float(data[field])
                        except (ValueError, TypeError):
                            validation_results["valid"] = False
                            validation_results["errors"].append(f"Field '{field}' must be a number")
            
            # Business rules validation
            business_rules = validation_rules.get("business_rules", [])
            for rule in business_rules:
                rule_type = rule.get("type")
                field = rule.get("field")
                
                if rule_type == "min_value" and field in data:
                    try:
                        value = float(data[field])
                        min_val = float(rule.get("value", 0))
                        if value < min_val:
                            validation_results["warnings"].append(f"Field '{field}' value is below recommended minimum of {min_val}")
                    except (ValueError, TypeError):
                        pass
                
                elif rule_type == "max_length" and field in data:
                    max_len = rule.get("value", 255)
                    if len(str(data[field])) > max_len:
                        validation_results["valid"] = False
                        validation_results["errors"].append(f"Field '{field}' exceeds maximum length of {max_len}")
            
            return json.dumps(validation_results)
            
        except Exception as e:
            self.logger.error(f"Data validation failed: {e}")
            return json.dumps({
                "valid": False,
                "errors": [f"Validation error: {str(e)}"]
            })
    
    def _validate_email(self, email: str) -> bool:
        """Simple email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(email)))
    
    def _validate_phone(self, phone: str) -> bool:
        """Simple phone validation"""
        import re
        # Remove non-digit characters
        digits = re.sub(r'\D', '', str(phone))
        # Check if it's 10 or 11 digits (US format)
        return len(digits) in [10, 11]

class FileOperationTool(BaseTool):
    name: str = "file_operations"
    description: str = "Handle file operations like reading, writing, and processing"
    
    def __init__(self):
        super().__init__()
        self.logger = setup_logger("file_tool")
        self.security_manager = SecurityManager()
    
    def _run(self, operation: str, file_path: str = None, 
             content: str = None, format: str = "txt") -> str:
        """
        Perform file operations
        
        Args:
            operation: Operation type (read, write, create, delete)
            file_path: Path to file
            content: Content to write (for write operations)
            format: File format (txt, json, csv)
        """
        try:
            # Security validation
            if file_path and not self.security_manager.validate_message(file_path):
                return json.dumps({
                    "success": False,
                    "error": "File path contains potentially unsafe content"
                })
            
            # For demonstration, simulate file operations
            if operation == "read":
                # Simulate reading a file
                sample_content = self._get_sample_file_content(format)
                return json.dumps({
                    "success": True,
                    "operation": "read",
                    "content": sample_content,
                    "format": format
                })
            
            elif operation == "write":
                # Simulate writing to a file
                return json.dumps({
                    "success": True,
                    "operation": "write",
                    "file_path": file_path or "simulated_file.txt",
                    "bytes_written": len(content or ""),
                    "format": format
                })
            
            elif operation == "create":
                # Simulate creating a file
                return json.dumps({
                    "success": True,
                    "operation": "create",
                    "file_path": file_path or "new_file.txt",
                    "created_at": datetime.now().isoformat()
                })
            
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Unsupported operation: {operation}"
                })
                
        except Exception as e:
            self.logger.error(f"File operation failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    def _get_sample_file_content(self, format: str) -> str:
        """Generate sample file content for demonstration"""
        if format == "json":
            return json.dumps({
                "sample_data": True,
                "timestamp": datetime.now().isoformat(),
                "records": [
                    {"id": 1, "name": "Sample Record 1"},
                    {"id": 2, "name": "Sample Record 2"}
                ]
            })
        elif format == "csv":
            return "id,name,email\n1,John Doe,john@example.com\n2,Jane Smith,jane@example.com"
        else:
            return "This is sample file content for demonstration purposes."

class TruckSearchTool(BaseTool):
    name: str = "truck_search"
    description: str = "Search for available trucks from point A to point B"
    
    def __init__(self):
        super().__init__()
        self.logger = setup_logger("truck_search_tool")
        try:
            self.security_manager = SecurityManager()
        except Exception:
            self.security_manager = None
    
    def _run(self, pickup_location: str, delivery_location: str, 
             date: str = None, truck_type: str = None) -> str:
        """
        Search for available trucks
        
        Args:
            pickup_location: Pickup location
            delivery_location: Delivery location
            date: Preferred date (optional)
            truck_type: Type of truck needed (optional)
        """
        try:
            # Security validation
            if self.security_manager:
                for location in [pickup_location, delivery_location]:
                    if not self.security_manager.validate_message(location):
                        return json.dumps({
                            "success": False,
                            "error": "Location contains potentially unsafe content"
                        })
            
            # Simulate truck search results
            trucks = [
                {
                    "truck_id": "TRK001",
                    "owner_name": "ABC Transport",
                    "contact": "+91-9876543210",
                    "truck_type": "Medium Truck",
                    "capacity": "5 tons",
                    "price_per_km": 25,
                    "estimated_total": 2500,
                    "rating": 4.5,
                    "location": pickup_location,
                    "availability": "Available"
                },
                {
                    "truck_id": "TRK002", 
                    "owner_name": "XYZ Logistics",
                    "contact": "+91-9876543211",
                    "truck_type": "Large Truck",
                    "capacity": "10 tons",
                    "price_per_km": 35,
                    "estimated_total": 3500,
                    "rating": 4.2,
                    "location": pickup_location,
                    "availability": "Available"
                },
                {
                    "truck_id": "TRK003",
                    "owner_name": "PQR Transport",
                    "contact": "+91-9876543212", 
                    "truck_type": "Small Truck",
                    "capacity": "2 tons",
                    "price_per_km": 18,
                    "estimated_total": 1800,
                    "rating": 4.8,
                    "location": pickup_location,
                    "availability": "Available"
                }
            ]
            
            # Filter by truck type if specified
            if truck_type:
                trucks = [t for t in trucks if truck_type.lower() in t["truck_type"].lower()]
            
            return json.dumps({
                "success": True,
                "pickup_location": pickup_location,
                "delivery_location": delivery_location,
                "date": date or datetime.now().strftime("%Y-%m-%d"),
                "available_trucks": trucks,
                "total_found": len(trucks)
            })
            
        except Exception as e:
            self.logger.error(f"Truck search failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class TripDetailCollectorTool(BaseTool):
    name: str = "trip_detail_collector"
    description: str = "Collect detailed trip information from user"
    
    def __init__(self):
        super().__init__()
        self.logger = setup_logger("trip_collector_tool")
        try:
            self.security_manager = SecurityManager()
        except Exception:
            self.security_manager = None
    
    def _run(self, truck_id: str, consigner_name: str = None, consignee_name: str = None,
             pickup_address: str = None, delivery_address: str = None,
             parcel_size: str = None, parcel_weight: str = None, 
             parcel_value: str = None, special_instructions: str = None) -> str:
        """
        Collect and validate trip details
        
        Args:
            truck_id: Selected truck ID
            consigner_name: Person sending the parcel
            consignee_name: Person receiving the parcel  
            pickup_address: Complete pickup address
            delivery_address: Complete delivery address
            parcel_size: Size/dimensions of parcel
            parcel_weight: Weight of parcel
            parcel_value: Declared value of parcel
            special_instructions: Any special handling instructions
        """
        try:
            # Collect the provided details
            trip_details = {
                "truck_id": truck_id,
                "consigner_name": consigner_name,
                "consignee_name": consignee_name,
                "pickup_address": pickup_address,
                "delivery_address": delivery_address,
                "parcel_size": parcel_size,
                "parcel_weight": parcel_weight,
                "parcel_value": parcel_value,
                "special_instructions": special_instructions,
                "created_at": datetime.now().isoformat()
            }
            
            # Identify missing required fields
            required_fields = [
                "consigner_name", "consignee_name", "pickup_address", 
                "delivery_address", "parcel_size", "parcel_weight"
            ]
            
            missing_fields = []
            for field in required_fields:
                if not trip_details.get(field):
                    missing_fields.append(field)
            
            # Security validation for provided fields
            if self.security_manager:
                for field, value in trip_details.items():
                    if value and isinstance(value, str):
                        if not self.security_manager.validate_message(value):
                            return json.dumps({
                                "success": False,
                                "error": f"Invalid content in field: {field}"
                            })
            
            # Return result
            result = {
                "success": len(missing_fields) == 0,
                "trip_details": {k: v for k, v in trip_details.items() if v is not None},
                "missing_fields": missing_fields
            }
            
            if missing_fields:
                result["message"] = f"Please provide the following required information: {', '.join(missing_fields)}"
            else:
                result["message"] = "All trip details collected successfully"
                result["ready_for_verification"] = True
            
            return json.dumps(result)
            
        except Exception as e:
            self.logger.error(f"Trip detail collection failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class TruckOwnerContactTool(BaseTool):
    name: str = "truck_owner_contact"
    description: str = "Contact truck owner to verify availability"
    
    def __init__(self):
        super().__init__()
        self.logger = setup_logger("truck_contact_tool")
        try:
            self.security_manager = SecurityManager()
        except Exception:
            self.security_manager = None
    
    def _run(self, truck_id: str, owner_contact: str, trip_details: Dict = None,
             message_type: str = "availability_check") -> str:
        """
        Contact truck owner for availability verification
        
        Args:
            truck_id: Truck ID to verify
            owner_contact: Owner contact information
            trip_details: Trip details for booking
            message_type: Type of message (availability_check, booking_confirm)
        """
        try:
            # Simulate contacting truck owner
            import random
            
            # 80% chance of availability for simulation
            is_available = random.random() > 0.2
            
            contact_result = {
                "success": True,
                "truck_id": truck_id,
                "owner_contact": self.security_manager.mask_sensitive_data(owner_contact) if self.security_manager else owner_contact[:4] + "***",
                "contacted_at": datetime.now().isoformat(),
                "message_type": message_type,
                "response_time": f"{random.randint(30, 300)} seconds"
            }
            
            if message_type == "availability_check":
                contact_result.update({
                    "availability_status": "available" if is_available else "not_available",
                    "owner_response": "Truck is available for the requested dates" if is_available 
                                    else "Truck is not available for the requested dates",
                    "next_available_date": None if is_available else 
                                         datetime.now().strftime("%Y-%m-%d")
                })
                
                if is_available and trip_details:
                    contact_result["booking_confirmed"] = True
                    contact_result["booking_reference"] = f"BK{random.randint(10000, 99999)}"
                
            elif message_type == "booking_confirm":
                contact_result.update({
                    "booking_status": "confirmed" if is_available else "declined",
                    "confirmation_code": f"CONF{random.randint(1000, 9999)}" if is_available else None
                })
            
            self.logger.info(f"Contacted truck owner for {truck_id}: {'Available' if is_available else 'Not Available'}")
            
            return json.dumps(contact_result)
            
        except Exception as e:
            self.logger.error(f"Truck owner contact failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class BiltyGeneratorTool(BaseTool):
    name: str = "bilty_generator"
    description: str = "Generate bilty (waybill) for truck bookings"
    
    def __init__(self):
        super().__init__()
        self.logger = setup_logger("bilty_generator_tool")
    
    def _run(self, booking_details: Dict, truck_details: Dict, pricing_details: Dict = None) -> str:
        """
        Generate bilty for confirmed booking
        
        Args:
            booking_details: Trip and customer information
            truck_details: Truck and driver information  
            pricing_details: Pricing breakdown (optional)
        """
        try:
            import random
            from datetime import datetime, timedelta
            
            # Generate bilty number
            bilty_number = f"BLT{random.randint(100000, 999999)}"
            
            # Calculate pricing if not provided
            if not pricing_details:
                base_rate = truck_details.get('price_per_km', 25)
                estimated_km = 100  # Default distance
                pricing_details = {
                    "base_fare": base_rate * estimated_km,
                    "loading_charges": 500,
                    "tax_gst": 0,
                    "total_amount": (base_rate * estimated_km) + 500
                }
                pricing_details["tax_gst"] = pricing_details["total_amount"] * 0.18
                pricing_details["total_amount"] += pricing_details["tax_gst"]
            
            # Generate bilty
            bilty = {
                "bilty_number": bilty_number,
                "generated_date": datetime.now().isoformat(),
                "booking_reference": booking_details.get("booking_reference", ""),
                
                # Trip Details
                "consigner": {
                    "name": booking_details.get("consigner_name", ""),
                    "address": booking_details.get("pickup_address", ""),
                    "contact": booking_details.get("consigner_contact", "")
                },
                "consignee": {
                    "name": booking_details.get("consignee_name", ""),
                    "address": booking_details.get("delivery_address", ""),
                    "contact": booking_details.get("consignee_contact", "")
                },
                
                # Parcel Details
                "parcel_details": {
                    "description": booking_details.get("parcel_description", "General Goods"),
                    "weight": booking_details.get("parcel_weight", ""),
                    "size": booking_details.get("parcel_size", ""),
                    "value": booking_details.get("parcel_value", ""),
                    "quantity": booking_details.get("quantity", "1 Lot")
                },
                
                # Truck Details
                "truck_details": {
                    "truck_id": truck_details.get("truck_id", ""),
                    "truck_number": truck_details.get("truck_number", "TBD"),
                    "driver_name": truck_details.get("driver_name", "TBD"),
                    "driver_contact": truck_details.get("driver_contact", "TBD"),
                    "truck_type": truck_details.get("truck_type", ""),
                    "capacity": truck_details.get("capacity", "")
                },
                
                # Pricing
                "pricing": pricing_details,
                
                # Terms and Conditions
                "terms": [
                    "Goods dispatched at owner's risk",
                    "Company is not responsible for damages due to natural causes",
                    "Delivery subject to local conditions and restrictions",
                    "Payment due on delivery",
                    "Any disputes subject to local jurisdiction"
                ],
                
                # Status
                "status": "Generated",
                "created_by": "System",
                "valid_until": (datetime.now() + timedelta(days=30)).isoformat()
            }
            
            self.logger.info(f"Bilty generated: {bilty_number}")
            
            return json.dumps({
                "success": True,
                "bilty": bilty,
                "message": f"Bilty {bilty_number} generated successfully"
            })
            
        except Exception as e:
            self.logger.error(f"Bilty generation failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class DocumentUploadTool(BaseTool):
    name: str = "document_upload"
    description: str = "Handle document uploads from users and drivers"
    
    def __init__(self):
        super().__init__()
        self.logger = setup_logger("document_upload_tool")
        try:
            self.security_manager = SecurityManager()
        except Exception:
            self.security_manager = None
    
    def _run(self, user_type: str, document_type: str, file_path: str = None, 
             file_data: str = None, booking_reference: str = None) -> str:
        """
        Handle document upload and verification
        
        Args:
            user_type: 'customer' or 'driver'
            document_type: Type of document (id_proof, parcel_photo, driver_license, etc.)
            file_path: Path to uploaded file (optional)
            file_data: Base64 encoded file data (optional)
            booking_reference: Associated booking reference
        """
        try:
            import random
            from datetime import datetime
            
            # Document type validation
            valid_customer_docs = ['id_proof', 'parcel_photo', 'address_proof', 'invoice']
            valid_driver_docs = ['driver_license', 'vehicle_registration', 'insurance', 'pollution_cert']
            
            if user_type == 'customer' and document_type not in valid_customer_docs:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid document type. Valid types: {valid_customer_docs}"
                })
            
            if user_type == 'driver' and document_type not in valid_driver_docs:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid document type. Valid types: {valid_driver_docs}"
                })
            
            # Generate document ID
            doc_id = f"DOC{random.randint(10000, 99999)}"
            
            # Simulate file validation
            file_size = random.randint(100, 2048)  # KB
            is_valid = random.choice([True, True, True, False])  # 75% success rate
            
            upload_result = {
                "success": is_valid,
                "document_id": doc_id,
                "user_type": user_type,
                "document_type": document_type,
                "booking_reference": booking_reference,
                "uploaded_at": datetime.now().isoformat(),
                "file_size_kb": file_size,
                "status": "verified" if is_valid else "rejected"
            }
            
            if is_valid:
                upload_result.update({
                    "verification_notes": "Document successfully verified",
                    "storage_path": f"uploads/{user_type}/{doc_id}_{document_type}.pdf"
                })
            else:
                upload_result.update({
                    "rejection_reason": "Document unclear or invalid format",
                    "retry_required": True
                })
            
            self.logger.info(f"Document upload: {doc_id} - {upload_result['status']}")
            
            return json.dumps(upload_result)
            
        except Exception as e:
            self.logger.error(f"Document upload failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class TripStatusTrackerTool(BaseTool):
    name: str = "trip_status_tracker"
    description: str = "Track and update trip status from booking to delivery"
    
    def __init__(self):
        super().__init__()
        self.logger = setup_logger("trip_status_tool")
    
    def _run(self, action: str, booking_reference: str, new_status: str = None, 
             location: str = None, notes: str = None, driver_id: str = None) -> str:
        """
        Track trip status changes
        
        Args:
            action: 'update_status', 'get_status', 'get_history'
            booking_reference: Booking reference number
            new_status: New status to set
            location: Current location (for tracking)
            notes: Additional notes
            driver_id: Driver ID for verification
        """
        try:
            from datetime import datetime
            import random
            
            # Define valid statuses and transitions
            valid_statuses = [
                "Booked",
                "Documents Pending", 
                "Documents Verified",
                "Driver Assigned",
                "Pickup Scheduled",
                "In Transit",
                "Delivered",
                "Completed",
                "Cancelled"
            ]
            
            if action == "update_status":
                if new_status not in valid_statuses:
                    return json.dumps({
                        "success": False,
                        "error": f"Invalid status. Valid statuses: {valid_statuses}"
                    })
                
                # Simulate status update
                update_result = {
                    "success": True,
                    "booking_reference": booking_reference,
                    "previous_status": "Booked",  # Would come from database
                    "new_status": new_status,
                    "updated_at": datetime.now().isoformat(),
                    "location": location or "Unknown",
                    "notes": notes or "",
                    "updated_by": driver_id or "System"
                }
                
                # Add estimated delivery if in transit
                if new_status == "In Transit":
                    from datetime import timedelta
                    eta = datetime.now() + timedelta(hours=random.randint(4, 12))
                    update_result["estimated_delivery"] = eta.isoformat()
                
                self.logger.info(f"Status updated: {booking_reference} -> {new_status}")
                return json.dumps(update_result)
            
            elif action == "get_status":
                # Simulate current status retrieval
                current_status = {
                    "booking_reference": booking_reference,
                    "current_status": "In Transit",
                    "last_updated": datetime.now().isoformat(),
                    "current_location": "Highway NH-8, near Gurgaon",
                    "estimated_delivery": "2025-07-23T14:30:00",
                    "driver_contact": "+91-9876543210",
                    "tracking_url": f"https://track.example.com/{booking_reference}"
                }
                
                return json.dumps(current_status)
            
            elif action == "get_history":
                # Simulate status history
                history = {
                    "booking_reference": booking_reference,
                    "status_history": [
                        {
                            "status": "Booked",
                            "timestamp": "2025-07-22T10:00:00",
                            "location": "Mumbai",
                            "notes": "Booking confirmed"
                        },
                        {
                            "status": "Documents Verified", 
                            "timestamp": "2025-07-22T11:30:00",
                            "location": "Mumbai",
                            "notes": "All documents verified"
                        },
                        {
                            "status": "Driver Assigned",
                            "timestamp": "2025-07-22T12:00:00", 
                            "location": "Mumbai",
                            "notes": "Driver: Rajesh Kumar (+91-9876543210)"
                        },
                        {
                            "status": "In Transit",
                            "timestamp": "2025-07-22T14:00:00",
                            "location": "Highway NH-8",
                            "notes": "Departed from pickup location"
                        }
                    ]
                }
                
                return json.dumps(history)
            
            else:
                return json.dumps({
                    "success": False,
                    "error": f"Invalid action: {action}. Valid actions: update_status, get_status, get_history"
                })
                
        except Exception as e:
            self.logger.error(f"Trip status tracking failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class DriverVerificationTool(BaseTool):
    name: str = "driver_verification"
    description: str = "Verify driver documents and credentials"
    
    def __init__(self):
        super().__init__()
        self.logger = setup_logger("driver_verification_tool")
    
    def _run(self, driver_id: str, document_ids: List[str], booking_reference: str) -> str:
        """
        Verify driver documents and credentials
        
        Args:
            driver_id: Driver identifier
            document_ids: List of uploaded document IDs to verify
            booking_reference: Associated booking reference
        """
        try:
            import random
            from datetime import datetime, timedelta
            
            # Simulate document verification process
            verification_results = []
            
            for doc_id in document_ids:
                # Random verification result (90% pass rate)
                is_verified = random.random() > 0.1
                
                result = {
                    "document_id": doc_id,
                    "verified": is_verified,
                    "verification_date": datetime.now().isoformat(),
                    "notes": "Document verified successfully" if is_verified else "Document requires resubmission"
                }
                
                if not is_verified:
                    result["rejection_reason"] = random.choice([
                        "Document expired",
                        "Image quality poor",
                        "Information mismatch",
                        "Invalid document type"
                    ])
                
                verification_results.append(result)
            
            # Overall verification status
            all_verified = all(result["verified"] for result in verification_results)
            
            driver_verification = {
                "success": True,
                "driver_id": driver_id,
                "booking_reference": booking_reference,
                "overall_status": "verified" if all_verified else "pending",
                "verification_date": datetime.now().isoformat(),
                "document_results": verification_results,
                "documents_verified": sum(1 for r in verification_results if r["verified"]),
                "total_documents": len(verification_results)
            }
            
            if all_verified:
                driver_verification.update({
                    "driver_approved": True,
                    "approval_valid_until": (datetime.now() + timedelta(days=365)).isoformat(),
                    "next_action": "Assign to booking and schedule pickup"
                })
            else:
                driver_verification.update({
                    "driver_approved": False,
                    "required_actions": [
                        "Resubmit rejected documents",
                        "Wait for verification completion"
                    ]
                })
            
            self.logger.info(f"Driver verification: {driver_id} - {driver_verification['overall_status']}")
            
            return json.dumps(driver_verification)
            
        except Exception as e:
            self.logger.error(f"Driver verification failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })

class NotificationTool(BaseTool):
    name: str = "notification"
    description: str = "Send notifications via various channels"
    
    def __init__(self):
        super().__init__()
        self.logger = setup_logger("notification_tool")
        try:
            self.security_manager = SecurityManager()
        except Exception:
            self.security_manager = None
    
    def _run(self, channel: str, recipient: str, message: str, 
             subject: str = None, priority: str = "normal") -> str:
        """
        Send notification
        
        Args:
            channel: Notification channel (email, slack, sms, webhook)
            recipient: Recipient identifier
            message: Notification message
            subject: Message subject (for email)
            priority: Priority level (low, normal, high, urgent)
        """
        try:
            # For demonstration, simulate sending notifications
            notification_result = {
                "success": True,
                "channel": channel,
                "recipient": self.security_manager.mask_sensitive_data(recipient) if self.security_manager else recipient[:4] + "***",
                "message_id": f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "priority": priority
            }
            
            if channel == "email":
                notification_result["subject"] = subject or "Workflow Notification"
                
            elif channel == "slack":
                notification_result["workspace"] = "simulated_workspace"
                
            elif channel == "sms":
                notification_result["carrier"] = "simulated_carrier"
                
            elif channel == "webhook":
                notification_result["endpoint"] = recipient
                notification_result["http_method"] = "POST"
            
            self.logger.info(f"Notification sent via {channel} to {recipient[:10]}...")
            
            return json.dumps(notification_result)
            
        except Exception as e:
            self.logger.error(f"Notification failed: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })