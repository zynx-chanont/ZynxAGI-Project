from typing import Dict, Any, List, Optional, Tuple
import re
from dataclasses import dataclass
from ..config.settings import settings

@dataclass
class ThaiCulturalContext:
    """Thai cultural context analysis result"""
    formality_level: float  # 0.0 to 1.0
    politeness_level: float  # 0.0 to 1.0
    cultural_elements: Dict[str, float]  # Cultural element scores
    suggestions: List[str]  # Cultural adjustment suggestions
    detected_particles: List[str]  # Detected polite particles
    cultural_patterns: List[str]  # Detected cultural patterns

class ThaiCulturalEngine:
    """Thai cultural intelligence engine"""
    
    def __init__(self):
        self.settings = settings
        
        # Cultural settings
        self.cultural_weight = settings.THAI_CULTURAL_WEIGHT
        self.cultural_threshold = settings.DEFAULT_CULTURAL_THRESHOLD
        
        # Polite particles and their formality levels
        self.polite_particles = {
            # Most formal particles
            "ครับ": 1.0,
            "ค่ะ": 1.0,
            "ค่ะ/ครับ": 1.0,
            "ครับ/ค่ะ": 1.0,
            "ขอประทาน": 1.0,
            "กราบเรียน": 1.0,
            "กราบทูล": 1.0,
            
            # Semi-formal particles
            "นะคะ": 0.8,
            "นะครับ": 0.8,
            "ค่ะนะ": 0.8,
            "ครับนะ": 0.8,
            "ขอโทษค่ะ": 0.8,
            "ขอโทษครับ": 0.8,
            
            # Casual polite particles
            "จ้ะ": 0.6,
            "จ้า": 0.6,
            "นะ": 0.5,
            "จ๋า": 0.4,
            "สิ": 0.3,
            "เหรอ": 0.3,
            "หรอ": 0.3,
            
            # Question particles
            "หรือคะ": 0.8,
            "หรือครับ": 0.8,
            "หรือเปล่าคะ": 0.8,
            "หรือเปล่าครับ": 0.8,
            "ไหมคะ": 0.8,
            "ไหมครับ": 0.8,
        }
        
        # Thai cultural patterns and their characteristics
        self.cultural_patterns = {
            "kreng_jai": {
                "patterns": [
                    r"ไม่เป็นไร",
                    r"ไม่ต้องกังวล",
                    r"ไม่เป็นไรมาก",
                    r"ไม่ต้องลำบาก",
                    r"ไม่ต้องห่วง",
                    r"ไม่ต้องเกรงใจ",
                    r"ไม่ต้องอาย",
                    r"ไม่ต้องเกรงใจ",
                    r"ไม่ต้องเกรงใจกัน",
                    r"ไม่ต้องเกรงใจเลย",
                    r"ไม่ต้องกังวลใจ",
                    r"ไม่ต้องเป็นห่วง",
                    r"ไม่ต้องเกรงใจกันเลย",
                    r"ไม่ต้องเกรงใจกันมาก"
                ],
                "weight": 0.8
            },
            "sanuk": {
                "patterns": [
                    r"สนุก",
                    r"เฮฮา",
                    r"รื่นเริง",
                    r"เบิกบาน",
                    r"สดใส",
                    r"มีความสุข",
                    r"เพลิดเพลิน",
                    r"บันเทิง",
                    r"ครึกครื้น",
                    r"ครื้นเครง",
                    r"สนุกสนาน",
                    r"เบิกบานใจ",
                    r"สดชื่น",
                    r"สดใสใจ"
                ],
                "weight": 0.7
            },
            "mai_pen_rai": {
                "patterns": [
                    r"ไม่เป็นไร",
                    r"ไม่เป็นไรมาก",
                    r"ไม่ต้องกังวล",
                    r"ปล่อยไป",
                    r"ช่างมัน",
                    r"ไม่เป็นอะไร",
                    r"ไม่เป็นไรมากมาย",
                    r"ไม่ต้องห่วง",
                    r"ไม่ต้องกังวลใจ",
                    r"ไม่ต้องเป็นห่วง",
                    r"ไม่เป็นไรหรอก",
                    r"ไม่เป็นไรเลย",
                    r"ไม่เป็นไรจริงๆ",
                    r"ไม่เป็นไรหรอกค่ะ"
                ],
                "weight": 0.6
            },
            "greng_jai": {
                "patterns": [
                    r"เกรงใจ",
                    r"เกรงใจคุณ",
                    r"เกรงใจท่าน",
                    r"เกรงใจพี่",
                    r"เกรงใจน้อง",
                    r"เกรงใจกัน",
                    r"เกรงใจมาก",
                    r"เกรงใจจริงๆ",
                    r"เกรงใจเหลือเกิน",
                    r"เกรงใจมากมาย",
                    r"เกรงใจกันมาก",
                    r"เกรงใจกันจริงๆ",
                    r"เกรงใจกันเหลือเกิน",
                    r"เกรงใจกันมากมาย"
                ],
                "weight": 0.9
            },
            "jai_yen": {
                "patterns": [
                    r"ใจเย็น",
                    r"ใจเย็นๆ",
                    r"ใจเย็นไว้",
                    r"ใจเย็นก่อน",
                    r"ใจเย็นสักนิด",
                    r"ใจเย็นหน่อย",
                    r"ใจเย็นๆ นะ",
                    r"ใจเย็นไว้ก่อน",
                    r"ใจเย็นสักครู่นะ",
                    r"ใจเย็นๆ ไว้ก่อน",
                    r"ใจเย็นไว้ก่อนนะ",
                    r"ใจเย็นสักครู่นะคะ",
                    r"ใจเย็นๆ ไว้ก่อนนะ",
                    r"ใจเย็นไว้ก่อนนะคะ"
                ],
                "weight": 0.7
            },
            "nam_jai": {
                "patterns": [
                    r"น้ำใจ",
                    r"น้ำใจดี",
                    r"มีน้ำใจ",
                    r"น้ำใจงาม",
                    r"น้ำใจดีมาก",
                    r"น้ำใจงามมาก",
                    r"น้ำใจดีจริงๆ",
                    r"น้ำใจงามจริงๆ",
                    r"น้ำใจดีเหลือเกิน",
                    r"น้ำใจงามเหลือเกิน",
                    r"น้ำใจดีมากมาย",
                    r"น้ำใจงามมากมาย",
                    r"น้ำใจดีจริงๆ ค่ะ",
                    r"น้ำใจงามจริงๆ ค่ะ"
                ],
                "weight": 0.8
            },
            "kreng_klua": {
                "patterns": [
                    r"เกรงกลัว",
                    r"เกรงกลัวคุณ",
                    r"เกรงกลัวท่าน",
                    r"เกรงกลัวพี่",
                    r"เกรงกลัวน้อง",
                    r"เกรงกลัวกัน",
                    r"เกรงกลัวมาก",
                    r"เกรงกลัวจริงๆ",
                    r"เกรงกลัวเหลือเกิน",
                    r"เกรงกลัวมากมาย",
                    r"เกรงกลัวกันมาก",
                    r"เกรงกลัวกันจริงๆ",
                    r"เกรงกลัวกันเหลือเกิน",
                    r"เกรงกลัวกันมากมาย"
                ],
                "weight": 0.7
            }
        }
        
        # Formal language patterns
        self.formal_patterns = {
            "pronouns": {
                "formal": [
                    "ดิฉัน", "กระผม", "ผม", "หนู",
                    "ข้าพเจ้า", "กระหม่อม", "หม่อมฉัน",
                    "ข้าพระพุทธเจ้า", "ใต้เท้า"
                ],
                "informal": [
                    "กู", "มึง", "เรา", "ชั้น",
                    "ข้า", "ข้าน้อย", "ข้าพระพุทธเจ้า",
                    "ข้าพระพุทธเจ้า", "ข้าพระพุทธเจ้า"
                ]
            },
            "verbs": {
                "formal": [
                    "ขออนุญาต", "กราบเรียน", "กราบทูล", "ขอประทาน",
                    "ขออภัย", "ขออ้าง", "ขอแจ้ง", "ขอรายงาน",
                    "ขอเสนอ", "ขอแนะนำ"
                ],
                "informal": [
                    "บอก", "พูด", "บอกให้", "บอกว่า",
                    "บอกเลย", "บอกไป", "บอกมา", "บอกก่อน",
                    "บอกที", "บอกหน่อย"
                ]
            },
            "greetings": {
                "formal": [
                    "สวัสดีครับ", "สวัสดีค่ะ",
                    "กราบสวัสดีครับ", "กราบสวัสดีค่ะ",
                    "กราบเรียนสวัสดีครับ", "กราบเรียนสวัสดีค่ะ"
                ],
                "informal": [
                    "สวัสดี", "หวัดดี", "หวัดดีจ้า",
                    "หวัดดีจ๋า", "หวัดดีนะ", "หวัดดีค่ะ"
                ]
            }
        }

    def analyze_polite_particles(self, text: str) -> Tuple[List[str], float]:
        """Analyze polite particles in text"""
        detected_particles = []
        politeness_score = 0.0
        
        for particle, formality in self.polite_particles.items():
            if particle in text:
                detected_particles.append(particle)
                politeness_score = max(politeness_score, formality)
        
        return detected_particles, politeness_score

    def analyze_formality(self, text: str) -> float:
        """Analyze formality level of text"""
        formality_score = 0.0
        
        # Check for formal pronouns
        for pronoun in self.formal_patterns["pronouns"]["formal"]:
            if pronoun in text:
                formality_score += 0.3
        
        # Check for formal verbs
        for verb in self.formal_patterns["verbs"]["formal"]:
            if verb in text:
                formality_score += 0.2
        
        # Check for formal greetings
        for greeting in self.formal_patterns["greetings"]["formal"]:
            if greeting in text:
                formality_score += 0.2
        
        # Check for informal elements
        for pronoun in self.formal_patterns["pronouns"]["informal"]:
            if pronoun in text:
                formality_score -= 0.3
        
        for verb in self.formal_patterns["verbs"]["informal"]:
            if verb in text:
                formality_score -= 0.2
        
        for greeting in self.formal_patterns["greetings"]["informal"]:
            if greeting in text:
                formality_score -= 0.2
        
        return max(0.0, min(1.0, formality_score))

    def detect_cultural_patterns(self, text: str) -> Dict[str, float]:
        """Detect Thai cultural patterns in text"""
        pattern_scores = {}
        
        for pattern_name, pattern_data in self.cultural_patterns.items():
            score = 0.0
            for regex in pattern_data["patterns"]:
                if re.search(regex, text, re.IGNORECASE):
                    score += pattern_data["weight"]
            if score > 0:
                pattern_scores[pattern_name] = min(1.0, score)
        
        return pattern_scores

    def generate_cultural_suggestions(self, 
                                   formality: float, 
                                   politeness: float,
                                   cultural_patterns: Dict[str, float]) -> List[str]:
        """Generate suggestions for cultural adjustments"""
        suggestions = []
        
        # Formality suggestions
        if formality < 0.3:
            suggestions.append("ควรใช้ภาษาที่เป็นทางการมากขึ้น")
            suggestions.append("เพิ่มคำสรรพนามที่เป็นทางการ (ดิฉัน, กระผม)")
            suggestions.append("ใช้คำกริยาที่เป็นทางการ (กราบเรียน, ขออนุญาต)")
        elif formality > 0.8:
            suggestions.append("ควรใช้ภาษาที่เป็นกันเองมากขึ้น")
            suggestions.append("ลดการใช้คำสรรพนามที่เป็นทางการ")
            suggestions.append("ใช้คำกริยาที่เป็นกันเองมากขึ้น")
        
        # Politeness suggestions
        if politeness < 0.3:
            suggestions.append("ควรเพิ่มความสุภาพในการสื่อสาร")
            suggestions.append("เพิ่มคำลงท้ายที่สุภาพ (ค่ะ, ครับ)")
            suggestions.append("ใช้คำขอโทษและขอบคุณให้มากขึ้น")
        elif politeness > 0.8:
            suggestions.append("อาจจะสุภาพมากเกินไปในบางสถานการณ์")
            suggestions.append("ลองปรับระดับความสุภาพให้เหมาะสมกับบริบท")
        
        # Cultural pattern suggestions
        if "kreng_jai" in cultural_patterns and cultural_patterns["kreng_jai"] > 0.7:
            suggestions.append("แสดงความเกรงใจในระดับที่เหมาะสม")
            suggestions.append("ใช้คำพูดที่แสดงความเกรงใจอย่างสุภาพ")
        
        if "sanuk" in cultural_patterns and cultural_patterns["sanuk"] > 0.7:
            suggestions.append("สร้างบรรยากาศที่เป็นมิตรและสนุกสนาน")
            suggestions.append("ใช้คำพูดที่สร้างความสุขและความบันเทิง")
        
        if "jai_yen" in cultural_patterns and cultural_patterns["jai_yen"] > 0.7:
            suggestions.append("แสดงความใจเย็นและความเข้าใจ")
            suggestions.append("ใช้คำพูดที่ให้กำลังใจและปลอบใจ")
        
        if "nam_jai" in cultural_patterns and cultural_patterns["nam_jai"] > 0.7:
            suggestions.append("แสดงน้ำใจและความเอื้อเฟื้อ")
            suggestions.append("ใช้คำพูดที่แสดงความมีน้ำใจและความช่วยเหลือ")
        
        return suggestions

    def adjust_response(self, 
                       text: str, 
                       target_formality: float = 0.7,
                       target_politeness: float = 0.8) -> str:
        """Adjust response based on cultural context"""
        current_formality = self.analyze_formality(text)
        current_politeness = self.analyze_polite_particles(text)[1]
        
        # Adjust formality
        if current_formality < target_formality:
            # Make more formal
            text = self._make_more_formal(text)
        elif current_formality > target_formality:
            # Make more casual
            text = self._make_more_casual(text)
        
        # Adjust politeness
        if current_politeness < target_politeness:
            # Make more polite
            text = self._make_more_polite(text)
        elif current_politeness > target_politeness:
            # Make less polite
            text = self._make_less_polite(text)
        
        return text

    def _make_more_formal(self, text: str) -> str:
        """Make text more formal"""
        # Replace informal pronouns with formal ones
        for informal, formal in zip(
            self.formal_patterns["pronouns"]["informal"],
            self.formal_patterns["pronouns"]["formal"]
        ):
            text = text.replace(informal, formal)
        
        # Replace informal verbs with formal ones
        for informal, formal in zip(
            self.formal_patterns["verbs"]["informal"],
            self.formal_patterns["verbs"]["formal"]
        ):
            text = text.replace(informal, formal)
        
        return text

    def _make_more_casual(self, text: str) -> str:
        """Make text more casual"""
        # Replace formal pronouns with informal ones
        for formal, informal in zip(
            self.formal_patterns["pronouns"]["formal"],
            self.formal_patterns["pronouns"]["informal"]
        ):
            text = text.replace(formal, informal)
        
        # Replace formal verbs with informal ones
        for formal, informal in zip(
            self.formal_patterns["verbs"]["formal"],
            self.formal_patterns["verbs"]["informal"]
        ):
            text = text.replace(formal, informal)
        
        return text

    def _make_more_polite(self, text: str) -> str:
        """Make text more polite"""
        # Add polite particles if not present
        if not any(particle in text for particle in ["ค่ะ", "ครับ"]):
            text += "ค่ะ" if "ดิฉัน" in text or "หนู" in text else "ครับ"
        
        return text

    def _make_less_polite(self, text: str) -> str:
        """Make text less polite"""
        # Remove polite particles
        for particle in ["ค่ะ", "ครับ", "นะคะ", "นะครับ"]:
            text = text.replace(particle, "")
        
        return text

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a message with Thai cultural context"""
        text = message.get("text", "")
        context_type = message.get("context_type", "formal")
        
        # Analyze text
        particles, politeness = self.analyze_polite_particles(text)
        formality = self.analyze_formality(text)
        cultural_patterns = self.detect_cultural_patterns(text)
        
        # Generate suggestions
        suggestions = self.generate_cultural_suggestions(
            formality, politeness, cultural_patterns
        )
        
        # Create cultural context
        cultural_context = ThaiCulturalContext(
            formality_level=formality,
            politeness_level=politeness,
            cultural_elements=cultural_patterns,
            suggestions=suggestions,
            detected_particles=particles,
            cultural_patterns=list(cultural_patterns.keys())
        )
        
        # Adjust response if needed
        if message.get("adjust_response", True):
            adjusted_text = self.adjust_response(
                text,
                target_formality=self.settings.FORMAL_CONTEXT_WEIGHT if context_type == "formal" 
                               else self.settings.INFORMAL_CONTEXT_WEIGHT,
                target_politeness=self.settings.THAI_CULTURAL_WEIGHT
            )
        else:
            adjusted_text = text
        
        return {
            "original_text": text,
            "adjusted_text": adjusted_text,
            "cultural_context": {
                "formality_level": formality,
                "politeness_level": politeness,
                "cultural_elements": cultural_patterns,
                "suggestions": suggestions,
                "detected_particles": particles,
                "cultural_patterns": list(cultural_patterns.keys())
            }
        } 