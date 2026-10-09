"""
GramSehat Layer 5: Safety Rule Engine Service
=============================================
A deterministic, explainable, config-driven clinical rule engine.
Evaluates structured symptoms (Layer 4), raw user text transcripts (Layer 2),
and computer vision screening flags (Layer 3) against fixed WHO/IMCI danger rules.

NO LLMs, neural networks, or external network requests are utilized in this layer.
"""

import os
import re
import logging
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

from app.schemas.rules import (
    UrgencyAssessmentRequest,
    UrgencyAssessmentResponse,
)

logger = logging.getLogger("gramsehat.rule_engine")

# Punctuation to strip during text normalization (ASCII + Devanagari dandas)
PUNCT_PATTERN = re.compile(r'[\!\"\#\$\%\&\'\(\)\*\+\,\-\.\/\:\;\<\=\>\?\@\[\\\]\^\_\`\{\|\}\~\।॥]')
WHITESPACE_PATTERN = re.compile(r'\s+')

# Pure demographic tags (not clinical symptoms on their own)
DEMOGRAPHIC_TAGS = {"child_under_5", "elderly_over_60", "pregnancy"}

# Default directory for rules and keywords configs
DEFAULT_CONFIG_DIR = Path(__file__).resolve().parent.parent / "rules"


def normalize_text(text: str) -> str:
    """
    Standardize text input for robust multi-lingual keyword matching.
    - Applies Unicode NFKC normalization
    - Converts to lowercase
    - Replaces punctuation with spaces (avoids accidental word merging)
    - Normalizes multi-spaces to a single space
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", str(text))
    text = text.lower()
    text = PUNCT_PATTERN.sub(" ", text)
    return WHITESPACE_PATTERN.sub(" ", text).strip()


class SafetyRuleEngine:
    """
    Config-driven deterministic rule engine for clinical urgency triage.
    Supports live config reloading on file modification.
    """

    def __init__(
        self,
        rules_path: Optional[str] = None,
        keywords_path: Optional[str] = None,
        auto_reload: bool = True
    ):
        self.rules_path = Path(
            rules_path
            or os.environ.get("RULES_CONFIG_PATH")
            or DEFAULT_CONFIG_DIR / "rules.yaml"
        )
        self.keywords_path = Path(
            keywords_path
            or os.environ.get("KEYWORDS_CONFIG_PATH")
            or DEFAULT_CONFIG_DIR / "keywords.yaml"
        )
        self.auto_reload = auto_reload

        self._rules_mtime: float = 0.0
        self._keywords_mtime: float = 0.0

        self.rules: List[Dict[str, Any]] = []
        self.keywords_map: Dict[str, List[str]] = {}
        self.known_symptom_tags: Set[str] = set()

        self._load_configs(force=True)

    def _load_configs(self, force: bool = False) -> None:
        """Load or reload rules.yaml and keywords.yaml if modified."""
        try:
            if self.keywords_path.exists():
                mtime = self.keywords_path.stat().st_mtime
                if force or mtime > self._keywords_mtime:
                    with open(self.keywords_path, "r", encoding="utf-8") as f:
                        raw_data = yaml.safe_load(f) or {}
                    raw_keywords = raw_data.get("keywords", {})
                    
                    parsed_keywords: Dict[str, List[str]] = {}
                    for tag, lang_dict in raw_keywords.items():
                        synonyms: List[str] = []
                        if isinstance(lang_dict, dict):
                            for phrases in lang_dict.values():
                                if isinstance(phrases, list):
                                    for p in phrases:
                                        cleaned = normalize_text(str(p))
                                        if cleaned and cleaned not in synonyms:
                                            synonyms.append(cleaned)
                        elif isinstance(lang_dict, list):
                            for p in lang_dict:
                                cleaned = normalize_text(str(p))
                                if cleaned and cleaned not in synonyms:
                                    synonyms.append(cleaned)
                        
                        # Sort longest phrases first for greedy matching
                        synonyms.sort(key=lambda x: len(x), reverse=True)
                        parsed_keywords[tag] = synonyms

                    self.keywords_map = parsed_keywords
                    self.known_symptom_tags = set(parsed_keywords.keys())
                    self._keywords_mtime = mtime
                    logger.info("Loaded %d symptom keyword mappings from %s", len(self.keywords_map), self.keywords_path)

            if self.rules_path.exists():
                mtime = self.rules_path.stat().st_mtime
                if force or mtime > self._rules_mtime:
                    with open(self.rules_path, "r", encoding="utf-8") as f:
                        raw_data = yaml.safe_load(f) or {}
                    self.rules = raw_data.get("rules", [])
                    self._rules_mtime = mtime
                    logger.info("Loaded %d clinical rules from %s", len(self.rules), self.rules_path)

        except Exception as e:
            logger.error("Failed to load rule engine configurations: %s", e, exc_info=True)
            if not self.rules:
                raise

    def check_and_reload(self) -> None:
        """Check modification timestamps and reload configs if modified."""
        if self.auto_reload:
            self._load_configs(force=False)

    def extract_tags_from_text(self, text: str) -> Set[str]:
        """
        Scan normalized raw text transcript for keyword occurrences across
        English, Hindi, and Hinglish lexicons.
        """
        detected: Set[str] = set()
        normalized = normalize_text(text)
        if not normalized:
            return detected

        for tag, phrases in self.keywords_map.items():
            for phrase in phrases:
                # If multi-word phrase, check substring or boundary
                if " " in phrase:
                    if phrase in normalized:
                        detected.add(tag)
                        break
                else:
                    # Single word token: check word boundary
                    pattern = rf"(?:^|\s){re.escape(phrase)}(?:\s|$)"
                    if re.search(pattern, normalized):
                        detected.add(tag)
                        break

        return detected

    def extract_tags_from_structured_list(self, structured_items: List[str]) -> Set[str]:
        """
        Process Layer 4 structured symptoms or screening flags.
        Matches directly against known canonical tag identifiers, or runs
        item text against keyword dictionary.
        """
        detected: Set[str] = set()
        for item in structured_items:
            if not item:
                continue
            canonical_candidate = normalize_text(item).replace(" ", "_")
            if canonical_candidate in self.known_symptom_tags:
                detected.add(canonical_candidate)
                continue

            # Check direct aliases
            if canonical_candidate == "eye_redness_flag":
                detected.add("eye_redness")
                continue
            if canonical_candidate in ("pallor", "pallor_flag"):
                detected.add("pallor_screening_flag")
                continue

            # Also scan phrase text
            matched = self.extract_tags_from_text(item)
            detected.update(matched)

        return detected

    def evaluate(self, request: UrgencyAssessmentRequest) -> UrgencyAssessmentResponse:
        """
        Execute deterministic urgency assessment following the 6-stage clinical pipeline:
        1. Config synchronization
        2. Multi-source symptom extraction (Layer 4, Layer 2, Layer 3)
        3. Demographic risk injection (Age <5, >60, Pregnancy)
        4. Rule matching & modifier escalation
        5. Verdict arbitration (Red > Yellow > Green)
        6. Fail-safe validation for empty or uninterpretable input
        """
        self.check_and_reload()

        # Step 1: Extract tags from Layer 2 raw text
        raw_tags = self.extract_tags_from_text(request.raw_text or "")

        # Step 2: Extract tags from Layer 4 structured symptoms
        structured_tags = self.extract_tags_from_structured_list(request.structured_symptoms or [])

        # Step 3: Extract tags from Layer 3 screening flags
        screening_tags = self.extract_tags_from_structured_list(request.screening_flags or [])

        # Step 4: Union of all detected clinical symptoms
        clinical_symptom_tags: Set[str] = set()
        clinical_symptom_tags.update(raw_tags)
        clinical_symptom_tags.update(structured_tags)
        clinical_symptom_tags.update(screening_tags)

        # Step 5: Patient demographic status
        patient = request.patient
        age = patient.age if patient else None
        is_pregnant = bool(patient.is_pregnant) if patient else False

        is_under_5 = age is not None and age < 5.0
        is_over_60 = age is not None and age > 60.0

        all_detected_tags = set(clinical_symptom_tags)
        if is_under_5:
            all_detected_tags.add("child_under_5")
        if is_over_60:
            all_detected_tags.add("elderly_over_60")
        if is_pregnant:
            all_detected_tags.add("pregnancy")

        # Step 6: Fail-Safe Guard for empty or unclear input
        # If no clinical symptoms were recognized (even if demographics are present)
        if not clinical_symptom_tags:
            return UrgencyAssessmentResponse(
                urgency="yellow",
                triggered_rules=["FAILSAFE_UNCLEAR_INPUT"],
                reason=(
                    "No recognized clinical symptoms could be identified from the provided input. "
                    "To guarantee patient safety, urgent medical conditions cannot be ruled out without further assessment."
                ),
                recommended_action=(
                    "Please provide more specific details regarding your current health complaint, "
                    "including pain location, symptom duration, or consult your nearest ASHA worker / PHC."
                ),
                required_specialty="General Medicine",
                follow_up_question=(
                    "Can you tell us what main problem or discomfort you are experiencing right now, "
                    "how many days it has been present, and if you have any severe pain or breathing trouble?"
                )
            )

        # Step 7: Evaluate deterministic rules from rules.yaml
        triggered_rules_info: List[Dict[str, Any]] = []

        for rule in self.rules:
            rule_id = rule.get("id", "UNKNOWN_RULE")
            level = rule.get("level", "yellow").lower()
            all_of = rule.get("all_of") or []
            any_of = rule.get("any_of") or []
            none_of = rule.get("none_of") or []
            specialty = rule.get("specialty")
            action = rule.get("action", "")
            reason = rule.get("reason", "")
            escalate_modifiers = rule.get("escalate_modifiers") or {}

            # Condition 1: all_of must be fully satisfied
            if all_of and not all(tag in all_detected_tags for tag in all_of):
                continue

            # Condition 2: any_of must have at least one match (if specified)
            if any_of and not any(tag in all_detected_tags for tag in any_of):
                continue

            # Condition 3: none_of must have zero matches (if specified)
            if none_of and any(tag in all_detected_tags for tag in none_of):
                continue

            # Rule triggered! Check modifier escalations (e.g. Yellow -> Red)
            effective_level = level
            effective_specialty = specialty
            effective_reason = reason

            if level == "yellow" and escalate_modifiers:
                if is_under_5 and "under_5" in escalate_modifiers:
                    mod = escalate_modifiers["under_5"]
                    effective_level = mod.get("escalate_to", "red")
                    if mod.get("specialty_override"):
                        effective_specialty = mod.get("specialty_override")
                    if mod.get("reason_suffix"):
                        effective_reason = f"{reason} [{mod.get('reason_suffix')}]"
                elif is_pregnant and "pregnant" in escalate_modifiers:
                    mod = escalate_modifiers["pregnant"]
                    effective_level = mod.get("escalate_to", "red")
                    if mod.get("specialty_override"):
                        effective_specialty = mod.get("specialty_override")
                    if mod.get("reason_suffix"):
                        effective_reason = f"{reason} [{mod.get('reason_suffix')}]"
                elif is_over_60 and "over_60" in escalate_modifiers:
                    mod = escalate_modifiers["over_60"]
                    effective_level = mod.get("escalate_to", "red")
                    if mod.get("specialty_override"):
                        effective_specialty = mod.get("specialty_override")
                    if mod.get("reason_suffix"):
                        effective_reason = f"{reason} [{mod.get('reason_suffix')}]"

            triggered_rules_info.append({
                "id": rule_id,
                "level": effective_level,
                "specialty": effective_specialty,
                "action": action,
                "reason": effective_reason,
                "all_of": all_of
            })

        # Step 8: Verdict arbitration
        def rule_specificity_priority(r: Dict[str, Any]) -> int:
            score = 0
            spec = r.get("specialty", "")
            # Prioritize vulnerable demographic targeted rules when matching patient status
            if is_under_5 and spec == "Pediatrics":
                score += 300
            elif is_pregnant and spec == "Obstetrics":
                score += 300
            # Prioritize rules requiring specific compound tags over broad catch-alls
            score += len(r.get("all_of", [])) * 10
            return score

        red_triggers = [r for r in triggered_rules_info if r["level"] == "red"]
        red_triggers.sort(key=rule_specificity_priority, reverse=True)

        yellow_triggers = [r for r in triggered_rules_info if r["level"] == "yellow"]
        yellow_triggers.sort(key=rule_specificity_priority, reverse=True)

        if red_triggers:
            # RED VERDICT
            triggered_ids = [r["id"] for r in red_triggers]
            primary_red = red_triggers[0]
            
            # Combine reasons if multiple red rules trigger
            if len(red_triggers) > 1:
                combined_reason = " | ".join(f"({r['id']}) {r['reason']}" for r in red_triggers)
            else:
                combined_reason = primary_red["reason"]

            return UrgencyAssessmentResponse(
                urgency="red",
                triggered_rules=triggered_ids,
                reason=combined_reason,
                recommended_action=primary_red["action"],
                required_specialty=primary_red["specialty"],
                follow_up_question=None
            )

        elif yellow_triggers:
            # YELLOW VERDICT
            triggered_ids = [r["id"] for r in yellow_triggers]
            primary_yellow = yellow_triggers[0]

            if len(yellow_triggers) > 1:
                combined_reason = " | ".join(f"({r['id']}) {r['reason']}" for r in yellow_triggers)
            else:
                combined_reason = primary_yellow["reason"]

            return UrgencyAssessmentResponse(
                urgency="yellow",
                triggered_rules=triggered_ids,
                reason=combined_reason,
                recommended_action=primary_yellow["action"],
                required_specialty=primary_yellow["specialty"],
                follow_up_question=(
                    "Have your symptoms worsened over the last 24 hours, "
                    "or have you noticed any difficulty in breathing or taking fluids?"
                )
            )

        else:
            # GREEN VERDICT (Recognized symptoms present, but no red or yellow rules triggered)
            return UrgencyAssessmentResponse(
                urgency="green",
                triggered_rules=[],
                reason=(
                    "No emergency danger signs or prolonged red/yellow flag symptoms detected. "
                    "Symptoms appear mild and short-lived, suitable for supportive home care and observation."
                ),
                recommended_action=(
                    "Rest, maintain adequate hydration and nutrition. If symptoms worsen, "
                    "new danger signs appear, or no improvement is seen in 48 hours, visit your nearest Primary Health Centre."
                ),
                required_specialty=None,
                follow_up_question=None
            )


# Singleton engine instance for FastAPI route integration
_engine_instance: Optional[SafetyRuleEngine] = None


def get_rule_engine() -> SafetyRuleEngine:
    """Return singleton instance of SafetyRuleEngine."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = SafetyRuleEngine()
    return _engine_instance
