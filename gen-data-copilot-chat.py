import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

faker_th = Faker('th_TH')
faker_en = Faker('en_US')

# -------------------------------
# Helper Functions
# -------------------------------

def generate_thai_id():
    digits = [random.randint(0, 9) for _ in range(12)]
    checksum = sum([(13 - i) * digits[i] for i in range(12)]) % 11
    check_digit = (11 - checksum) % 10
    digits.append(check_digit)
    return ''.join(map(str, digits))

def buddhist_date(date_obj):
    months_th = ["มกราคม","กุมภาพันธ์","มีนาคม","เมษายน","พฤษภาคม","มิถุนายน",
                 "กรกฎาคม","สิงหาคม","กันยายน","ตุลาคม","พฤศจิกายน","ธันวาคม"]
    return f"{date_obj.day} {months_th[date_obj.month-1]} {date_obj.year + 543}"

def calculate_age(birthdate, renewal_date):
    delta = renewal_date - birthdate
    years = delta.days // 365
    days = delta.days % 365
    return f"{years} ปี {days} วัน"

def random_phone():
    return "08" + "".join([str(random.randint(0,9)) for _ in range(8)])

# -------------------------------
# Date Setup
# -------------------------------

renewal_date = datetime(2026, 8, 15)

def get_days_before(timeline):
    if "90 - 30" in timeline:
        return random.randint(30, 90)
    elif "29 - 1" in timeline:
        return random.randint(1, 29)
    else:
        return 0

# -------------------------------
# Person Generators
# -------------------------------

def generate_holder(days_before):
    first_name_th = faker_th.first_name()
    last_name_th = faker_th.last_name()
    first_name_en = faker_en.first_name()
    birthdate = renewal_date - timedelta(days=random.randint(7300, 10950))  # 20-30 ปี
    return f"""ชื่อ: {first_name_th} {last_name_th}
เลขบัตรประชาชน: {generate_thai_id()}
เบอร์โทรศัพท์: {random_phone()}
อีเมล: {first_name_en.lower()}@email.com
ว/ด/ป เกิด: {buddhist_date(birthdate)}
อายุ: {calculate_age(birthdate, renewal_date)}"""

def generate_spouse(days_before, overage=False, deceased=False):
    first_name_th = faker_th.first_name()
    last_name_th = faker_th.last_name()
    if overage:
        birthdate = datetime(1961, 8, 15)  # >65 ปี
    else:
        birthdate = renewal_date - timedelta(days=random.randint(7300, 10950))
    status = "เสียชีวิต" if deceased else "มีชีวิต"
    return f"""คู่สมรส: {status}
ชื่อ: {first_name_th} {last_name_th}
ว/ด/ป เกิด: {buddhist_date(birthdate)}
อายุ: {calculate_age(birthdate, renewal_date)}"""

def generate_child(days_before, overage=False, deceased=False, index=1):
    first_name_th = faker_th.first_name()
    last_name_th = faker_th.last_name()
    if overage:
        birthdate = datetime(2009, 8, 15)  # >15 ปี
    else:
        birthdate = datetime(random.randint(2013, 2025), random.randint(1,12), random.randint(1,28))
    status = "เสียชีวิต" if deceased else "มีชีวิต"
    return f"""บุตรคนที่ {index}: {status}
ชื่อ: {first_name_th} {last_name_th}
ว/ด/ป เกิด: {buddhist_date(birthdate)}
อายุ: {calculate_age(birthdate, renewal_date)}"""

# -------------------------------
# Main Workflow
# -------------------------------

df = pd.read_csv("SCK insurance - Sheet1.csv", encoding="utf-8-sig")

output_rows = []
for _, row in df.iterrows():
    timeline = row['Timeline']
    bundle = row['Bundle']
    family_case = str(row['Family'])
    days_before = get_days_before(timeline)

    # ข้อมูลผู้ถือกรมธรรม์
    holder_info = generate_holder(days_before)

    # ข้อมูลสมาชิก
    members_info = ""
    if "Family" in bundle:
        if "คนซื้อ + คู่สมรส" in family_case and "ลูก" not in family_case:
            members_info = generate_spouse(days_before)
        elif "คู่สมรส + ลูก 1" in family_case:
            members_info = generate_spouse(days_before) + "\n\n" + generate_child(days_before, index=1)
        elif "คู่สมรส + ลูก 2" in family_case:
            members_info = generate_spouse(days_before) + "\n\n" + generate_child(days_before, index=1) + "\n\n" + generate_child(days_before, index=2)
        elif "คนซื้อ + ลูก 1" in family_case:
            members_info = generate_child(days_before, index=1)
        elif "คนซื้อ + ลูก 2" in family_case:
            members_info = generate_child(days_before, index=1) + "\n\n" + generate_child(days_before, index=2)
        elif "บุตรและคู่สมรสอายุเกิน" in family_case:
            members_info = generate_spouse(days_before, overage=True) + "\n\n" + generate_child(days_before, overage=True, index=1)
        elif "บุตรและคู่สมรสเสียชีวิต" in family_case:
            members_info = generate_spouse(days_before, deceased=True) + "\n\n" + generate_child(days_before, deceased=True, index=1)
        elif "บุตร 1 คนอายุเกินและคู่สมรสอายุเกิน" in family_case:
            members_info = generate_spouse(days_before, overage=True) + "\n\n" + generate_child(days_before, overage=True, index=1)
        elif "คู่สมรสอายุเกิน" in family_case:
            members_info = generate_spouse(days_before, overage=True)
        elif "บุตร 1 คน อายุเกิน" in family_case:
            members_info = generate_child(days_before, overage=True, index=1)
        elif "บุตร 2 คน อายุเกิน" in family_case:
            members_info = generate_child(days_before, overage=True, index=1) + "\n\n" + generate_child(days_before, overage=True, index=2)
        elif "คู่สมรสเสียชีวิต และบุตรอายุเกิน 1 คน" in family_case:
            members_info = generate_spouse(days_before, deceased=True) + "\n\n" + generate_child(days_before, overage=True, index=1)
        elif "คู่สมรสเสียชีวิต และบุตรอายุเกิน 2 คน" in family_case:
            members_info = generate_spouse(days_before, deceased=True) + "\n\n" + generate_child(days_before, overage=True, index=1) + "\n\n" + generate_child(days_before, overage=True, index=2)
        elif "คู่สมรสเสียชีวิต" in family_case:
            members_info = generate_spouse(days_before, deceased=True)
        elif "บุตรเสียชีวิต" in family_case:
            members_info = generate_child(days_before, deceased=True, index=1)

    # Status
    end_date = renewal_date + timedelta(days=days_before)
    start_date = end_date - timedelta(days=365)
    status_info = f"""จำนวนวันที่ต่ออายุล่วงหน้า: {days_before} วัน
วันที่ต่ออายุ: {buddhist_date(renewal_date)}
วันสิ้นสุดความคุ้มครอง: {buddhist_date(end_date)}
วันเริ่มสัญญาฉบับปัจจุบัน: {buddhist_date(start_date)}"""

    output_rows.append({
        "Timeline": timeline,
        "Bundle": bundle,
        "Family": family_case,
        "ข้อมูลผู้ถือกรมธรรม์": holder_info,
        "ข้อมูลสมาชิกในกรมธรรม์": members_info,
        "Status": status_info
    })

output_df = pd.DataFrame(output_rows)
output_df.to_csv("SCK_insurance_output.csv", encoding="utf-8-sig", index=False)
