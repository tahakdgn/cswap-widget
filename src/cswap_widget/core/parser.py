import re
import json
from typing import List
from .models import AccountStatus, ScopedQuota


def parse_cswap_json(json_str: str) -> List[AccountStatus]:
    """
    Parses machine-readable JSON output from `cswap list --json` into structured AccountStatus objects.
    """
    try:
        data = json.loads(json_str)
        accounts_data = data.get("accounts", [])
        active_num = data.get("activeAccountNumber")
        accounts: List[AccountStatus] = []

        for acc in accounts_data:
            acc_id = acc.get("number", 0)
            email = acc.get("email", "")
            org = acc.get("organizationName", "")
            is_active = acc.get("active", False) or (acc_id == active_num)

            usage = acc.get("usage") or acc.get("lastGoodUsage") or {}

            five_h = usage.get("fiveHour") or {}
            five_hour_pct = int(round(five_h.get("pct", 0)))
            five_hour_reset_time = five_h.get("clock")
            five_hour_reset_in = five_h.get("countdown")

            seven_d = usage.get("sevenDay") or {}
            seven_day_pct = int(round(seven_d.get("pct", 0)))
            seven_day_reset_time = seven_d.get("clock")
            seven_day_reset_in = seven_d.get("countdown")

            scoped_raw = usage.get("scoped") or []
            scoped_quotas = [
                ScopedQuota(name=s.get("name", "Model"), pct=int(round(s.get("pct", 0))))
                for s in scoped_raw if isinstance(s, dict)
            ]

            is_max_plan = (
                any(s.name.lower() == "fable" for s in scoped_quotas)
                or len(scoped_quotas) > 0
                or "max" in org.lower()
            )

            accounts.append(AccountStatus(
                id=acc_id,
                email=email,
                organization=org,
                is_active=is_active,
                five_hour_pct=five_hour_pct,
                five_hour_reset_time=five_hour_reset_time,
                five_hour_reset_in=five_hour_reset_in,
                seven_day_pct=seven_day_pct,
                seven_day_reset_time=seven_day_reset_time,
                seven_day_reset_in=seven_day_reset_in,
                scoped_quotas=scoped_quotas,
                is_max_plan=is_max_plan
            ))

        return accounts
    except Exception:
        return []


def parse_cswap_output(output: str) -> List[AccountStatus]:
    """
    Parses raw textual output from `cswap list` into structured AccountStatus objects.
    """
    accounts: List[AccountStatus] = []

    # Split into account blocks (starts with pattern like "  1: email@domain.com")
    account_blocks = re.split(r'\n\s*(?=\d+:)', output)

    for block in account_blocks:
        lines = [line.rstrip() for line in block.strip().split('\n') if line.strip()]
        if not lines:
            continue

        first_line = lines[0]
        # Match "1: email@domain.com [Organization Name] (active)"
        header_match = re.search(r'^\s*(\d+):\s*([^\s\[]+)(?:\s*\[(.*?)\])?(?:\s*\(active\))?', first_line)
        if not header_match:
            continue

        acc_id = int(header_match.group(1))
        email = header_match.group(2)
        org = header_match.group(3) or ""
        is_active = "(active)" in first_line.lower()

        five_hour_pct = 0
        five_hour_reset_time = None
        five_hour_reset_in = None

        seven_day_pct = 0
        seven_day_reset_time = None
        seven_day_reset_in = None
        scoped_quotas: List[ScopedQuota] = []

        block_text = "\n".join(lines[1:])

        # 5h line matching: e.g. "├ 5h:  27%   resets 17:09   in 3h 41m"
        m_5h = re.search(r'5h:\s*(\d+)%(?:.*?resets\s+([a-zA-Z0-9:\s]+?)\s+in\s+([^\n\r]+))?', block_text)
        if m_5h:
            five_hour_pct = int(m_5h.group(1))
            if m_5h.group(2) and m_5h.group(3):
                five_hour_reset_time = m_5h.group(2).strip()
                five_hour_reset_in = m_5h.group(3).strip()

        # 7d line matching: e.g. "└ 7d:  31%   resets Aug 24 19:59   in 3d 6h"
        m_7d = re.search(r'7d:\s*(\d+)%(?:.*?resets\s+([a-zA-Z0-9:\s]+?)\s+in\s+([^\n\r]+))?', block_text)
        if m_7d:
            seven_day_pct = int(m_7d.group(1))
            if m_7d.group(2) and m_7d.group(3):
                seven_day_reset_time = m_7d.group(2).strip()
                seven_day_reset_in = m_7d.group(3).strip()

        # Scoped model matching (e.g. "└ Fable:   0%" or "├ Fable: 10%")
        scoped_matches = re.finditer(r'(?:├|└|\s)\s*([A-Za-z0-9_-]+):\s*(\d+)%', block_text)
        for sm in scoped_matches:
            model_name = sm.group(1).strip()
            if model_name.lower() not in ["5h", "7d"]:
                scoped_pct = int(sm.group(2))
                scoped_quotas.append(ScopedQuota(name=model_name, pct=scoped_pct))

        is_max_plan = (
            any(s.name.lower() == "fable" for s in scoped_quotas)
            or len(scoped_quotas) > 0
            or "max" in org.lower()
        )

        accounts.append(AccountStatus(
            id=acc_id,
            email=email,
            organization=org,
            is_active=is_active,
            five_hour_pct=five_hour_pct,
            five_hour_reset_time=five_hour_reset_time,
            five_hour_reset_in=five_hour_reset_in,
            seven_day_pct=seven_day_pct,
            seven_day_reset_time=seven_day_reset_time,
            seven_day_reset_in=seven_day_reset_in,
            scoped_quotas=scoped_quotas,
            is_max_plan=is_max_plan
        ))

    return accounts

