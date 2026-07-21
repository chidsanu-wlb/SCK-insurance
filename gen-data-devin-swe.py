import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

faker_th = Faker('th_TH')
faker_en = Faker('en_US')

renewal_date = datetime(2026, 8, 15)
date_format = "%d %B %Y"

def generate_name():
    return f"{faker_th.first_name()} {faker_th.last_name()}"

def random_birthdate(age_min, age_max):
    # สุ่มวันเกิดตามช่วงอายุ
    days = random.randint(age_min*365, age_max*365)
    return renewal_date - timedelta(days=days)

def calculate_dates(timeline):
    if "90 - 30" in timeline:
        days = random.randint(30, 90)
    elif "29 - 1" in timeline:
        days = random.randint(1, 29)
    else:
        days = 0
    end_date = renewal_date + timedelta(days=days)
    start_date = end_date - timedelta(days=365)
    return days, renewal_date.strftime(date_format), end_date.strftime(date_format), start_date.strftime(date_format)

def generate_holder():
    birthdate = random_birthdate(30, 50)
    age = (renewal_date - birthdate).days // 365
    return {
        "ชื่อ": generate_name(),
        "เลขบัตรประชาชน": faker_en.ssn(),
        "เบอร์โทรศัพท์": "08" + "".join([str(random.randint(0,9)) for _ in range(8)]),
        "อีเมล": f"{faker_en.first_name().lower()}@email.com",
        "ว/ด/ป เกิด": birthdate.strftime(date_format),
        "อายุ": f"{age} ปี"
    }

def generate_spouse(case, days):
    if "เสียชีวิต" in case:
        status = "เสียชีวิต"
    else:
        status = "มีชีวิต"
    if "อายุเกิน" in case:
        birthdate = datetime(1960, 8, 15) + timedelta(days=days+1)
    else:
        birthdate = random_birthdate(30, 50)
    age = (renewal_date - birthdate).days // 365
    return {
        "ชื่อ": generate_name(),
        "ว/ด/ป เกิด": birthdate.strftime(date_format),
        "อายุ": f"{age} ปี",
        "สถานะ": status
    }

def generate_child(case, days):
    if "เสียชีวิต" in case:
        status = "เสียชีวิต"
    else:
        status = "มีชีวิต"
    if "อายุเกิน" in case:
        birthdate = datetime(2003, 8, 15) + timedelta(days=days+1)
    else:
        birthdate = random_birthdate(1, 13)
    age = (renewal_date - birthdate).days // 365
    return {
        "ชื่อ": generate_name(),
        "ว/ด/ป เกิด": birthdate.strftime(date_format),
        "อายุ": f"{age} ปี",
        "สถานะ": status
    }

df = pd.read_csv("SCK insurance - Sheet1.csv")
output = []

for _, row in df.iterrows():
    days, renewal_str, end_str, start_str = calculate_dates(row["Timeline"])
    holder = generate_holder()
    members = []
    case = str(row["Family"])
    if "คู่สมรส" in case:
        members.append({"คู่สมรส": generate_spouse(case, days)})
    if "ลูก 1" in case:
        members.append({"บุตรคนที่ 1": generate_child(case, days)})
    if "ลูก 2" in case:
        members.append({"บุตรคนที่ 2": generate_child(case, days)})
    status_info = {
        "จำนวนวันที่ต่ออายุล่วงหน้า": f"{days} วัน",
        "วันที่ต่ออายุ": renewal_str,
        "วันสิ้นสุดความคุ้มครอง": end_str,
        "วันเริ่มสัญญาฉบับปัจจุบัน": start_str
    }
    output.append({
        "Timeline": row["Timeline"],
        "Bundle": row["Bundle"],
        "Family": row["Family"],
        "ข้อมูลผู้ถือกรมธรรม์": holder,
        "ข้อมูลสมาชิกในกรมธรรม์": members,
        "Status": status_info
    })

out_df = pd.DataFrame(output)
out_df.to_csv("SCK_insurance_output.csv", index=False, encoding="utf-8-sig")
