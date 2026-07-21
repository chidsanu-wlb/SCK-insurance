import pandas as pd
import random
from faker import Faker
import datetime
import math

faker_th = Faker('th_TH')
faker_en = Faker('en_US')

# ฟังก์ชันสร้างเลขบัตรประชาชน 13 หลัก (mod 11 checksum)
def generate_thai_id():
    digits = [random.randint(0, 9) for _ in range(12)]
    total = sum([(13 - i) * d for i, d in enumerate(digits)])
    check_digit = (11 - (total % 11)) % 10
    digits.append(check_digit)
    return ''.join(map(str, digits))

# วันที่ต่ออายุ (ใช้ปี พ.ศ.)
renew_date = datetime.date(2569, 8, 15)

# ฟังก์ชันคำนวณอายุจากวันเกิดถึงวันต่ออายุ
def calculate_age(birth_date, ref_date):
    delta_days = (ref_date - birth_date).days
    return int(delta_days // 365.25)

def random_days(timeline):
    if "90 - 30" in str(timeline):
        return random.randint(30, 90)
    elif "29 - 1" in str(timeline):
        return random.randint(1, 29)
    elif "ภายในวันที่หมดอายุ" in str(timeline):
        return 0
    return 0

def calc_dates(timeline):
    days = random_days(timeline)
    end_date = renew_date + datetime.timedelta(days=days)
    start_date = end_date.replace(year=end_date.year - 1)
    return days, end_date, start_date

def create_person(role="adult", over_age=False, dead=False):
    first_name = faker_th.first_name()
    last_name = faker_th.last_name()
    thai_id = generate_thai_id()
    phone = "08" + "".join([str(random.randint(0,9)) for _ in range(8)])
    email = f"{first_name}@email.com"

    # วันเกิดตามเกณฑ์
    if role == "child":
        if over_age:
            # อายุเกิน 15 ปี
            birth_date = faker_en.date_between_dates(
                datetime.date(2553,8,16), datetime.date(2554,8,15)
            )
        else:
            # อายุไม่เกิน 15 ปี
            birth_date = faker_en.date_between_dates(
                datetime.date(2556,1,1), datetime.date(2568,12,31)
            )
    else:  # adult
        if over_age:
            # อายุเกิน 65 ปี
            birth_date = faker_en.date_between_dates(
                datetime.date(2503,8,16), datetime.date(2504,8,15)
            )
        else:
            # อายุไม่เกิน 65 ปี
            birth_date = faker_en.date_of_birth(minimum_age=20, maximum_age=60)

    age = calculate_age(birth_date, renew_date)
    status = "เสียชีวิต" if dead else "มีชีวิต"

    return {
        "ชื่อ": f"{first_name} {last_name}",
        "เลขบัตรประชาชน": thai_id,
        "เบอร์โทรศัพท์": phone,
        "อีเมล": email,
        "วันเกิด": birth_date.strftime("%d %B %Y"),
        "อายุ": age,
        "สถานะ": status
    }

# โหลด CSV
df = pd.read_csv("SCK insurance - Sheet1.csv")

output_rows = []
for idx, row in df.iterrows():
    timeline, bundle, family = row['Timeline'], row['Bundle'], row['Family']
    days, end_date, start_date = calc_dates(timeline)

    holder = create_person(role="adult")

    members = []
    family_str = str(family)

    # ตรวจสอบกรณีต่าง ๆ
    if "คู่สมรส" in family_str:
        over_age = "คู่สมรสอายุเกิน" in family_str
        dead = "คู่สมรสเสียชีวิต" in family_str
        members.append(create_person(role="adult", over_age=over_age, dead=dead))

    if "ลูก 1" in family_str:
        over_age = "บุตร 1 คน อายุเกิน" in family_str
        dead = "บุตรเสียชีวิต" in family_str
        members.append(create_person(role="child", over_age=over_age, dead=dead))

    if "ลูก 2" in family_str:
        over_age = "บุตร 2 คน อายุเกิน" in family_str
        dead = "บุตรเสียชีวิต" in family_str
        members.append(create_person(role="child", over_age=over_age, dead=dead))

    status = f"จำนวนวันที่ต่ออายุล่วงหน้า: {days} วัน | วันที่ต่ออายุ: {renew_date} | วันสิ้นสุดความคุ้มครอง: {end_date} | วันเริ่มสัญญาฉบับปัจจุบัน: {start_date}"

    output_rows.append({
        "Timeline": timeline,
        "Bundle": bundle,
        "Family": family,
        "ข้อมูลผู้ถือกรมธรรม์": holder,
        "ข้อมูลสมาชิกในกรมธรรม์": members,
        "Status": status
    })

output_df = pd.DataFrame(output_rows)
output_df.to_csv("SCK_insurance_output.csv", index=False, encoding="utf-8-sig")
