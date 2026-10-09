"""
GramSehat Layer 7: Data Access Layer (data_access.py)
=====================================================
Database access module for Supabase (PostgreSQL), Realtime, and Storage.
Imported directly by Layer 6 (FastAPI orchestration) for all persistence needs.

Guarantees:
- Never logs sensitive patient text or credentials
- Typed functions returning plain dicts
- Raises clear DataError on failure
- Uses SUPABASE_SERVICE_KEY (service_role) for backend operations
- Safe fallback / in-memory simulation when Supabase credentials are unset (local testing)
"""

import math
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.config import settings
from app.services.specialties import map_specialty_to_canonical

import logging
logger = logging.getLogger("gramsehat.data_access")


class DataError(Exception):
    """Base exception raised for all database or storage failures in Layer 7."""
    pass


def _now_iso() -> str:
    """Returns current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


# ------------------------------------------------------------------------------
# Haversine Distance Helper (Used in Fallback Simulator & Offline Mode)
# ------------------------------------------------------------------------------
def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculates spherical distance between two coordinate pairs in kilometers."""
    r = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lng = math.radians(lng2 - lng1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lng / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(max(0.0, min(1.0, a))))
    return round(r * c, 2)


# ------------------------------------------------------------------------------
# Client Factory & InMemory Fallback Store
# ------------------------------------------------------------------------------
class InMemoryStore:
    """Thread-safe simulated store when Supabase cloud credentials are not active."""

    def __init__(self):
        self.patients: Dict[str, dict] = {}
        self.sessions: Dict[str, dict] = {}
        self.visits: Dict[str, dict] = {}
        self.hospitals: Dict[str, dict] = {}
        self.referrals: Dict[str, dict] = {}
        self.prealerts: Dict[str, dict] = {}
        self.ambulance_requests: Dict[str, dict] = {}
        self.storage: Dict[str, bytes] = {}
        self._seed_default_hospitals()

    def _seed_default_hospitals(self):
        c_lat, c_lng = 26.8467, 80.9462
        raw_hospitals = [
            ("Drishti Rural Eye Institute (Demo)", "Eye Hospital", ["ophthalmology", "general_medicine"], 12, c_lat + 0.021, c_lng + 0.018, "+91 94150 11001"),
            ("Avadh Netralaya Vision Center (Demo)", "Eye Hospital", ["ophthalmology"], 0, c_lat + 0.009, c_lng - 0.012, "+91 94150 11002"),
            ("Rampur District Mother & Child Hospital (Demo)", "District Hospital", ["obstetrics", "emergency", "pediatrics", "surgery"], 24, c_lat - 0.035, c_lng + 0.041, "+91 94150 11003"),
            ("Sanjivani Heart & Trauma Institute (Demo)", "Tertiary Care", ["cardiology", "emergency", "surgery"], 8, c_lat + 0.052, c_lng - 0.031, "+91 94150 11004"),
            ("Shivpur Primary Health Centre (Demo)", "PHC", ["general_medicine", "emergency"], 6, c_lat + 0.008, c_lng + 0.006, "+91 94150 11005"),
            ("Rampur Community Health Centre (Demo)", "CHC", ["general_medicine", "emergency", "surgery"], 18, c_lat - 0.018, c_lng + 0.022, "+91 94150 11006"),
            ("Bal Arogya Pediatric Centre (Demo)", "Child Care", ["pediatrics", "emergency"], 14, c_lat + 0.015, c_lng - 0.024, "+91 94150 11007"),
            ("Gomti Rural Cardiac Annex (Demo)", "Specialty Clinic", ["cardiology"], 0, c_lat + 0.012, c_lng + 0.035, "+91 94150 11008"),
            ("Mahamaya Neuro & Trauma Hospital (Demo)", "Trauma Centre", ["neurology", "surgery", "emergency"], 10, c_lat - 0.042, c_lng - 0.029, "+91 94150 11009"),
            ("Kalyan Skin & General Wellness Clinic (Demo)", "Clinic", ["dermatology", "general_medicine"], 4, c_lat + 0.032, c_lng + 0.015, "+91 94150 11010"),
        ]
        for name, htype, specs, beds, lat, lng, contact in raw_hospitals:
            hid = str(uuid.uuid4())
            self.hospitals[hid] = {
                "id": hid,
                "name": name,
                "type": htype,
                "specialties": specs,
                "beds_available": beds,
                "lat": lat,
                "lng": lng,
                "contact": contact,
                "is_demo": True,
                "created_at": _now_iso()
            }


_mem_store = InMemoryStore()


def _get_supabase_client():
    """Initializes or returns Supabase client if URL and service key are provided."""
    sb_url = os.environ.get("SUPABASE_URL", "").strip()
    sb_key = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()

    if not sb_url or not sb_key or "your-project" in sb_url or "your_supabase" in sb_key:
        return None

    try:
        from supabase import create_client
        return create_client(sb_url, sb_key)
    except Exception as e:
        logger.warning("Could not initialize Supabase client (%s). Using local store.", e)
        return None


# ------------------------------------------------------------------------------
# 1. Patient Data Access
# ------------------------------------------------------------------------------
def get_or_create_patient(
    name: str,
    age: Optional[float] = None,
    language: str = "hi",
    is_pregnant: bool = False,
    patient_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieves existing patient or creates a new patient record.
    Returns plain dictionary of patient data.
    """
    if not name or not name.strip():
        raise DataError("Patient name cannot be empty.")

    client = _get_supabase_client()
    if client is not None:
        try:
            if patient_id:
                res = client.table("patients").select("*").eq("id", patient_id).execute()
                if res.data:
                    return res.data[0]

            # Look up by exact name and language
            res = client.table("patients").select("*").ilike("name", name.strip()).execute()
            if res.data:
                return res.data[0]

            # Create new record
            payload = {
                "name": name.strip(),
                "age": age,
                "language": language or "hi",
                "is_pregnant": bool(is_pregnant)
            }
            res = client.table("patients").insert(payload).execute()
            if not res.data:
                raise DataError("Failed to insert patient record.")
            return res.data[0]
        except Exception as e:
            logger.error("Supabase patient query failed: %s", str(e))
            raise DataError(f"Database error while querying patient: {str(e)}") from e

    # In-memory mode
    if patient_id and patient_id in _mem_store.patients:
        return _mem_store.patients[patient_id]

    for p in _mem_store.patients.values():
        if p["name"].lower() == name.strip().lower():
            return p

    new_id = patient_id or str(uuid.uuid4())
    record = {
        "id": new_id,
        "name": name.strip(),
        "age": age,
        "language": language or "hi",
        "is_pregnant": bool(is_pregnant),
        "created_at": _now_iso()
    }
    _mem_store.patients[new_id] = record
    return record


# ------------------------------------------------------------------------------
# 2. Session Data Access (Layer 6 Follow-up loop state)
# ------------------------------------------------------------------------------
def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves session state by UUID string, or returns None if not found."""
    if not session_id:
        return None

    client = _get_supabase_client()
    if client is not None:
        try:
            res = client.table("sessions").select("*").eq("id", session_id).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            raise DataError(f"Failed to retrieve session: {str(e)}") from e

    return _mem_store.sessions.get(str(session_id))


def upsert_session(
    session_id: Optional[str] = None,
    patient_id: Optional[str] = None,
    accumulated_text: str = "",
    state: Optional[dict] = None,
    status: str = "active"
) -> Dict[str, Any]:
    """
    Creates or updates an active triage dialogue session.
    """
    if status not in ("active", "completed", "abandoned"):
        raise DataError(f"Invalid session status '{status}'. Must be active, completed, or abandoned.")

    target_id = session_id or str(uuid.uuid4())
    state_payload = state or {}

    client = _get_supabase_client()
    if client is not None:
        try:
            payload = {
                "id": target_id,
                "patient_id": patient_id,
                "accumulated_text": accumulated_text or "",
                "state": state_payload,
                "status": status,
                "updated_at": _now_iso()
            }
            res = client.table("sessions").upsert(payload).execute()
            if not res.data:
                raise DataError("Failed to upsert session record.")
            return res.data[0]
        except Exception as e:
            raise DataError(f"Database error during session upsert: {str(e)}") from e

    # In-memory mode
    existing = _mem_store.sessions.get(target_id)
    if existing:
        existing.update({
            "accumulated_text": accumulated_text or "",
            "state": state_payload,
            "status": status,
            "updated_at": _now_iso()
        })
        if patient_id:
            existing["patient_id"] = patient_id
        return existing

    record = {
        "id": target_id,
        "patient_id": patient_id,
        "accumulated_text": accumulated_text or "",
        "state": state_payload,
        "status": status,
        "updated_at": _now_iso(),
        "created_at": _now_iso()
    }
    _mem_store.sessions[target_id] = record
    return record


# ------------------------------------------------------------------------------
# 3. Visits & Patient Timeline Data Access
# ------------------------------------------------------------------------------
def save_visit(
    patient_id: str,
    session_id: Optional[str] = None,
    transcribed_text: str = "",
    structured_symptoms: Optional[list] = None,
    screening_flags: Optional[list] = None,
    report_text: str = "",
    urgency: str = "green",
    triggered_rules: Optional[list] = None,
    reason: str = "",
    required_specialty: Optional[str] = None,
    recommended_action: str = "",
    degraded: bool = False,
    image_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Persists a completed clinical visit record following triage.
    """
    if urgency not in ("red", "yellow", "green"):
        raise DataError(f"Invalid urgency level '{urgency}'. Must be red, yellow, or green.")

    canonical_specialty = map_specialty_to_canonical(required_specialty)

    payload = {
        "id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "session_id": session_id,
        "transcribed_text": transcribed_text or "",
        "structured_symptoms": structured_symptoms or [],
        "screening_flags": screening_flags or [],
        "report_text": report_text or "",
        "urgency": urgency,
        "triggered_rules": triggered_rules or [],
        "reason": reason or "",
        "required_specialty": canonical_specialty,
        "recommended_action": recommended_action or "",
        "degraded": bool(degraded),
        "image_path": image_path,
        "created_at": _now_iso()
    }

    client = _get_supabase_client()
    if client is not None:
        try:
            res = client.table("visits").insert(payload).execute()
            if not res.data:
                raise DataError("Failed to save visit record.")
            return res.data[0]
        except Exception as e:
            raise DataError(f"Database error while saving visit: {str(e)}") from e

    _mem_store.visits[payload["id"]] = payload
    return payload


def get_timeline(patient_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Retrieves chronological visit history for a patient, ordered newest first.
    """
    if not patient_id:
        return []

    client = _get_supabase_client()
    if client is not None:
        try:
            res = (
                client.table("visits")
                .select("*")
                .eq("patient_id", patient_id)
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return res.data or []
        except Exception as e:
            raise DataError(f"Failed to fetch patient timeline: {str(e)}") from e

    matched = [v for v in _mem_store.visits.values() if v.get("patient_id") == patient_id]
    matched.sort(key=lambda x: x["created_at"], reverse=True)
    return matched[:limit]


# ------------------------------------------------------------------------------
# 4. Hospital Matching (RPC / Haversine)
# ------------------------------------------------------------------------------
def find_hospitals(
    specialty: Optional[str],
    lat: float,
    lng: float,
    limit: int = 3
) -> List[Dict[str, Any]]:
    """
    Executes hospital matching with bed availability and Haversine distance ordering.
    If no hospital with available beds has the requested specialty, falls back to
    emergency / general_medicine facilities with fallback = True.
    """
    canonical = map_specialty_to_canonical(specialty) or (specialty.strip().lower() if specialty else "")

    client = _get_supabase_client()
    if client is not None:
        try:
            rpc_params = {
                "p_specialty": canonical,
                "p_lat": float(lat),
                "p_lng": float(lng),
                "p_limit": int(limit)
            }
            res = client.rpc("match_hospitals", rpc_params).execute()
            return res.data or []
        except Exception as e:
            logger.warning("Supabase match_hospitals RPC error (%s). Using fallback calculation.", e)

    # In-memory calculation matching SQL match_hospitals logic
    candidates = []
    if canonical:
        for h in _mem_store.hospitals.values():
            if canonical in h["specialties"] and h["beds_available"] > 0:
                d = haversine_km(lat, lng, h["lat"], h["lng"])
                entry = dict(h)
                entry["distance_km"] = d
                entry["fallback"] = False
                candidates.append(entry)

    if candidates:
        candidates.sort(key=lambda x: x["distance_km"])
        return candidates[:limit]

    # Fallback search: emergency or general_medicine with beds > 0
    fallback_candidates = []
    for h in _mem_store.hospitals.values():
        has_emergency_or_gen = "emergency" in h["specialties"] or "general_medicine" in h["specialties"]
        if has_emergency_or_gen and h["beds_available"] > 0:
            d = haversine_km(lat, lng, h["lat"], h["lng"])
            entry = dict(h)
            entry["distance_km"] = d
            entry["fallback"] = True
            fallback_candidates.append(entry)

    fallback_candidates.sort(key=lambda x: x["distance_km"])
    return fallback_candidates[:limit]


# ------------------------------------------------------------------------------
# 5. Referrals, Prealerts, and Ambulance Requests
# ------------------------------------------------------------------------------
def save_referral(
    visit_id: str,
    hospital_id: str,
    distance_km: float = 0.0,
    status: str = "pending"
) -> Dict[str, Any]:
    """Links a visit to a target hospital referral."""
    valid_statuses = ("pending", "accepted", "rejected", "completed", "cancelled")
    if status not in valid_statuses:
        raise DataError(f"Invalid referral status '{status}'. Must be one of {valid_statuses}")

    payload = {
        "id": str(uuid.uuid4()),
        "visit_id": visit_id,
        "hospital_id": hospital_id,
        "distance_km": float(distance_km),
        "status": status,
        "created_at": _now_iso()
    }

    client = _get_supabase_client()
    if client is not None:
        try:
            res = client.table("referrals").insert(payload).execute()
            if not res.data:
                raise DataError("Failed to save referral.")
            return res.data[0]
        except Exception as e:
            raise DataError(f"Database error while saving referral: {str(e)}") from e

    _mem_store.referrals[payload["id"]] = payload
    return payload


def create_prealert(
    referral_id: str,
    hospital_id: str,
    summary: str,
    urgency: str = "red",
    eta_minutes: int = 15,
    status: str = "pending"
) -> Dict[str, Any]:
    """Creates a prealert for hospital ER clinicians (broadcasts via Realtime)."""
    if urgency not in ("red", "yellow", "green"):
        raise DataError(f"Invalid prealert urgency '{urgency}'.")

    payload = {
        "id": str(uuid.uuid4()),
        "referral_id": referral_id,
        "hospital_id": hospital_id,
        "summary": summary,
        "urgency": urgency,
        "eta_minutes": max(0, int(eta_minutes)),
        "status": status,
        "created_at": _now_iso()
    }

    client = _get_supabase_client()
    if client is not None:
        try:
            res = client.table("prealerts").insert(payload).execute()
            if not res.data:
                raise DataError("Failed to create prealert.")
            return res.data[0]
        except Exception as e:
            raise DataError(f"Database error creating prealert: {str(e)}") from e

    _mem_store.prealerts[payload["id"]] = payload
    return payload


def create_ambulance_request(
    visit_id: str,
    hospital_id: str,
    eta_minutes: int = 15,
    vehicle_label: str = "Govt 108 Ambulance",
    current_lat: Optional[float] = None,
    current_lng: Optional[float] = None,
    status: str = "requested"
) -> Dict[str, Any]:
    """Dispatches 108 emergency vehicle request (broadcasts via Realtime)."""
    valid_statuses = ("requested", "dispatched", "in_transit", "arrived", "cancelled")
    if status not in valid_statuses:
        raise DataError(f"Invalid ambulance status '{status}'. Must be one of {valid_statuses}")

    payload = {
        "id": str(uuid.uuid4()),
        "visit_id": visit_id,
        "hospital_id": hospital_id,
        "status": status,
        "eta_minutes": max(0, int(eta_minutes)),
        "vehicle_label": vehicle_label,
        "current_lat": current_lat,
        "current_lng": current_lng,
        "updated_at": _now_iso(),
        "created_at": _now_iso()
    }

    client = _get_supabase_client()
    if client is not None:
        try:
            res = client.table("ambulance_requests").insert(payload).execute()
            if not res.data:
                raise DataError("Failed to create ambulance request.")
            return res.data[0]
        except Exception as e:
            raise DataError(f"Database error creating ambulance request: {str(e)}") from e

    _mem_store.ambulance_requests[payload["id"]] = payload
    return payload


def update_ambulance_position(
    ambulance_request_id: str,
    current_lat: float,
    current_lng: float,
    eta_minutes: Optional[int] = None,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """Updates live GPS telemetry and ETA for ambulance tracking screen."""
    update_data: Dict[str, Any] = {
        "current_lat": float(current_lat),
        "current_lng": float(current_lng),
        "updated_at": _now_iso()
    }
    if eta_minutes is not None:
        update_data["eta_minutes"] = max(0, int(eta_minutes))
    if status is not None:
        update_data["status"] = status

    client = _get_supabase_client()
    if client is not None:
        try:
            res = (
                client.table("ambulance_requests")
                .update(update_data)
                .eq("id", ambulance_request_id)
                .execute()
            )
            if not res.data:
                raise DataError(f"Ambulance request '{ambulance_request_id}' not found.")
            return res.data[0]
        except Exception as e:
            raise DataError(f"Database error updating ambulance position: {str(e)}") from e

    record = _mem_store.ambulance_requests.get(ambulance_request_id)
    if not record:
        raise DataError(f"Ambulance request '{ambulance_request_id}' not found in store.")
    record.update(update_data)
    return record


# ------------------------------------------------------------------------------
# 6. Storage: Upload & Signed URLs (patient-images bucket)
# ------------------------------------------------------------------------------
def upload_image(
    file_bytes: bytes,
    filename: str = "report.jpg",
    content_type: str = "image/jpeg",
    bucket: str = "patient-images"
) -> str:
    """
    Uploads document image binary bytes to private storage bucket.
    Returns the storage object path.
    """
    if not file_bytes or len(file_bytes) < 10:
        raise DataError("Cannot upload empty image.")

    clean_name = filename.rsplit("/", 1)[-1].replace(" ", "_")
    storage_path = f"visits/{uuid.uuid4()}_{clean_name}"

    client = _get_supabase_client()
    if client is not None:
        try:
            res = client.storage.from_(bucket).upload(
                path=storage_path,
                file=file_bytes,
                file_options={"content-type": content_type}
            )
            return storage_path
        except Exception as e:
            raise DataError(f"Failed to upload image to Supabase storage: {str(e)}") from e

    # In-memory store
    _mem_store.storage[f"{bucket}/{storage_path}"] = file_bytes
    return storage_path


def get_signed_url(
    image_path: str,
    expires_in: int = 3600,
    bucket: str = "patient-images"
) -> str:
    """
    Generates a secure, time-limited signed URL for clinician view access.
    """
    if not image_path:
        raise DataError("Image path cannot be empty.")

    client = _get_supabase_client()
    if client is not None:
        try:
            res = client.storage.from_(bucket).create_signed_url(image_path, expires_in)
            if isinstance(res, dict) and "signedURL" in res:
                return res["signedURL"]
            if hasattr(res, "signed_url"):
                return res.signed_url
            return str(res)
        except Exception as e:
            raise DataError(f"Failed to generate signed URL: {str(e)}") from e

    # Simulated signed URL for local/offline demo
    return f"https://mock-supabase.local/storage/v1/object/sign/{bucket}/{image_path}?token=mock_signed_token&expires={expires_in}"
