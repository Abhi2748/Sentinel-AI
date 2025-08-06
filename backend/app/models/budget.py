"""
Budget control models for hierarchical budget management
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class BudgetLevel(str, Enum):
    """Budget hierarchy levels"""
    USER = "user"
    TEAM = "team"
    COMPANY = "company"


class BudgetPeriod(str, Enum):
    """Budget time periods"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class BudgetStatus(str, Enum):
    """Budget authorization status"""
    APPROVED = "approved"
    DENIED = "denied"
    WARNING = "warning"
    EXCEEDED = "exceeded"


class BudgetConfig(BaseModel):
    """Budget configuration for a level"""
    
    level: BudgetLevel = Field(..., description="Budget level")
    entity_id: str = Field(..., description="Entity identifier (user/team/company)")
    period: BudgetPeriod = Field(BudgetPeriod.MONTHLY, description="Budget period")
    
    # Budget limits
    limit_usd: float = Field(..., gt=0, description="Budget limit in USD")
    warning_threshold: float = Field(0.8, ge=0.0, le=1.0, description="Warning threshold as percentage")
    
    # Advanced settings
    rollover: bool = Field(False, description="Allow budget rollover to next period")
    emergency_limit: Optional[float] = Field(None, gt=0, description="Emergency budget limit")
    
    # Metadata
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    description: Optional[str] = Field(None, description="Budget description")


class BudgetUsage(BaseModel):
    """Current budget usage for a level"""
    
    level: BudgetLevel = Field(..., description="Budget level")
    entity_id: str = Field(..., description="Entity identifier")
    period: BudgetPeriod = Field(..., description="Budget period")
    
    # Usage metrics
    used_usd: float = Field(0.0, ge=0, description="Amount used in USD")
    remaining_usd: float = Field(0.0, ge=0, description="Remaining budget in USD")
    usage_percentage: float = Field(0.0, ge=0.0, le=1.0, description="Usage as percentage")
    
    # Period tracking
    period_start: datetime = Field(..., description="Period start timestamp")
    period_end: datetime = Field(..., description="Period end timestamp")
    
    # Status
    status: BudgetStatus = Field(BudgetStatus.APPROVED, description="Current budget status")
    is_warning: bool = Field(False, description="Whether budget is in warning state")
    is_exceeded: bool = Field(False, description="Whether budget is exceeded")
    
    # Metadata
    last_updated: datetime = Field(..., description="Last update timestamp")
    request_count: int = Field(0, ge=0, description="Number of requests in period")


class BudgetAuthorization(BaseModel):
    """Budget authorization result"""
    
    approved: bool = Field(..., description="Whether request is approved")
    status: BudgetStatus = Field(..., description="Authorization status")
    
    # Budget information
    level: BudgetLevel = Field(..., description="Budget level checked")
    entity_id: str = Field(..., description="Entity identifier")
    
    # Usage information
    current_usage: float = Field(..., ge=0, description="Current usage in USD")
    budget_limit: float = Field(..., gt=0, description="Budget limit in USD")
    remaining_budget: float = Field(..., ge=0, description="Remaining budget in USD")
    
    # Request-specific
    estimated_cost: float = Field(0.0, ge=0, description="Estimated cost for this request")
    would_exceed: bool = Field(False, description="Whether this request would exceed budget")
    
    # Messages
    message: Optional[str] = Field(None, description="Authorization message")
    warning_message: Optional[str] = Field(None, description="Warning message if applicable")


class BudgetAlert(BaseModel):
    """Budget alert/notification"""
    
    level: BudgetLevel = Field(..., description="Budget level")
    entity_id: str = Field(..., description="Entity identifier")
    alert_type: str = Field(..., description="Type of alert (warning, exceeded, etc.)")
    
    # Alert details
    message: str = Field(..., description="Alert message")
    threshold: float = Field(..., description="Threshold that triggered alert")
    current_usage: float = Field(..., description="Current usage at time of alert")
    
    # Timestamps
    created_at: datetime = Field(..., description="Alert creation timestamp")
    acknowledged_at: Optional[datetime] = Field(None, description="When alert was acknowledged")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional alert metadata")