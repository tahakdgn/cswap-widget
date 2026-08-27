import re
import subprocess
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class AccountStatus:
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


def parse_cswap_output(output: str) -> List[AccountStatus]:
    accounts: List[AccountStatus] = []
    
    # Split into account blocks
    # Accounts start with pattern like "  1: email@domain.com"
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
        
        block_text = "\n".join(lines[1:])
        
        # 5h line matching
        # e.g.: "├ 5h:  27%   resets 17:09         in 3h 41m" or "├ 5h:   0%"
        m_5h = re.search(r'5h:\s*(\d+)%(?:.*?resets\s+([a-zA-Z0-9:\s]+?)\s+in\s+([^\n\r]+))?', block_text)
        if m_5h:
            five_hour_pct = int(m_5h.group(1))
            if m_5h.group(2) and m_5h.group(3):
                five_hour_reset_time = m_5h.group(2).strip()
                five_hour_reset_in = m_5h.group(3).strip()

        # 7d line matching
        # e.g.: "└ 7d:  31%   resets Aug 24 19:59  in 3d 6h" or "└ 7d:   0%"
        m_7d = re.search(r'7d:\s*(\d+)%(?:.*?resets\s+([a-zA-Z0-9:\s]+?)\s+in\s+([^\n\r]+))?', block_text)
        if m_7d:
            seven_day_pct = int(m_7d.group(1))
            if m_7d.group(2) and m_7d.group(3):
                seven_day_reset_time = m_7d.group(2).strip()
                seven_day_reset_in = m_7d.group(3).strip()
                
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
            seven_day_reset_in=seven_day_reset_in
        ))
        
    return accounts


def fetch_cswap_accounts() -> tuple[List[AccountStatus], Optional[str]]:
    """Runs `cswap list` and returns parsed accounts and optional raw error."""
    try:
        result = subprocess.run(
            ["cswap", "list"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            shell=True,
            timeout=15
        )
        if result.returncode != 0 and not result.stdout:
            return [], result.stderr or "Bilinmeyen hata"
        
        output = result.stdout
        return parse_cswap_output(output), None
    except Exception as e:
        return [], str(e)


def switch_to_best_account() -> tuple[bool, str]:
    """Runs `cswap switch --strategy best`"""
    try:
        result = subprocess.run(
            ["cswap", "switch", "--strategy", "best"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            shell=True,
            timeout=20
        )
        msg = result.stdout if result.stdout else result.stderr
        return result.returncode == 0, msg.strip() if msg else "İşlem tamamlandı"
    except Exception as e:
        return False, str(e)


def switch_to_account_id(acc_id: int) -> tuple[bool, str]:
    """Runs `cswap switch <id>` if direct switch is supported."""
    try:
        result = subprocess.run(
            ["cswap", "switch", str(acc_id)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            shell=True,
            timeout=20
        )
        msg = result.stdout if result.stdout else result.stderr
        return result.returncode == 0, msg.strip() if msg else f"Hesap #{acc_id}'e geçildi"
    except Exception as e:
        return False, str(e)
