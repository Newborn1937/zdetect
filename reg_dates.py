import re
import subprocess
import datetime as dt

# Russian month names (genitive) -> month number
_RU_MONTH = {
    'января':1, 'февраля':2, 'марта':3, 'апреля':4, 'мая':5, 'июня':6,
    'июля':7, 'августа':8, 'сентября':9, 'октября':10, 'ноября':11, 'декабря':12
}

# Parse "Дата регистрации: 2 июля 2007" (optionally with "года")
_DATE_RE = re.compile(r'Дата регистрации:\s*([0-9]{1,2})\s+([А-Яа-я]+)\s+([0-9]{4})(?:\s*года)?')

# Current A record for regvk.com; update if it changes
_REGVK_IP = "81.177.139.247"

def _parse_reg_date_from_html(html: str):
    m = _DATE_RE.search(html)
    if not m:
        return None
    d = int(m.group(1))
    mon = m.group(2).lower()
    y = int(m.group(3))
    mm = _RU_MONTH.get(mon)
    if not mm:
        return None
    try:
        return dt.date(y, mm, d)
    except ValueError:
        return None

def _get_user_reg_date(user_id: int):
    """Get exact registration date from regvk.com. Returns datetime.date or None."""
    cmd = [
        "curl", "-s", "--compressed",
        "--resolve", f"regvk.com:443:{_REGVK_IP}",
        "https://regvk.com/",
        "--data-urlencode", f"link={user_id}",
        "--data-urlencode", "button=Определить дату регистрации",
    ]
    try:
        html = subprocess.check_output(cmd).decode("utf-8", "ignore")
    except Exception:
        return None
    return _parse_reg_date_from_html(html)

def get_user_reg_date(user_id: int):
    """Get user registration date; if unavailable, probe nearest IDs (±1..±4)."""
    # Try exact first
    d0 = _get_user_reg_date(user_id)
    if d0 is not None:
        return d0
    # Fallback: nearest numeric neighbors (like your old logic)
    for n in range(1, 5):
        for m in (1, -1):
            d = _get_user_reg_date(user_id + n * m)
            if d is not None:
                return d
    return None