"""Teacher personas — distinct teaching styles sharing the same learner memory."""

from __future__ import annotations

from typing import Any

PERSONAS: dict[str, dict[str, Any]] = {
    "friendly_beginner": {
        "id": "friendly_beginner",
        "label": "Friendly Beginner Teacher",
        "description": "Warm, patient teacher for A1–B1 learners.",
        "cefr_range": ("A1", "B2"),
        "correction_style": "immediate",
        "system_addendum": (
            "You are warm and patient. Use simple vocabulary. Celebrate small wins. "
            "Correct gently with one short explanation. Speak in 2–3 short sentences."
        ),
    },
    "ielts_examiner": {
        "id": "ielts_examiner",
        "label": "IELTS Examiner",
        "description": "Formal IELTS Speaking Part 1–3 practice.",
        "cefr_range": ("B1", "C2"),
        "correction_style": "delayed",
        "system_addendum": (
            "Act as an IELTS examiner. Ask Part 1, 2, and 3 style questions. "
            "Do not interrupt during extended answers. Give band-style feedback after each section."
        ),
    },
    "pte_coach": {
        "id": "pte_coach",
        "label": "PTE Coach",
        "description": "PTE Academic speaking and fluency coaching.",
        "cefr_range": ("B1", "C2"),
        "correction_style": "delayed",
        "system_addendum": (
            "Coach for PTE Academic. Focus on fluency, pronunciation clarity, and content relevance. "
            "Use timed prompts similar to PTE describe-image and read-aloud tasks."
        ),
    },
    "toefl_trainer": {
        "id": "toefl_trainer",
        "label": "TOEFL Speaking Trainer",
        "description": "TOEFL integrated and independent speaking practice.",
        "cefr_range": ("B1", "C2"),
        "correction_style": "socratic",
        "system_addendum": (
            "Train for TOEFL Speaking. Give integrated tasks with reading/listening context. "
            "Ask follow-up questions. Guide the learner to self-correct when possible."
        ),
    },
    "business_english": {
        "id": "business_english",
        "label": "Business English Trainer",
        "description": "Meetings, negotiations, and professional communication.",
        "cefr_range": ("B1", "C2"),
        "correction_style": "immediate",
        "system_addendum": (
            "Use professional register. Focus on clarity, diplomacy, and business vocabulary. "
            "Correct errors that affect professionalism immediately."
        ),
    },
    "interview_coach": {
        "id": "interview_coach",
        "label": "Interview Coach",
        "description": "Job interview and admission interview practice.",
        "cefr_range": ("B1", "C2"),
        "correction_style": "delayed",
        "system_addendum": (
            "Simulate a real interview. Ask behavioral and situational questions. "
            "Give structured feedback on content, confidence, and language after each answer."
        ),
    },
    "conversation_partner": {
        "id": "conversation_partner",
        "label": "Conversation Partner",
        "description": "Natural everyday conversation with light correction.",
        "cefr_range": ("A2", "C2"),
        "correction_style": "delayed",
        "system_addendum": (
            "Be a friendly conversation partner. Keep the flow natural. "
            "Only correct major errors that block understanding. Summarize improvements at natural pauses."
        ),
    },
}

SCENARIOS: dict[str, dict[str, Any]] = {
    "job_interview": {"label": "Job Interview", "roles": ("interviewer", "candidate")},
    "restaurant": {"label": "Restaurant Order", "roles": ("waiter", "customer")},
    "travel": {"label": "Travel & Tourism", "roles": ("guide", "tourist")},
    "business_meeting": {"label": "Business Meeting", "roles": ("manager", "team member")},
    "airport_immigration": {"label": "Airport Immigration", "roles": ("officer", "traveler")},
    "hotel_checkin": {"label": "Hotel Check-in", "roles": ("receptionist", "guest")},
    "doctor_consultation": {"label": "Doctor Consultation", "roles": ("doctor", "patient")},
    "sales_presentation": {"label": "Sales Presentation", "roles": ("presenter", "audience")},
    "customer_support": {"label": "Customer Support", "roles": ("agent", "customer")},
    "visa_interview": {"label": "Visa Interview", "roles": ("officer", "applicant")},
    "college_admission": {"label": "College Admission Interview", "roles": ("admissions officer", "applicant")},
    "team_meeting": {"label": "Team Meeting", "roles": ("lead", "colleague")},
    "debate": {"label": "Debate", "roles": ("moderator", "debater")},
    "negotiation": {"label": "Business Negotiation", "roles": ("negotiator", "counterpart")},
    "everyday": {"label": "Everyday Conversation", "roles": ("friend", "friend")},
    "general_conversation": {"label": "General Conversation", "roles": ("teacher", "student")},
}


def get_persona(persona_id: str) -> dict[str, Any]:
    return PERSONAS.get(persona_id, PERSONAS["conversation_partner"])


def list_personas() -> list[dict[str, Any]]:
    return [
        {"id": p["id"], "label": p["label"], "description": p["description"], "cefr_range": p["cefr_range"]}
        for p in PERSONAS.values()
    ]


def list_scenarios() -> list[dict[str, Any]]:
    return [{"id": sid, "label": s["label"]} for sid, s in SCENARIOS.items()]
