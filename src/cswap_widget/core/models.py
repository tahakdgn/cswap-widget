from dataclasses import dataclass
from typing import Optional


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
