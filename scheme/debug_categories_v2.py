import pandas as pd

try:
    df = pd.read_csv("schemes.csv", engine="python")
    df.columns = df.columns.str.strip().str.lower()
except Exception as e:
    print(e)
    exit()

def detect_category(text: str) -> str:
    text = str(text).lower()
    print(f"Checking: '{text}'")
    if "kisan" in text or "farmer" in text or "crop" in text:
        return "farmer"
    elif "student" in text or "education" in text or "scholar":
        print(f"  -> Matched Student keywords")
        return "student"
    elif "pension" in text or "senior":
        return "senior"
    elif "health" in text or "insurance":
        return "health"
    else:
        return "general"

# Inspect first row
row1 = df.iloc[0]
print(f"Row 1 Name: {row1['scheme_name']}")
cat = detect_category(row1['scheme_name'])
print(f"Row 1 Category: {cat}")

# Inspect Row with 'PM Awas Yojana Rural'
row_awas = df[df["scheme_name"].str.contains("Awas", na=False)].iloc[0]
print(f"\nAwas Name: {row_awas['scheme_name']}")
cat_awas = detect_category(row_awas['scheme_name'])
print(f"Awas Category: {cat_awas}")
