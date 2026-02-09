"""
State API Router

Endpoints for managing user focus state (FLOW/SHALLOW/IDLE).
"""

from fastapi import APIRouter, Depends

from ..db import UserStateManager
from ..deps import CurrentUser, get_current_user, get_state_manager
from ..schemas import FlowState, StateResponse, StateUpdateRequest


router = APIRouter(prefix="/state", tags=["state"])


@router.get("", response_model=StateResponse)
async def get_state(
    user: CurrentUser = Depends(get_current_user),
    state_manager: UserStateManager = Depends(get_state_manager),
):
    """Get current user focus state."""
    state = state_manager.get_state(user.id)
    return StateResponse(state=FlowState(state), user_id=user.id)


@router.put("", response_model=StateResponse)
async def update_state(
    request: StateUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    state_manager: UserStateManager = Depends(get_state_manager),
):
    """Update user focus state."""
    state_manager.set_state(user.id, request.state.value)
    return StateResponse(state=request.state, user_id=user.id)
