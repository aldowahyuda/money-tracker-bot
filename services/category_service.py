# services/category_service.py
import re
from typing import Dict, List

# ---------------------
# RULES: kategori -> keyword list
# (extend sesuai kebutuhan)
# ---------------------
CATEGORY_RULES: Dict[str, List[str]] = {
    "Salary": ["gaji", "salary", "payroll", "gajian"],
    "Bonus": ["bonus", "thr", "insentif"],
    "Food & Groceries": ["makan", "belanja", "grocery", "grocery", "grosir", "sembako"],
    "Dining": ["resto", "restaurant", "rumah makan", "kedai", "warung", "makan di luar"],
    "Coffee & Drinks": ["kopi", "coffee", "teh", "milkshake", "minum", "minuman"],
    "Snacks": ["cemilan", "cimol", "gorengan", "kudapan", "snack"],
    "Transport": ["transport", "transportasi", "gojek", "grab", "ojek", "taksi", "uber", "bus", "kereta"],
    "Fuel": ["bensin", "pertamax", "pertalite", "solar", "fuel", "bbm"],
    "Parking": ["parkir"],
    "Bills & Utilities": ["listrik", "air", "internet", "wifi", "telkom", "telepon", "tagihan"],
    "Rent / Mortgage": ["sewa", "kontrakan", "mortgage", "kpr", "rumah sewa"],
    "Household Supplies": ["peralatan rumah", "perabot", "alat rumah", "sapu", "pembersih"],
    "Healthcare": ["dokter", "obat", "apotik", "klinik", "rumah sakit", "kesehatan"],
    "Insurance": ["asuransi", "premi"],
    "Education": ["sekolah", "tuition", "kursus", "les", "pendidikan"],
    "Personal Care": ["salon", "potong rambut", "perawatan", "skincare", "kosmetik"],
    "Shopping": ["baju", "sepatu", "belanja online", "shopee", "tokopedia", "lazada"],
    "Entertainment": ["nonton", "bioskop", "game", "hiburan", "konser"],
    "Subscriptions": ["netflix", "spotify", "langganan", "subscription", "spotify", "youtube premium"],
    "Travel": ["liburan", "travel", "hotel", "pesawat", "tiket"],
    "Gifts & Donations": ["hadiah", "kado", "donasi", "sedekah", "zakat"],
    "Savings": ["tabungan", "simpan", "save"],
    "Investment": ["investasi", "saham", "reksadana", "crypto", "bitcoin"],
    "Debt Payments": ["hutang", "cicilan", "angsuran", "pinjaman"],
    "Utilities - Mobile": ["pulsa", "paket data", "kuota"],
    "Medical": ["bpjs", "puskesmas", "vaksin"],
    "Pet": ["hewan", "kucing", "anjing", "vet", "veteriner"],
    "Work": ["kantor", "meeting", "work", "dinas"],
    "Office Supplies": ["kertas", "printer", "alat tulis"],
    "Beauty & Fashion": ["makeup", "fashion", "tas", "perhiasan"],
    "Home Improvement": ["tukang", "renovasi", "perbaikan", "plumbing", "listrik rumah"],
    "Other": []  # fallback
}

# ---------------------
# PRECOMPILE regex patterns (word-boundary)
# ---------------------
_CATEGORY_PATTERNS = []
for cat, kws in CATEGORY_RULES.items():
    if not kws:
        continue
    # build single regex per category: \b(k1|k2|k3)\b
    escaped = [re.escape(k) for k in kws]
    pattern = re.compile(r"\b(" + "|".join(escaped) + r")\b", flags=re.IGNORECASE)
    _CATEGORY_PATTERNS.append((cat, pattern))


# ---------------------
# detect_category(title) -> returns category name (string)
# ---------------------
def detect_category(title: str) -> str:
    if not title:
        return "Other"

    title = title.lower()
    # 1) exact keyword match via regex (first-match)
    for cat, pattern in _CATEGORY_PATTERNS:
        if pattern.search(title):
            return cat

    # 2) fallback: check substrings (looser) to catch things like "mcdonalds" -> Dining
    substr_map = {
        "mcd": "Dining",
        "mcdonald": "Dining",
        "starbuck": "Coffee & Drinks",
        "alfamart": "Shopping",
        "indomaret": "Shopping",
        "tokopedia": "Shopping",
        "shopee": "Shopping",
        "grab": "Transport",
        "gojek": "Transport"
    }
    for k, v in substr_map.items():
        if k in title:
            return v

    # 3) final fallback
    return "Other"


# ---------------------
# convenience: add or extend a category at runtime (optional)
# ---------------------
def add_keyword_to_category(category: str, keyword: str):
    """Add a keyword (string) to CATEGORY_RULES and recompile patterns (simple)."""
    category = category.strip()
    keyword = keyword.strip().lower()
    if category not in CATEGORY_RULES:
        CATEGORY_RULES[category] = [keyword]
    else:
        CATEGORY_RULES[category].append(keyword)
    # note: for simplicity we do not recompile patterns here; you can restart or call a helper to rebuild
