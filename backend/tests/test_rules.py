"""
Comprehensive Test Suite for GramSehat Layer 5: Safety Rule Engine
==================================================================
Tests deterministic clinical rule evaluation across:
- Emergency Red Flags (Cardiac, Ocular, Obstetric, IMCI Pediatric, Neuro, Respiratory, Trauma)
- Multi-lingual matching (Hindi Devanagari, Hinglish colloquial, English)
- Fail-safe guards on empty/ambiguous inputs (guaranteed Yellow, never Green)
- Demographic modifier escalations (Child <5, Elderly >60, Pregnancy)
- Dual source protection (Danger sign in raw text when LLM misses it)
- Layer 3 Computer Vision screening flags
- Config-driven dynamic rule reloading without code change
- FastAPI /assess-urgency HTTP endpoint verification
"""

import os
import tempfile
import unittest
from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.rules import (
    PatientContext,
    UrgencyAssessmentRequest,
    UrgencyAssessmentResponse,
)
from app.services.rule_engine import SafetyRuleEngine, get_rule_engine


class TestSafetyRuleEngine(unittest.TestCase):
    """Unit and integration tests for Layer 5 deterministic triage engine."""

    @classmethod
    def setUpClass(cls):
        cls.engine = get_rule_engine()
        cls.client = TestClient(app)

    # --------------------------------------------------------------------------
    # 1. FAIL-SAFE BEHAVIOR (Empty / Unclear Input -> NEVER Green, Always Yellow)
    # --------------------------------------------------------------------------

    def test_01_empty_input_returns_yellow_failsafe(self):
        """Empty input must safely return yellow with follow-up prompt, NEVER green."""
        req = UrgencyAssessmentRequest(
            structured_symptoms=[],
            raw_text="",
            screening_flags=[],
            patient=PatientContext(age=30, is_pregnant=False)
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "yellow")
        self.assertIn("FAILSAFE_UNCLEAR_INPUT", res.triggered_rules)
        self.assertIsNotNone(res.follow_up_question)
        self.assertEqual(res.required_specialty, "General Medicine")

    def test_02_gibberish_or_conversational_greeting_returns_yellow(self):
        """Conversational greetings without clinical symptoms must trigger fail-safe yellow."""
        req = UrgencyAssessmentRequest(
            structured_symptoms=[],
            raw_text="Namaste doctor ji, ram ram, kripya suniye",
            screening_flags=[]
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "yellow")
        self.assertIn("FAILSAFE_UNCLEAR_INPUT", res.triggered_rules)
        self.assertIsNotNone(res.follow_up_question)

    def test_03_demographics_only_without_symptoms_returns_yellow(self):
        """Child or pregnant patient without symptoms must return fail-safe yellow, not green."""
        req = UrgencyAssessmentRequest(
            structured_symptoms=[],
            raw_text="",
            patient=PatientContext(age=2, is_pregnant=False)
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "yellow")
        self.assertIn("FAILSAFE_UNCLEAR_INPUT", res.triggered_rules)

    # --------------------------------------------------------------------------
    # 2. CARDIAC EMERGENCIES & MULTILINGUAL MATCHING (RED)
    # --------------------------------------------------------------------------

    def test_04_hindi_only_chest_pain_with_breathlessness_red(self):
        """Hindi Devanagari chest pain with breathlessness must return RED Cardiology."""
        req = UrgencyAssessmentRequest(
            structured_symptoms=[],
            raw_text="सीने में बहुत तेज दर्द है और सांस लेने में भारी दिक्कत हो रही है",
            screening_flags=[]
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "red")
        self.assertIn("RED_CHEST_CARDIAC", res.triggered_rules)
        self.assertEqual(res.required_specialty, "Cardiology")
        self.assertIn("myocardial infarction", res.reason.lower())

    def test_05_hinglish_chest_pain_with_sweating_red(self):
        """Hinglish chest pain with cold sweating must return RED Cardiology."""
        req = UrgencyAssessmentRequest(
            structured_symptoms=[],
            raw_text="kal raat se seene me dard ho raha hai aur thanda pasina aa raha hai bohot",
            screening_flags=[]
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "red")
        self.assertIn("RED_CHEST_CARDIAC", res.triggered_rules)
        self.assertEqual(res.required_specialty, "Cardiology")

    def test_06_chest_pain_with_left_arm_radiation_red(self):
        """Structured chest pain with left arm radiation must return RED Cardiology."""
        req = UrgencyAssessmentRequest(
            structured_symptoms=["chest_pain", "left_arm_pain"],
            raw_text="baye hath me dard uth raha hai"
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "red")
        self.assertIn("RED_CHEST_CARDIAC", res.triggered_rules)
        self.assertEqual(res.required_specialty, "Cardiology")

    # --------------------------------------------------------------------------
    # 3. DUAL-SOURCE PROTECTION: DANGER SIGN ONLY IN RAW TEXT
    # --------------------------------------------------------------------------

    def test_07_llm_misses_danger_sign_present_in_raw_text_triggers_red(self):
        """If Layer 4 LLM only extracted 'mild fever', but raw text contains loss of consciousness, return RED."""
        req = UrgencyAssessmentRequest(
            structured_symptoms=["mild_fever"],
            raw_text="Patient ko bukhar tha lekin achanak behosh ho gaye the aur hosh nahi tha",
            screening_flags=[]
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "red")
        self.assertIn("RED_NEURO_CRITICAL", res.triggered_rules)
        self.assertEqual(res.required_specialty, "Emergency/Neurology")

    # --------------------------------------------------------------------------
    # 4. OCULAR EMERGENCIES (RED) vs MILD CONJUNCTIVITIS (YELLOW)
    # --------------------------------------------------------------------------

    def test_08_acute_ocular_emergency_red_ophthalmology(self):
        """Acute red eye with severe pain, reduced vision, and light sensitivity triggers RED Ophthalmology."""
        req = UrgencyAssessmentRequest(
            structured_symptoms=["eye_redness", "severe_eye_pain", "reduced_vision"],
            raw_text="aankh me tez dard hai aur roshni se takleef ho rahi hai achanak shuru hua",
            screening_flags=["eye_redness_flag"]
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "red")
        self.assertIn("RED_OCULAR_EMERGENCY", res.triggered_rules)
        self.assertEqual(res.required_specialty, "Ophthalmology")
        self.assertIn("glaucoma", res.reason.lower())

    def test_09_mild_conjunctivitis_yellow_ophthalmology(self):
        """Mild eye redness with watering and NO pain/vision loss triggers YELLOW Ophthalmology."""
        req = UrgencyAssessmentRequest(
            structured_symptoms=["eye_redness", "mild_eye_redness_watering"],
            raw_text="aankh me halki lali hai aur paani nikal raha hai",
            screening_flags=["eye_redness_flag"]
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "yellow")
        self.assertIn("YELLOW_MILD_CONJUNCTIVITIS", res.triggered_rules)
        self.assertEqual(res.required_specialty, "Ophthalmology")

    # --------------------------------------------------------------------------
    # 5. PREGNANCY & OBSTETRIC DANGER SIGNS (RED)
    # --------------------------------------------------------------------------

    def test_10_pregnancy_severe_headache_and_blurred_vision_red(self):
        """Pregnant patient with pre-eclampsia signs (headache + blurred vision) triggers RED Obstetrics."""
        req = UrgencyAssessmentRequest(
            structured_symptoms=[],
            raw_text="Main garbhavati hoon, sar me bohot tez dard hai aur aankhon ke aage andhera chha raha hai",
            patient=PatientContext(age=25, is_pregnant=True)
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "red")
        self.assertIn("RED_PREGNANCY_DANGER", res.triggered_rules)
        self.assertEqual(res.required_specialty, "Obstetrics")
        self.assertIn("pre-eclampsia", res.reason.lower())

    def test_11_pregnancy_reduced_fetal_movement_red(self):
        """Pregnant patient with reduced fetal movements triggers RED Obstetrics."""
        req = UrgencyAssessmentRequest(
            structured_symptoms=["reduced_fetal_movement"],
            raw_text="pet me bachha hil nahi raha hai kal subah se",
            patient=PatientContext(age=28, is_pregnant=True)
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "red")
        self.assertIn("RED_PREGNANCY_DANGER", res.triggered_rules)
        self.assertEqual(res.required_specialty, "Obstetrics")

    def test_12_pregnancy_heavy_bleeding_red(self):
        """Heavy bleeding in pregnancy triggers RED Obstetrics."""
        req = UrgencyAssessmentRequest(
            raw_text="pregnant aurat ko bhaari bleeding ho rahi hai bohot khoon nikal raha hai",
            patient=PatientContext(age=24, is_pregnant=True)
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "red")
        self.assertIn("RED_PREGNANCY_DANGER", res.triggered_rules)
        self.assertEqual(res.required_specialty, "Obstetrics")

    # --------------------------------------------------------------------------
    # 6. NEUROLOGICAL & RESPIRATORY EMERGENCIES (RED)
    # --------------------------------------------------------------------------

    def test_13_acute_stroke_signs_red_neurology(self):
        """Unilateral weakness and slurred speech trigger RED Neurology (acute stroke)."""
        req = UrgencyAssessmentRequest(
            raw_text="achanak se ek taraf lakwa mar gaya aur boli ladkhada rahi hai bol nahi pa rahe",
            patient=PatientContext(age=62)
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "red")
        self.assertIn("RED_NEURO_CRITICAL", res.triggered_rules)
        self.assertEqual(res.required_specialty, "Emergency/Neurology")

    def test_14_respiratory_distress_blue_lips_red(self):
        """Cyanosis (blue lips) or severe breathlessness triggers RED Emergency/General."""
        req = UrgencyAssessmentRequest(
            raw_text="mareez ke honth neele pad rahe hain aur saans nahi aa rahi",
            patient=PatientContext(age=55)
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "red")
        self.assertIn("RED_RESPIRATORY_CRITICAL", res.triggered_rules)
        self.assertEqual(res.required_specialty, "Emergency/General")

    def test_15_trauma_and_profuse_hemorrhage_red(self):
        """Major trauma or severe bleeding triggers RED Emergency/Surgery."""
        req = UrgencyAssessmentRequest(
            raw_text="bada accident ho gaya gehra ghaav hai aur khoon ruk nahi raha",
            patient=PatientContext(age=35)
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "red")
        self.assertIn("RED_TRAUMA_HEMORRHAGE", res.triggered_rules)
        self.assertEqual(res.required_specialty, "Emergency/Surgery")

    # --------------------------------------------------------------------------
    # 7. PEDIATRIC IMCI DANGER SIGNS (<5 YEARS) (RED)
    # --------------------------------------------------------------------------

    def test_16_child_under_5_convulsions_fits_red(self):
        """Child under 5 with fits/convulsions triggers RED Pediatrics IMCI."""
        req = UrgencyAssessmentRequest(
            raw_text="2 saal ka bachha hai, jhatke aa rahe hain aur doodh nahi pee raha",
            patient=PatientContext(age=2, is_pregnant=False)
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "red")
        self.assertIn("RED_PEDIATRIC_IMCI_DANGER", res.triggered_rules)
        self.assertEqual(res.required_specialty, "Pediatrics")

    def test_17_child_under_5_fever_and_stiff_neck_red(self):
        """Child under 5 with high fever and neck stiffness triggers RED Pediatrics."""
        req = UrgencyAssessmentRequest(
            structured_symptoms=["high_fever", "stiff_neck"],
            raw_text="bachhe ki gardan akdna aur tez bukhar hai",
            patient=PatientContext(age=3)
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "red")
        self.assertIn("RED_PEDIATRIC_FEVER_MENINGISM", res.triggered_rules)
        self.assertEqual(res.required_specialty, "Pediatrics")

    # --------------------------------------------------------------------------
    # 8. DEMOGRAPHIC MODIFIER ESCALATIONS (YELLOW -> RED)
    # --------------------------------------------------------------------------

    def test_18_modifier_escalates_yellow_fever_to_red_for_child_under_5(self):
        """Prolonged fever (>3d) is normally YELLOW, but child under 5 must escalate to RED Pediatrics."""
        req = UrgencyAssessmentRequest(
            structured_symptoms=["fever_over_3_days"],
            patient=PatientContext(age=3.5, is_pregnant=False)
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "red")
        self.assertIn("YELLOW_PROLONGED_FEVER", res.triggered_rules)
        self.assertEqual(res.required_specialty, "Pediatrics")
        self.assertIn("Escalated to RED", res.reason)

    def test_19_prolonged_fever_adult_remains_yellow(self):
        """Prolonged fever in normal adult (35y) remains YELLOW General Medicine."""
        req = UrgencyAssessmentRequest(
            raw_text="char din se bukhar chal raha hai",
            patient=PatientContext(age=35, is_pregnant=False)
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "yellow")
        self.assertIn("YELLOW_PROLONGED_FEVER", res.triggered_rules)
        self.assertEqual(res.required_specialty, "General Medicine")

    def test_20_modifier_escalates_dehydration_to_red_for_elderly(self):
        """Persistent diarrhea (>2d) is YELLOW for adults, but escalates to RED for elderly >60."""
        req = UrgencyAssessmentRequest(
            raw_text="dada ji ko teen din se dast ho rahe hain",
            patient=PatientContext(age=72, is_pregnant=False)
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "red")
        self.assertIn("YELLOW_GI_PERSISTENT", res.triggered_rules)
        self.assertIn("Escalated to RED", res.reason)

    def test_21_modifier_escalates_pallor_to_red_for_pregnant_patient(self):
        """Pallor is YELLOW for adults, but escalates to RED Obstetrics for pregnant patient."""
        req = UrgencyAssessmentRequest(
            screening_flags=["pallor_screening_flag"],
            raw_text="aankh me peelapan lag raha hai",
            patient=PatientContext(age=23, is_pregnant=True)
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "red")
        self.assertIn("YELLOW_PALLOR_FATIGUE", res.triggered_rules)
        self.assertEqual(res.required_specialty, "Obstetrics")
        self.assertIn("Escalated to RED", res.reason)

    # --------------------------------------------------------------------------
    # 9. SCREENING FLAGS & DERMATOLOGY (YELLOW)
    # --------------------------------------------------------------------------

    def test_22_screening_flag_pallor_general_adult_yellow(self):
        """Layer 3 pallor screening flag for non-pregnant adult returns YELLOW General Medicine."""
        req = UrgencyAssessmentRequest(
            screening_flags=["pallor_screening_flag"],
            raw_text="bahut thakan lagti hai",
            patient=PatientContext(age=40, is_pregnant=False)
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "yellow")
        self.assertIn("YELLOW_PALLOR_FATIGUE", res.triggered_rules)
        self.assertEqual(res.required_specialty, "General Medicine (blood test)")

    def test_23_spreading_skin_rash_yellow_dermatology(self):
        """Spreading rash triggers YELLOW Dermatology."""
        req = UrgencyAssessmentRequest(
            raw_text="shareer par lal daane phail rahe hain teen din se",
            patient=PatientContext(age=25)
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "yellow")
        self.assertIn("YELLOW_SPREADING_RASH", res.triggered_rules)
        self.assertEqual(res.required_specialty, "Dermatology")

    # --------------------------------------------------------------------------
    # 10. MILD / GREEN HOME-CARE VERDICT
    # --------------------------------------------------------------------------

    def test_24_mild_cold_cough_returns_green(self):
        """Mild symptoms without any red/yellow danger signs return GREEN home care."""
        req = UrgencyAssessmentRequest(
            structured_symptoms=["mild_cough", "mild_cold"],
            raw_text="kal se halki khansi aur halka jukam hai",
            patient=PatientContext(age=30, is_pregnant=False)
        )
        res = self.engine.evaluate(req)
        self.assertEqual(res.urgency, "green")
        self.assertEqual(res.triggered_rules, [])
        self.assertIsNone(res.required_specialty)
        self.assertIsNone(res.follow_up_question)
        self.assertIn("mild", res.reason.lower())

    # --------------------------------------------------------------------------
    # 11. CONFIG-DRIVEN DYNAMICS (Editing rules.yaml changes behavior without code changes)
    # --------------------------------------------------------------------------

    def test_25_config_driven_custom_rule_evaluation(self):
        """Instantiating engine with a custom YAML file verifies purely config-driven execution."""
        custom_rules_data = {
            "version": "test",
            "rules": [
                {
                    "id": "CUSTOM_EAR_EMERGENCY",
                    "level": "red",
                    "all_of": ["ear_bleeding"],
                    "specialty": "ENT",
                    "action": "Immediate ENT consultation.",
                    "reason": "Bleeding from ear indicates temporal bone fracture."
                }
            ]
        }
        custom_keywords_data = {
            "version": "test",
            "keywords": {
                "ear_bleeding": {
                    "english": ["ear bleeding"],
                    "hindi": ["कान से खून"],
                    "hinglish": ["kaan se khoon"]
                }
            }
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            rf = Path(tmpdir) / "rules.yaml"
            kf = Path(tmpdir) / "keywords.yaml"
            with open(rf, "w") as f:
                yaml.safe_dump(custom_rules_data, f)
            with open(kf, "w") as f:
                yaml.safe_dump(custom_keywords_data, f)

            dynamic_engine = SafetyRuleEngine(rules_path=str(rf), keywords_path=str(kf))
            
            # Test that new custom rule triggers RED without any code modifications
            req = UrgencyAssessmentRequest(raw_text="kaan se khoon nikal raha hai")
            res = dynamic_engine.evaluate(req)
            self.assertEqual(res.urgency, "red")
            self.assertIn("CUSTOM_EAR_EMERGENCY", res.triggered_rules)
            self.assertEqual(res.required_specialty, "ENT")

    # --------------------------------------------------------------------------
    # 12. FASTAPI HTTP ROUTE VERIFICATION (POST /assess-urgency)
    # --------------------------------------------------------------------------

    def test_26_fastapi_http_endpoint_post_assess_urgency(self):
        """Verify POST /assess-urgency returns 200 and schema compliant JSON."""
        payload = {
            "structured_symptoms": ["chest_pain"],
            "raw_text": "seene me tez dard aur saans lene me dikkat",
            "screening_flags": [],
            "patient": {"age": 54, "is_pregnant": False}
        }
        response = self.client.post("/assess-urgency", json=payload)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["urgency"], "red")
        self.assertIn("RED_CHEST_CARDIAC", data["triggered_rules"])
        self.assertEqual(data["required_specialty"], "Cardiology")
        self.assertIn("reason", data)
        self.assertIn("recommended_action", data)


if __name__ == "__main__":
    unittest.main()
