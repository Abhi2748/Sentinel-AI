"""
BudgetController for hierarchical budget management
Manages budgets at user, team, and company levels with automatic authorization
"""

import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum

from ..models.budget import (
    BudgetConfig,
    BudgetUsage,
    BudgetAuthorization,
    BudgetLevel,
    BudgetPeriod,
    BudgetStatus
)
from ..models.requests import AIRequest


class BudgetPeriodCalculator:
    """Calculates budget periods and tracking windows."""
    
    @staticmethod
    def get_period_dates(period: BudgetPeriod, reference_date: datetime = None) -> tuple[datetime, datetime]:
        """Get start and end dates for a budget period."""
        if reference_date is None:
            reference_date = datetime.now()
        
        if period == BudgetPeriod.DAILY:
            start = reference_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif period == BudgetPeriod.WEEKLY:
            # Start from Monday
            days_since_monday = reference_date.weekday()
            start = reference_date.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
            end = start + timedelta(weeks=1)
        elif period == BudgetPeriod.MONTHLY:
            start = reference_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if reference_date.month == 12:
                end = start.replace(year=start.year + 1, month=1)
            else:
                end = start.replace(month=start.month + 1)
        elif period == BudgetPeriod.YEARLY:
            start = reference_date.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end = start.replace(year=start.year + 1)
        else:
            raise ValueError(f"Unknown budget period: {period}")
        
        return start, end


class BudgetController:
    """
    Manages hierarchical budget control with automatic authorization.
    Supports user → team → company hierarchy with configurable limits.
    """
    
    def __init__(self):
        """Initialize budget controller."""
        self.budget_configs: Dict[str, BudgetConfig] = {}
        self.budget_usage: Dict[str, BudgetUsage] = {}
        self.period_calculator = BudgetPeriodCalculator()
        
        # Initialize default budgets
        self._initialize_default_budgets()
    
    def _initialize_default_budgets(self):
        """Initialize default budget configurations."""
        # Default company budget
        company_config = BudgetConfig(
            level=BudgetLevel.COMPANY,
            entity_id="default_company",
            period=BudgetPeriod.MONTHLY,
            limit_usd=10000.0,
            warning_threshold=0.8,
            description="Default company budget"
        )
        self.budget_configs["default_company"] = company_config
        
        # Default team budget
        team_config = BudgetConfig(
            level=BudgetLevel.TEAM,
            entity_id="default_team",
            period=BudgetPeriod.MONTHLY,
            limit_usd=1000.0,
            warning_threshold=0.8,
            description="Default team budget"
        )
        self.budget_configs["default_team"] = team_config
        
        # Default user budget
        user_config = BudgetConfig(
            level=BudgetLevel.USER,
            entity_id="default_user",
            period=BudgetPeriod.MONTHLY,
            limit_usd=100.0,
            warning_threshold=0.8,
            description="Default user budget"
        )
        self.budget_configs["default_user"] = user_config
    
    def add_budget_config(self, config: BudgetConfig) -> None:
        """Add a new budget configuration."""
        key = f"{config.level.value}_{config.entity_id}"
        self.budget_configs[key] = config
    
    def get_budget_config(self, level: BudgetLevel, entity_id: str) -> Optional[BudgetConfig]:
        """Get budget configuration for a level and entity."""
        key = f"{level.value}_{entity_id}"
        return self.budget_configs.get(key)
    
    def _get_entity_hierarchy(self, request: AIRequest) -> List[tuple[BudgetLevel, str]]:
        """Get the budget hierarchy for a request."""
        hierarchy = []
        
        # User level (always present)
        hierarchy.append((BudgetLevel.USER, request.user_id))
        
        # Team level (if present)
        if request.team_id:
            hierarchy.append((BudgetLevel.TEAM, request.team_id))
        
        # Company level (if present)
        if request.company_id:
            hierarchy.append((BudgetLevel.COMPANY, request.company_id))
        
        return hierarchy
    
    async def check_authorization(self, request: AIRequest, estimated_cost: float = 0.0) -> BudgetAuthorization:
        """
        Check if a request is authorized based on budget constraints.
        
        Args:
            request: The AI request to check
            estimated_cost: Estimated cost for this request
            
        Returns:
            BudgetAuthorization with approval status and details
        """
        hierarchy = self._get_entity_hierarchy(request)
        
        # Check each level in the hierarchy
        for level, entity_id in hierarchy:
            config = self.get_budget_config(level, entity_id)
            if not config:
                # Use default config for this level
                config = self._get_default_config_for_level(level)
            
            # Get current usage
            usage = await self._get_budget_usage(config, entity_id)
            
            # Check if this request would exceed budget
            would_exceed = usage.used_usd + estimated_cost > config.limit_usd
            remaining_after_request = config.limit_usd - (usage.used_usd + estimated_cost)
            
            # Determine authorization status
            if would_exceed:
                return BudgetAuthorization(
                    approved=False,
                    status=BudgetStatus.EXCEEDED,
                    level=level,
                    entity_id=entity_id,
                    current_usage=usage.used_usd,
                    budget_limit=config.limit_usd,
                    remaining_budget=usage.remaining_usd,
                    estimated_cost=estimated_cost,
                    would_exceed=True,
                    message=f"Request would exceed {level.value} budget limit"
                )
            
            # Check warning threshold
            usage_percentage = (usage.used_usd + estimated_cost) / config.limit_usd
            if usage_percentage >= config.warning_threshold:
                return BudgetAuthorization(
                    approved=True,
                    status=BudgetStatus.WARNING,
                    level=level,
                    entity_id=entity_id,
                    current_usage=usage.used_usd,
                    budget_limit=config.limit_usd,
                    remaining_budget=remaining_after_request,
                    estimated_cost=estimated_cost,
                    would_exceed=False,
                    message=f"Request approved but {level.value} budget is at {usage_percentage:.1%}",
                    warning_message=f"Approaching {level.value} budget limit"
                )
        
        # All levels approved
        return BudgetAuthorization(
            approved=True,
            status=BudgetStatus.APPROVED,
            level=hierarchy[-1][0] if hierarchy else BudgetLevel.USER,
            entity_id=hierarchy[-1][1] if hierarchy else request.user_id,
            current_usage=0.0,  # Will be updated after request
            budget_limit=0.0,    # Will be updated after request
            remaining_budget=0.0, # Will be updated after request
            estimated_cost=estimated_cost,
            would_exceed=False,
            message="Request approved"
        )
    
    def _get_default_config_for_level(self, level: BudgetLevel) -> BudgetConfig:
        """Get default budget configuration for a level."""
        if level == BudgetLevel.COMPANY:
            return self.budget_configs["default_company"]
        elif level == BudgetLevel.TEAM:
            return self.budget_configs["default_team"]
        else:  # USER
            return self.budget_configs["default_user"]
    
    async def _get_budget_usage(self, config: BudgetConfig, entity_id: str) -> BudgetUsage:
        """Get current budget usage for a configuration."""
        key = f"{config.level.value}_{entity_id}"
        
        if key in self.budget_usage:
            usage = self.budget_usage[key]
            
            # Check if we need to reset for new period
            current_period_start, current_period_end = self.period_calculator.get_period_dates(
                config.period, datetime.now()
            )
            
            if usage.period_start != current_period_start:
                # Reset for new period
                usage = await self._reset_budget_usage(config, entity_id, current_period_start, current_period_end)
                self.budget_usage[key] = usage
            
            return usage
        else:
            # Initialize new usage
            period_start, period_end = self.period_calculator.get_period_dates(config.period)
            usage = await self._reset_budget_usage(config, entity_id, period_start, period_end)
            self.budget_usage[key] = usage
            return usage
    
    async def _reset_budget_usage(self, config: BudgetConfig, entity_id: str, 
                                 period_start: datetime, period_end: datetime) -> BudgetUsage:
        """Reset budget usage for a new period."""
        return BudgetUsage(
            level=config.level,
            entity_id=entity_id,
            period=config.period,
            used_usd=0.0,
            remaining_usd=config.limit_usd,
            usage_percentage=0.0,
            period_start=period_start,
            period_end=period_end,
            status=BudgetStatus.APPROVED,
            is_warning=False,
            is_exceeded=False,
            last_updated=datetime.now(),
            request_count=0
        )
    
    async def record_usage(self, request: AIRequest, actual_cost: float) -> None:
        """
        Record actual usage after a request is completed.
        
        Args:
            request: The completed AI request
            actual_cost: The actual cost incurred
        """
        hierarchy = self._get_entity_hierarchy(request)
        
        for level, entity_id in hierarchy:
            config = self.get_budget_config(level, entity_id)
            if not config:
                config = self._get_default_config_for_level(level)
            
            key = f"{level.value}_{entity_id}"
            usage = await self._get_budget_usage(config, entity_id)
            
            # Update usage
            usage.used_usd += actual_cost
            usage.remaining_usd = max(0, config.limit_usd - usage.used_usd)
            usage.usage_percentage = usage.used_usd / config.limit_usd
            usage.request_count += 1
            usage.last_updated = datetime.now()
            
            # Update status
            if usage.usage_percentage >= 1.0:
                usage.status = BudgetStatus.EXCEEDED
                usage.is_exceeded = True
            elif usage.usage_percentage >= config.warning_threshold:
                usage.status = BudgetStatus.WARNING
                usage.is_warning = True
            else:
                usage.status = BudgetStatus.APPROVED
                usage.is_warning = False
                usage.is_exceeded = False
            
            self.budget_usage[key] = usage
    
    async def get_budget_summary(self, level: BudgetLevel, entity_id: str) -> Dict[str, Any]:
        """Get budget summary for a specific level and entity."""
        config = self.get_budget_config(level, entity_id)
        if not config:
            config = self._get_default_config_for_level(level)
        
        usage = await self._get_budget_usage(config, entity_id)
        
        return {
            "level": level.value,
            "entity_id": entity_id,
            "period": config.period.value,
            "limit_usd": config.limit_usd,
            "used_usd": usage.used_usd,
            "remaining_usd": usage.remaining_usd,
            "usage_percentage": usage.usage_percentage,
            "status": usage.status.value,
            "is_warning": usage.is_warning,
            "is_exceeded": usage.is_exceeded,
            "request_count": usage.request_count,
            "period_start": usage.period_start.isoformat(),
            "period_end": usage.period_end.isoformat(),
            "last_updated": usage.last_updated.isoformat()
        }
    
    async def get_hierarchy_summary(self, request: AIRequest) -> List[Dict[str, Any]]:
        """Get budget summary for all levels in the hierarchy."""
        hierarchy = self._get_entity_hierarchy(request)
        summaries = []
        
        for level, entity_id in hierarchy:
            summary = await self.get_budget_summary(level, entity_id)
            summaries.append(summary)
        
        return summaries
    
    def estimate_request_cost(self, request: AIRequest, complexity_score: float) -> float:
        """
        Estimate the cost of a request based on complexity and requirements.
        
        Args:
            request: The AI request
            complexity_score: Complexity score from analyzer
            
        Returns:
            Estimated cost in USD
        """
        # Base cost estimation
        base_cost = 0.002  # $0.002 per 1k tokens
        
        # Adjust based on complexity
        complexity_multiplier = 1.0 + (complexity_score * 2.0)  # 1x to 3x
        
        # Adjust based on model requirements
        model_multiplier = 1.0
        if request.provider:
            if request.provider.value == "anthropic":
                model_multiplier = 1.5  # Anthropic is more expensive
            elif request.provider.value == "groq":
                model_multiplier = 0.7  # Groq is cheaper
        
        # Adjust based on temperature (higher temperature = more tokens)
        temperature_multiplier = 1.0 + (request.temperature * 0.5)  # 1x to 1.5x
        
        # Estimate token count based on prompt length
        estimated_tokens = len(request.prompt) // 4  # Rough estimate
        
        # Calculate final cost
        estimated_cost = (
            base_cost * 
            (estimated_tokens / 1000) * 
            complexity_multiplier * 
            model_multiplier * 
            temperature_multiplier
        )
        
        return max(estimated_cost, 0.001)  # Minimum cost of $0.001
    
    async def get_budget_alerts(self, level: BudgetLevel, entity_id: str) -> List[Dict[str, Any]]:
        """Get budget alerts for a specific level and entity."""
        config = self.get_budget_config(level, entity_id)
        if not config:
            return []
        
        usage = await self._get_budget_usage(config, entity_id)
        alerts = []
        
        # Warning alert
        if usage.is_warning and not usage.is_exceeded:
            alerts.append({
                "type": "warning",
                "message": f"{level.value.title()} budget is at {usage.usage_percentage:.1%}",
                "threshold": config.warning_threshold,
                "current_usage": usage.used_usd,
                "created_at": datetime.now().isoformat()
            })
        
        # Exceeded alert
        if usage.is_exceeded:
            alerts.append({
                "type": "exceeded",
                "message": f"{level.value.title()} budget has been exceeded",
                "threshold": 1.0,
                "current_usage": usage.used_usd,
                "created_at": datetime.now().isoformat()
            })
        
        return alerts