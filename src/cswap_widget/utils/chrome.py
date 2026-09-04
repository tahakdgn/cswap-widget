import os
import sys
import json
import shutil
import subprocess
from typing import Optional, Dict, Any, Tuple


def find_chrome_executable() -> Optional[str]:
    """Finds the Google Chrome executable path across common Windows & OS locations."""
    possible_paths = [
        os.path.join(os.environ.get("PROGRAMFILES", r"C:\Program Files"), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"), "Google", "Chrome", "Application", "chrome.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Google", "Chrome", "Application", "chrome.exe"),
    ]

    for p in possible_paths:
        if p and os.path.exists(p):
            return p

    # Fallback to PATH
    return shutil.which("chrome") or shutil.which("google-chrome") or shutil.which("chrome.exe") or "chrome.exe"


def get_chrome_user_data_dir() -> str:
    """Returns the Chrome user data directory path."""
    local_app_data = os.environ.get("LOCALAPPDATA") or os.path.join(
        os.environ.get("USERPROFILE", ""), "AppData", "Local"
    )
    return os.path.join(local_app_data, "Google", "Chrome", "User Data")


def get_chrome_profiles() -> Dict[str, Dict[str, Any]]:
    """
    Scans Chrome profiles from 'Local State' and optionally claude-account-switcher accounts.json.
    Returns a dict mapping lowercase email -> {
        'profile_key': 'Profile 1',
        'name': 'Kodjet',
        'email': 'yazilimkodjet@gmail.com',
        'path': '...'
    }
    """
    profiles_by_email: Dict[str, Dict[str, Any]] = {}
    user_data = get_chrome_user_data_dir()
    local_state_path = os.path.join(user_data, "Local State")

    if os.path.exists(local_state_path):
        try:
            with open(local_state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            info_cache = data.get("profile", {}).get("info_cache", {})
            for key, info in info_cache.items():
                email = (info.get("user_name") or "").strip()
                name = (info.get("name") or key).strip()
                profile_path = os.path.join(user_data, key)
                entry = {
                    "profile_key": key,
                    "name": name,
                    "email": email,
                    "path": profile_path,
                }
                if email:
                    profiles_by_email[email.lower()] = entry
        except Exception as e:
            print(f"Error reading Chrome Local State: {e}")

    # Fallback to claude-account-switcher electron/accounts.json if present
    possible_switcher_json = [
        os.path.join(
            os.environ.get("USERPROFILE", ""),
            "Documents", "kodjetProjeler", "claude-account-switcher", "electron", "accounts.json"
        )
    ]
    for json_path in possible_switcher_json:
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    s_data = json.load(f)
                for acc in s_data.get("accounts", []):
                    s_email = (acc.get("googleEmail") or "").strip().lower()
                    s_key = acc.get("chromeProfile")
                    s_name = acc.get("displayName") or acc.get("chromeProfileName") or s_key
                    if s_email and s_key and s_email not in profiles_by_email:
                        profiles_by_email[s_email] = {
                            "profile_key": s_key,
                            "name": s_name,
                            "email": s_email,
                            "path": acc.get("chromeProfilePath") or os.path.join(user_data, s_key),
                        }
            except Exception as e:
                print(f"Error reading claude-account-switcher accounts.json: {e}")

    return profiles_by_email


def find_chrome_profile_for_account(email: str) -> Optional[Dict[str, Any]]:
    """Finds the Chrome profile matching the specified account email."""
    if not email:
        return None
    profiles = get_chrome_profiles()
    email_clean = email.strip().lower()

    # Exact email match
    if email_clean in profiles:
        return profiles[email_clean]

    # Substring / username match
    user_part = email_clean.split("@")[0]
    for p_email, info in profiles.items():
        if user_part in p_email or user_part in info.get("name", "").lower():
            return info

    return None


def launch_chrome_profile(
    profile_key: Optional[str] = None,
    target_url: str = "https://claude.ai"
) -> Tuple[bool, str]:
    """
    Launches Chrome using a specific profile directory in a fully detached background process.
    """
    chrome_exe = find_chrome_executable()
    if not chrome_exe or (not os.path.exists(chrome_exe) and not shutil.which(chrome_exe)):
        return False, "Google Chrome bulunamadı."

    args = [chrome_exe]
    if profile_key:
        args.append(f"--profile-directory={profile_key}")
    args.append(target_url)

    try:
        creationflags = 0
        if sys.platform == "win32":
            # DETACHED_PROCESS (0x00000008) | CREATE_NEW_PROCESS_GROUP (0x00000200)
            creationflags = 0x00000008 | 0x00000200

        subprocess.Popen(
            args,
            creationflags=creationflags,
            close_fds=True,
            shell=False
        )
        return True, f"Chrome açıldı ({profile_key or 'Varsayılan Profil'})."
    except Exception as e:
        return False, f"Chrome başlatılamadı: {e}"


def open_claude_for_account(
    email: str,
    target_url: str = "https://claude.ai"
) -> Tuple[bool, str]:
    """
    Resolves the Chrome profile for an account email and opens Claude in that profile.
    """
    profile = find_chrome_profile_for_account(email)
    profile_key = profile["profile_key"] if profile else None
    return launch_chrome_profile(profile_key=profile_key, target_url=target_url)
