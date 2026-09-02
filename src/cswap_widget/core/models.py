from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class ScopedQuota:
    """Represents an additional scoped model quota (such as Fable)."""
    name: str
    pct: int


@dataclass
class AccountStatus:
    """Represents the quota and status information for a Claude account."""
    id: int
    email: str
    organization: str
    is_active: bool
    five_hour_pct: int
    five_hour_reset_time: Optional[str]
    five_hour_reset_in: Optional[str]
    seven_day_pct: int
    seven_day_reset_time: Optional[str]
    seven_day_reset_in: Optional[str]
    scoped_quotas: List[ScopedQuota] = field(default_factory=list)
    is_max_plan: bool = False
    needs_relogin: bool = False

