"""Trip sharing and invite routes for collaborative trip editing."""

from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

from app.models import get_db
from app.models.database import Trip, User, TripInvite
from app.core.security import decode_token as decode_token_core
from app.auth.jwt import decode_token as decode_token_legacy

router = APIRouter(prefix="/sharing", tags=["Sharing"])


def get_current_user_from_cookie(
    authorization: Optional[str] = Header(None),
    timetide_token: str = Cookie(None),
    db: Session = Depends(get_db)
):
    """Extract and validate user from cookie or Authorization header."""
    token = None
    
    # Try Authorization header first (Bearer token)
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]  # Remove "Bearer " prefix
    # Fall back to cookie
    elif timetide_token:
        token = timetide_token
    
    if not token:
        print("DEBUG: No token found in request")
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user_data = None
    core_error = None
    legacy_error = None
    
    try:
        user_data = decode_token_core(token)
        print(f"DEBUG: decode_token_core succeeded, user_data type: {type(user_data)}")
    except Exception as e:
        core_error = str(e)
        print(f"DEBUG: decode_token_core failed: {core_error}")
        try:
            user_data = decode_token_legacy(token)
            print(f"DEBUG: decode_token_legacy succeeded, user_data type: {type(user_data)}")
        except Exception as e2:
            legacy_error = str(e2)
            print(f"DEBUG: decode_token_legacy failed: {legacy_error}")
    
    if not user_data:
        print(f"DEBUG: user_data is None/empty. Core error: {core_error}, Legacy error: {legacy_error}")
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = user_data.get('sub')
    print(f"DEBUG: Extracted user_id from token: {user_id}")
    
    if user_id:
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            pass
    
    if not user_id:
        print(f"DEBUG: No user_id in token data. Data: {user_data}")
        raise HTTPException(status_code=401, detail="Invalid token - no user_id")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        print(f"DEBUG: User not found in database with id: {user_id}")
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"DEBUG: Auth successful for user: {user.email}")
    return user


# Pydantic schemas
class ShareTripRequest(BaseModel):
    """Request schema for sharing a trip."""
    email: EmailStr
    permission_level: str = "editor"  # 'viewer' or 'editor'


class TripInviteOut(BaseModel):
    """Response schema for trip invites."""
    id: int
    trip_id: int
    trip_title: str
    inviter_id: int
    inviter_name: str
    invitee_id: int
    status: str
    permission_level: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class SharedTripOut(BaseModel):
    """Response schema for shared trips."""
    id: int
    title: str
    location: str
    start_date: str
    end_date: str
    cover_image: Optional[str]
    owner_id: int
    owner_name: str
    permission_level: str
    
    class Config:
        from_attributes = True


# Routes

@router.post("/trips/{trip_id}/share")
async def share_trip(
    trip_id: int,
    payload: ShareTripRequest,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Share a trip by sending an invite to another user's email."""
    
    try:
        # Verify trip ownership
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        if trip.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only share your own trips")
        
        # Find user by email
        invitee = db.query(User).filter(User.email == payload.email).first()
        if not invitee:
            raise HTTPException(status_code=404, detail=f"User with email {payload.email} not found")
        
        if invitee.id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot share trip with yourself")
        
        # Check if invite already exists
        existing_invite = db.query(TripInvite).filter(
            TripInvite.trip_id == trip_id,
            TripInvite.invitee_id == invitee.id,
            TripInvite.status == "pending"
        ).first()
        
        if existing_invite:
            raise HTTPException(status_code=400, detail="Invite already exists for this user")
        
        # Validate permission level
        if payload.permission_level not in ["viewer", "editor"]:
            raise HTTPException(status_code=400, detail="Invalid permission level")
        
        # Create invite
        invite = TripInvite(
            trip_id=trip_id,
            inviter_id=current_user.id,
            invitee_id=invitee.id,
            permission_level=payload.permission_level,
            status="pending"
        )
        db.add(invite)
        db.commit()
        db.refresh(invite)
        
        return {
            "id": invite.id,
            "trip_id": invite.trip_id,
            "trip_title": trip.title,
            "inviter_id": invite.inviter_id,
            "inviter_name": current_user.name,
            "invitee_id": invite.invitee_id,
            "status": invite.status,
            "permission_level": invite.permission_level,
            "created_at": invite.created_at,
            "message": f"Invite sent to {payload.email}"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in share_trip: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sharing trip: {str(e)}")


@router.get("/invites")
async def get_invites(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Get all invites for the current user, grouped by status."""
    
    try:
        query = db.query(TripInvite).filter(TripInvite.invitee_id == current_user.id)
        
        if status_filter:
            if status_filter not in ["pending", "accepted", "declined"]:
                raise HTTPException(status_code=400, detail="Invalid status filter")
            query = query.filter(TripInvite.status == status_filter)
        
        invites = query.order_by(TripInvite.created_at.desc()).all()
        
        # Group by status
        grouped = {
            "pending": [],
            "accepted": [],
            "declined": []
        }
        
        for invite in invites:
            try:
                # Check if trip and inviter still exist
                trip = db.query(Trip).filter(Trip.id == invite.trip_id).first()
                inviter = db.query(User).filter(User.id == invite.inviter_id).first()
                
                if not trip or not inviter:
                    # Skip invites with missing trip or inviter
                    continue
                
                invite_dict = {
                    "id": invite.id,
                    "trip_id": invite.trip_id,
                    "trip_title": trip.title,
                    "inviter_id": invite.inviter_id,
                    "inviter_email": inviter.email,
                    "inviter_name": inviter.name,
                    "invitee_id": invite.invitee_id,
                    "status": invite.status,
                    "permission_level": invite.permission_level,
                    "created_at": invite.created_at
                }
                grouped[invite.status].append(invite_dict)
            except Exception as e:
                # Log the error but continue processing other invites
                print(f"Error processing invite {invite.id}: {str(e)}")
                continue
        
        return grouped
    except Exception as e:
        print(f"Error in get_invites: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading invites: {str(e)}")


@router.put("/invites/{invite_id}/accept")
async def accept_invite(
    invite_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Accept a trip invite."""
    
    try:
        invite = db.query(TripInvite).filter(TripInvite.id == invite_id).first()
        if not invite:
            raise HTTPException(status_code=404, detail="Invite not found")
        
        if invite.invitee_id != current_user.id:
            raise HTTPException(status_code=403, detail="You cannot accept this invite")
        
        if invite.status != "pending":
            raise HTTPException(status_code=400, detail=f"Invite already {invite.status}")
        
        # Verify trip still exists
        trip = db.query(Trip).filter(Trip.id == invite.trip_id).first()
        if not trip:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        invite.status = "accepted"
        invite.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(invite)
        
        return {
            "id": invite.id,
            "trip_id": invite.trip_id,
            "trip_title": trip.title,
            "status": invite.status,
            "permission_level": invite.permission_level,
            "message": f"Invite accepted! You can now edit {trip.title}"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in accept_invite: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error accepting invite: {str(e)}")


@router.put("/invites/{invite_id}/decline")
async def decline_invite(
    invite_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Decline a trip invite."""
    
    try:
        invite = db.query(TripInvite).filter(TripInvite.id == invite_id).first()
        if not invite:
            raise HTTPException(status_code=404, detail="Invite not found")
        
        if invite.invitee_id != current_user.id:
            raise HTTPException(status_code=403, detail="You cannot decline this invite")
        
        if invite.status != "pending":
            raise HTTPException(status_code=400, detail=f"Invite already {invite.status}")
        
        invite.status = "declined"
        invite.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(invite)
        
        return {
            "id": invite.id,
            "trip_id": invite.trip_id,
            "status": invite.status,
            "message": "Invite declined"
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in decline_invite: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error declining invite: {str(e)}")



@router.get("/shared-trips")
async def get_shared_trips(
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Get all trips shared with the current user (accepted invites)."""
    
    accepted_invites = db.query(TripInvite).filter(
        TripInvite.invitee_id == current_user.id,
        TripInvite.status == "accepted"
    ).all()
    
    result = []
    for invite in accepted_invites:
        trip = invite.trip
        result.append({
            "id": trip.id,
            "title": trip.title,
            "location": trip.location,
            "start_date": str(trip.start_date),
            "end_date": str(trip.end_date),
            "cover_image": trip.cover_image,
            "owner_id": trip.owner_id,
            "owner_name": trip.owner.name,
            "permission_level": invite.permission_level,
            "invite_id": invite.id
        })
    
    return result


@router.get("/trips/{trip_id}/shared-with")
async def get_trip_shares(
    trip_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Get all users a trip is shared with (for owner)."""
    
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only trip owner can view shares")
    
    invites = db.query(TripInvite).filter(
        TripInvite.trip_id == trip_id,
        TripInvite.status == "accepted"
    ).all()
    
    result = []
    for invite in invites:
        result.append({
            "invite_id": invite.id,
            "user_id": invite.invitee_id,
            "user_name": invite.invitee.name,
            "user_email": invite.invitee.email,
            "permission_level": invite.permission_level,
            "shared_at": invite.created_at
        })
    
    return result


@router.delete("/trips/{trip_id}/shared-with/{invite_id}")
async def revoke_share(
    trip_id: int,
    invite_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    """Revoke a trip share (owner only)."""
    
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only trip owner can revoke shares")
    
    invite = db.query(TripInvite).filter(
        TripInvite.id == invite_id,
        TripInvite.trip_id == trip_id
    ).first()
    
    if not invite:
        raise HTTPException(status_code=404, detail="Share not found")
    
    db.delete(invite)
    db.commit()
    
    return {"message": f"Share with {invite.invitee.name} revoked"}
