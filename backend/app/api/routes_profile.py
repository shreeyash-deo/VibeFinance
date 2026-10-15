"""
backend/app/api/routes_profile.py - User Profile & Persona Management
"""

from fastapi import APIRouter, Depends, HTTPException
from backend.app.deps import get_current_user_id
from backend.app.schemas.profile import UserProfileSchema
from backend.app.graph.runner import DEFAULT_PERSONAS

router = APIRouter(tags=["Profile"])

@router.get("/personas")
async def list_personas():
    """Returns all 3 seeded demo personas."""
    return list(DEFAULT_PERSONAS.values())

@router.get("/me/profile", response_model=UserProfileSchema)
async def get_my_profile(current_user_id: str = Depends(get_current_user_id)):
    """Returns profile for the active persona."""
    slug = current_user_id.lower()
    if slug not in DEFAULT_PERSONAS:
        slug = "meena"
    p = DEFAULT_PERSONAS[slug]
    return UserProfileSchema(**p)

@router.put("/me/profile", response_model=UserProfileSchema)
async def update_my_profile(profile_data: UserProfileSchema, current_user_id: str = Depends(get_current_user_id)):
    """Updates profile in memory for active persona."""
    slug = current_user_id.lower()
    if slug in DEFAULT_PERSONAS:
        DEFAULT_PERSONAS[slug].update(profile_data.model_dump(exclude_unset=True))
    return profile_data

@router.post("/demo/persona/{name}")
async def switch_persona(name: str):
    """Switch active demo persona slug."""
    slug = name.lower()
    if slug not in DEFAULT_PERSONAS:
        raise HTTPException(status_code=404, detail=f"Persona '{name}' not found. Valid: meena, arjun, rohan")
    return {
        "status": "switched",
        "active_persona": slug,
        "profile": DEFAULT_PERSONAS[slug]
    }

