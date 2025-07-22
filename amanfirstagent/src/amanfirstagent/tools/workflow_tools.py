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

from utils.logger import setup_logger, log_api_call
from utils.security import SecurityManager

class TripAPITool(BaseTool):
    name: str = "trip_api"
    description: str = "Create and manage trips using external API"
    
    def __init__(self):
        super().__init__()
        self.logger = setup_logger("trip_api_tool")
        self.security_manager = SecurityManager()
        from config import get_config
        self.config = get_config()
    
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

class NotificationTool(BaseTool):
    name: str = "notification"
    description: str = "Send notifications via various channels"
    
    def __init__(self):
        super().__init__()
        self.logger = setup_logger("notification_tool")
    
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
                "recipient": self.security_manager.mask_sensitive_data(recipient),
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