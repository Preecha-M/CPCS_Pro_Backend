import re

def parse_prediction(pred_text: str):
    if not pred_text:
        return None, None

    # OLD LOGIC
    disease_old = None
    first_line = pred_text.split("\n", 1)[0]
    m_old = re.search(r"ผลการทำนาย:\s*(.+)$", first_line)
    if m_old:
        disease_old = m_old.group(1).strip()
    
    # NEW LOGIC (Proposed)
    disease_new = None
    m_new = re.search(r"ผลการทำนาย:\s*([^\n]+)", pred_text)
    if m_new:
        disease_new = m_new.group(1).strip()

    conf = None
    m2 = re.search(r"ความมั่นใจ:\s*([0-9]*\.?[0-9]+)", pred_text)
    if m2:
        try:
            conf = float(m2.group(1))
        except Exception:
            conf = None

    return disease_old, disease_new, conf

# Case 1: Standard
text_1 = """🔍 ผลการทำนาย: Disease A
✅ ความมั่นใจ: 90%"""

# Case 2: Leading Newline (Suspected culprit)
text_2 = """
🔍 ผลการทำนาย: Disease B
✅ ความมั่นใจ: 80%"""

print("--- Case 1 ---")
old1, new1, conf1 = parse_prediction(text_1)
print(f"Old: {old1}, New: {new1}, Conf: {conf1}")

print("\n--- Case 2 ---")
old2, new2, conf2 = parse_prediction(text_2)
print(f"Old: {old2}, New: {new2}, Conf: {conf2}")
