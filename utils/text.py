import re

def clean_text(s: str) -> str:
    if not s:
        return ""
    s = s.lower().strip()
    # remove URLs
    s = re.sub(r"http\S+", "", s)
    # keep only alphabets, numbers and basic punctuation
    s = re.sub(r"[^a-z0-9%$ .,:;!?+-]", " ", s)
    # squeeze multiple spaces to single
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def merge_fields(headline: str, summary: str) -> str:
    headline = headline or ""
    summary = summary or ""
    return f"{headline}. {summary}".strip()


