import subprocess
from typing import List, Optional, Tuple
from .models import AccountStatus
from .parser import parse_cswap_output


def fetch_cswap_accounts() -> Tuple[List[AccountStatus], Optional[str]]:
    """
    Executes `cswap list` and returns parsed accounts and an optional error message.
    """
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
            return [], result.stderr.strip() or "Bilinmeyen hata oluştu."

        output = result.stdout
        return parse_cswap_output(output), None
    except Exception as e:
        return [], str(e)


def switch_to_best_account() -> Tuple[bool, str]:
    """
    Executes `cswap switch --strategy best` to switch to the account with maximum headroom.
    """
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


def switch_to_account_id(acc_id: int) -> Tuple[bool, str]:
    """
    Executes `cswap switch <id>` to switch to a specific account slot ID.
    """
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
