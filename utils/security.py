"""
Security utilities for the agentic AI workflow system
Handles input validation, authorization, and audit logging
"""

import hashlib
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional
import os

class SecurityManager:
    """
    Manages security aspects of the workflow system
    """
    
    def __init__(self):
        self.logger = logging.getLogger("security")
        self.dangerous_patterns = [
            r'rm\s+-rf',  # Dangerous file deletion
            r'sudo\s+',   # Privilege escalation
            r'curl.*\|.*sh',  # Potentially dangerous downloads
            r'wget.*\|.*sh',
            r'eval\s*\(',  # Code evaluation
            r'exec\s*\(',  # Code execution
            r'__import__',  # Python imports
            r'subprocess',  # System calls
            r'os\.system',  # System commands
            r'shell=True', # Shell execution
        ]
        
        self.audit_log_file = os.getenv("AUDIT_LOG_FILE", "logs/security_audit.log")
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        log_dir = os.path.dirname(self.audit_log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    def validate_message(self, message: str) -> bool:
        """
        Validate user message for security risks
        
        Args:
            message: User input message
            
        Returns:
            True if message is safe, False otherwise
        """
        if not message or len(message.strip()) == 0:
            return False
        
        # Check message length
        if len(message) > 10000:  # Reasonable length limit
            self.log_security_event("message_too_long", {"length": len(message)})
            return False
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                self.log_security_event("dangerous_pattern_detected", {
                    "pattern": pattern,
                    "message": message[:100] + "..." if len(message) > 100 else message
                })
                return False
        
        # Check for suspicious URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, message)
        if urls:
            for url in urls:
                if not self._is_safe_url(url):
                    self.log_security_event("suspicious_url", {"url": url})
                    return False
        
        return True
    
    def _is_safe_url(self, url: str) -> bool:
        """
        Check if URL is safe (basic whitelist approach)
        """
        safe_domains = [
            'github.com',
            'docs.python.org',
            'stackoverflow.com',
            'google.com',
            'microsoft.com',
            'openai.com'
        ]
        
        # Extract domain from URL
        domain_match = re.search(r'https?://([^/]+)', url)
        if domain_match:
            domain = domain_match.group(1).lower()
            return any(safe_domain in domain for safe_domain in safe_domains)
        
        return False
    
    def sanitize_input(self, input_data: str) -> str:
        """
        Sanitize user input by removing or escaping dangerous characters
        """
        if not input_data:
            return ""
        
        # Remove null bytes and control characters
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', input_data)
        
        # Limit length
        sanitized = sanitized[:5000]
        
        return sanitized.strip()
    
    def validate_workflow_params(self, params: Dict) -> bool:
        """
        Validate workflow parameters for security
        """
        if not isinstance(params, dict):
            return False
        
        # Check for nested depth (prevent deep object attacks)
        if self._get_dict_depth(params) > 10:
            self.log_security_event("excessive_nesting", {"depth": self._get_dict_depth(params)})
            return False
        
        # Validate string values
        for key, value in params.items():
            if isinstance(value, str):
                if not self.validate_message(value):
                    return False
        
        return True
    
    def _get_dict_depth(self, d: Dict, depth: int = 0) -> int:
        """Calculate maximum depth of nested dictionary"""
        if not isinstance(d, dict):
            return depth
        
        if not d:
            return depth
        
        return max(self._get_dict_depth(v, depth + 1) for v in d.values())
    
    def log_unauthorized_access(self, user_id: str, message: str):
        """Log unauthorized access attempt"""
        self.log_security_event("unauthorized_access", {
            "user_id": user_id,
            "message": message[:100] + "..." if len(message) > 100 else message
        })
    
    def log_security_event(self, event_type: str, details: Dict):
        """
        Log security events to audit log
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details,
            "severity": self._get_event_severity(event_type)
        }
        
        # Log to file
        try:
            with open(self.audit_log_file, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            self.logger.error(f"Failed to write to audit log: {e}")
        
        # Log to system logger
        self.logger.warning(f"Security event: {event_type} - {details}")
    
    def _get_event_severity(self, event_type: str) -> str:
        """Determine severity level for security events"""
        high_severity = [
            "dangerous_pattern_detected",
            "unauthorized_access",
            "suspicious_url",
            "code_injection_attempt"
        ]
        
        if event_type in high_severity:
            return "HIGH"
        return "MEDIUM"
    
    def generate_session_token(self, user_id: str) -> str:
        """Generate secure session token for user"""
        timestamp = str(datetime.now().timestamp())
        data = f"{user_id}:{timestamp}:{os.getenv('SECRET_KEY', 'default_secret')}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def validate_api_key(self, api_key: str, expected_key: str) -> bool:
        """Validate API key using secure comparison"""
        if not api_key or not expected_key:
            return False
        
        # Use secure comparison to prevent timing attacks
        return hashlib.sha256(api_key.encode()).hexdigest() == hashlib.sha256(expected_key.encode()).hexdigest()
    
    def mask_sensitive_data(self, data: str) -> str:
        """
        Mask sensitive data in logs and responses
        """
        # Mask email addresses
        data = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                     lambda m: m.group()[:3] + "***@***.***", data)
        
        # Mask API keys and tokens
        data = re.sub(r'\b[A-Za-z0-9]{20,}\b', 
                     lambda m: m.group()[:4] + "*" * (len(m.group()) - 8) + m.group()[-4:], data)
        
        # Mask phone numbers
        data = re.sub(r'\b\d{3}-?\d{3}-?\d{4}\b', "***-***-****", data)
        
        return data
    
    def get_security_report(self) -> Dict:
        """
        Generate security report from audit logs
        """
        try:
            events = []
            if os.path.exists(self.audit_log_file):
                with open(self.audit_log_file, "r") as f:
                    for line in f:
                        try:
                            events.append(json.loads(line.strip()))
                        except json.JSONDecodeError:
                            continue
            
            # Analyze events
            event_counts = {}
            high_severity_count = 0
            
            for event in events[-100:]:  # Last 100 events
                event_type = event.get("event_type", "unknown")
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
                
                if event.get("severity") == "HIGH":
                    high_severity_count += 1
            
            return {
                "total_events": len(events),
                "recent_events": len(events[-100:]),
                "high_severity_events": high_severity_count,
                "event_types": event_counts,
                "report_generated": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to generate security report: {e}")
            return {"error": str(e)}