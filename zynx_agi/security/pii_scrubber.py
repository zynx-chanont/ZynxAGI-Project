import re
import hashlib
import hmac
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from ..config.settings import settings

@dataclass
class PIIDetectionResult:
    """Result of PII detection scan"""
    has_pii: bool
    detected_types: List[str]
    confidence_score: float
    redacted_text: str
    pseudonymized_data: Dict[str, str]

class PIIScrubber:
    """PII detection and scrubbing for Zynx AGI"""
    
    def __init__(self):
        self.hmac_key = settings.HMAC_PSEUDONYM_KEY.encode()
        
        # PII patterns for detection
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone_us': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            'phone_th': r'\b(?:\+66[-.\s]?|0)[-.\s]?[0-9]{1,2}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
            'phone_international': r'\+[0-9]{1,3}[-.\s]?[0-9]{1,3}[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'thai_id': r'\b\d{1}-\d{4}-\d{5}-\d{2}-\d{1}\b',
            'credit_card': r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',
            'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            'name_formal': r'\b(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Prof\.?)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
            'thai_name_pattern': r'\b(?:คุณ|นาย|นาง|นางสาว)\s*[ก-๙]+(?:\s+[ก-๙]+)*\b'
        }
        
        # Replacement patterns
        self.replacements = {
            'email': '[EMAIL_REDACTED]',
            'phone_us': '[PHONE_REDACTED]',
            'phone_th': '[PHONE_REDACTED]',
            'phone_international': '[PHONE_REDACTED]',
            'ssn': '[SSN_REDACTED]',
            'thai_id': '[ID_REDACTED]',
            'credit_card': '[CARD_REDACTED]',
            'ip_address': '[IP_REDACTED]',
            'name_formal': '[NAME_REDACTED]',
            'thai_name_pattern': '[ชื่อ_ถูกซ่อน]'
        }
    
    def _generate_pseudonym(self, original_value: str, pii_type: str) -> str:
        """Generate a consistent pseudonym for PII data"""
        # Create deterministic hash using HMAC
        signature = hmac.new(
            self.hmac_key, 
            f"{pii_type}:{original_value}".encode(), 
            hashlib.sha256
        ).hexdigest()[:8]
        
        return f"{pii_type.upper()}_{signature}"
    
    def detect_pii(self, text: str) -> PIIDetectionResult:
        """Detect PII in text and return detection results"""
        detected_types = []
        pseudonymized_data = {}
        redacted_text = text
        confidence_scores = []
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            
            for match in matches:
                detected_types.append(pii_type)
                original_value = match.group()
                
                # Generate pseudonym for logging/auditing
                pseudonym = self._generate_pseudonym(original_value, pii_type)
                pseudonymized_data[pseudonym] = pii_type
                
                # Replace with redaction marker
                redacted_text = redacted_text.replace(
                    original_value, 
                    self.replacements[pii_type]
                )
                
                # High confidence for exact pattern matches
                confidence_scores.append(0.9)
        
        # Calculate overall confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        return PIIDetectionResult(
            has_pii=len(detected_types) > 0,
            detected_types=list(set(detected_types)),
            confidence_score=avg_confidence,
            redacted_text=redacted_text,
            pseudonymized_data=pseudonymized_data
        )
    
    def scrub_request(self, request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], PIIDetectionResult]:
        """Scrub PII from request data"""
        scrubbed_data = request_data.copy()
        all_detected_types = []
        all_pseudonymized_data = {}
        all_text_parts = []
        
        # Check common text fields
        text_fields = ['text', 'message', 'prompt', 'content', 'query', 'input']
        
        for field in text_fields:
            if field in scrubbed_data and isinstance(scrubbed_data[field], str):
                detection_result = self.detect_pii(scrubbed_data[field])
                
                if detection_result.has_pii:
                    scrubbed_data[field] = detection_result.redacted_text
                    all_detected_types.extend(detection_result.detected_types)
                    all_pseudonymized_data.update(detection_result.pseudonymized_data)
                
                all_text_parts.append(scrubbed_data[field])
        
        # Create combined detection result
        combined_result = PIIDetectionResult(
            has_pii=len(all_detected_types) > 0,
            detected_types=list(set(all_detected_types)),
            confidence_score=0.9 if all_detected_types else 0.0,
            redacted_text=" ".join(all_text_parts),
            pseudonymized_data=all_pseudonymized_data
        )
        
        return scrubbed_data, combined_result
    
    def scrub_response(self, response_data: Dict[str, Any]) -> Tuple[Dict[str, Any], PIIDetectionResult]:
        """Scrub PII from response data"""
        scrubbed_data = response_data.copy()
        
        # Check response text fields
        text_fields = ['text', 'message', 'content', 'response']
        all_detected_types = []
        all_pseudonymized_data = {}
        
        for field in text_fields:
            if field in scrubbed_data and isinstance(scrubbed_data[field], str):
                detection_result = self.detect_pii(scrubbed_data[field])
                
                if detection_result.has_pii:
                    scrubbed_data[field] = detection_result.redacted_text
                    all_detected_types.extend(detection_result.detected_types)
                    all_pseudonymized_data.update(detection_result.pseudonymized_data)
        
        combined_result = PIIDetectionResult(
            has_pii=len(all_detected_types) > 0,
            detected_types=list(set(all_detected_types)),
            confidence_score=0.9 if all_detected_types else 0.0,
            redacted_text="",
            pseudonymized_data=all_pseudonymized_data
        )
        
        return scrubbed_data, combined_result

    def check_cross_border_compliance(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if cross-border data transfer compliance is required"""
        if not settings.CROSS_BORDER_COMPLIANCE:
            return {"compliant": True, "checks_required": False}
        
        # Simple compliance check - in production this would be more comprehensive
        compliance_result = {
            "compliant": True,
            "checks_required": True,
            "dpia_required": False,
            "region": "thailand",
            "transfer_allowed": True,
            "requirements": []
        }
        
        # Check if PII is present
        _, pii_result = self.scrub_request(request_data)
        
        if pii_result.has_pii:
            compliance_result["dpia_required"] = True
            compliance_result["requirements"].append("Data Protection Impact Assessment required")
            compliance_result["requirements"].append("PII detected - enhanced protection required")
        
        return compliance_result

# Global instance
pii_scrubber = PIIScrubber()