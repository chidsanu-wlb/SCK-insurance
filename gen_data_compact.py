import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker instances
faker_en = Faker('en_US')
faker_th = Faker('th_TH')

# Thai month names for Buddhist Era formatting
thai_months = {
    1: "มกราคม", 2: "กุมภาพันธ์", 3: "มีนาคม", 4: "เมษายน",
    5: "พฤษภาคม", 6: "มิถุนายน", 7: "กรกฎาคม", 8: "สิงหาคม",
    9: "กันยายน", 10: "ตุลาคม", 11: "พฤศจิกายน", 12: "ธันวาคม"
}

# Renewal date fixed
renewal_date = datetime(2026, 8, 15)

# Helper: Convert to Thai Buddhist Era date string
def thai_date(date_obj):
    year_be = date_obj.year + 543
    return f"{date_obj.day} {thai_months[date_obj.month]} {year_be}"

# Helper: Age string
def age_string(dob, ref_date=renewal_date):
    delta = ref_date - dob
    years = delta.days // 365
    days = delta.days % 365
    return f"{years} ปี {days} วัน"

# Helper: Thai ID generator with checksum
def generate_thai_id():
    digits = [random.randint(0, 9) for _ in range(12)]
    checksum = (11 - sum([(13 - i) * digits[i] for i in range(12)]) % 11) % 10
    digits.append(checksum)
    return ''.join(map(str, digits))

# Helper: Phone number
def generate_phone():
    return "08" + ''.join([str(random.randint(0, 9)) for _ in range(8)])

# Helper: DOB generator
def generate_dob(role, overage=False):
    if role in ["holder", "spouse"]:
        if overage:
            # Overage adult: between 16 Aug 1960 and 15 Aug 1961
            return datetime(1960, 8, 16) + timedelta(days=random.randint(0, 365))
        else:
            # Normal adult: 20–30 years old relative to renewal date
            return renewal_date - timedelta(days=random.randint(7300, 10950))
    elif role == "child":
        if overage:
            # Overage child: between 16 Aug 2010 and 15 Aug 2011
            return datetime(2010, 8, 16) + timedelta(days=random.randint(0, 365))
        else:
            # Normal child: DOB between 2013 and 2025
            year = random.randint(2013, 2025)
            month = random.randint(1, 12)
            day = random.randint(1, 28)  # safe day range
            return datetime(year, month, day)
    else:
        # Fallback: return a valid adult DOB if role is unexpected
        return renewal_date - timedelta(days=random.randint(7300, 10950))

# Generate holder info
def generate_holder():
    first_name_th = faker_th.first_name()
    last_name_th = faker_th.last_name()
    first_name_en = faker_en.first_name()
    dob = generate_dob("holder")
    return f"""ชื่อ: {first_name_th} {last_name_th}
เลขบัตรประชาชน: {generate_thai_id()}
เบอร์โทรศัพท์: {generate_phone()}
อีเมล: {first_name_en.lower()}@email.com
ว/ด/ป เกิด: {thai_date(dob)}
อายุ: {age_string(dob)}"""

# Generate member info
def generate_member(role_label, overage=False, deceased=False):
    # Map Thai role labels to internal role keys
    if "คู่สมรส" in role_label:
        role_key = "spouse"
    elif "บุตร" in role_label:
        role_key = "child"
    else:
        role_key = "holder"

    first_name_th = faker_th.first_name()
    last_name_th = faker_th.last_name()
    dob = generate_dob(role_key, overage)
    status = "เสียชีวิต" if deceased else "มีชีวิต"

    return f"""{role_label}: {status}
ชื่อ: {first_name_th} {last_name_th}
ว/ด/ป เกิด: {thai_date(dob)}
อายุ: {age_string(dob)}"""

# Timeline mapping
def days_advance(timeline):
    if "90 - 30" in timeline:
        return random.randint(30, 90)
    elif "29 - 1" in timeline:
        return random.randint(1, 29)
    elif "ภายในวันที่หมดอายุ" in timeline:
        return 0
    return 0

# Read input CSV
df = pd.read_csv("SCK insurance - Sheet1.csv")

output_rows = []
for _, row in df.iterrows():
    timeline = row['Timeline']
    bundle = row['Bundle']
    family = str(row['Family']) if not pd.isna(row['Family']) else ""

    advance_days = days_advance(timeline)
    expiry_date = renewal_date + timedelta(days=advance_days)
    start_date = expiry_date - timedelta(days=365)

    holder_info = generate_holder()
    member_info = ""

    if "Family" in bundle:
        if "คู่สมรส" in family:
            member_info += generate_member("คู่สมรส", overage="อายุเกิน" in family, deceased="เสียชีวิต" in family) + "\n\n"
        if "ลูก 1" in family:
            member_info += generate_member("บุตรคนที่ 1", overage="อายุเกิน" in family, deceased="เสียชีวิต" in family) + "\n\n"
        if "ลูก 2" in family:
            member_info += generate_member("บุตรคนที่ 2", overage="อายุเกิน" in family, deceased="เสียชีวิต" in family) + "\n\n"

    status_info = f"""จำนวนวันที่ต่ออายุล่วงหน้า: {advance_days} วัน
วันที่ต่ออายุ: {thai_date(renewal_date)}
วันสิ้นสุดความคุ้มครอง: {thai_date(expiry_date)}
วันเริ่มสัญญาฉบับปัจจุบัน: {thai_date(start_date)}"""

    output_rows.append({
        "Timeline": timeline,
        "Bundle": bundle,
        "Family": family,
        "ข้อมูลผู้ถือกรมธรรม์": holder_info,
        "ข้อมูลสมาชิกในกรมธรรม์": member_info.strip(),
        "Status": status_info
    })

# Save output CSV
output_df = pd.DataFrame(output_rows)
output_df.to_csv("insurance_mock_output.csv", index=False, encoding="utf-8-sig")
