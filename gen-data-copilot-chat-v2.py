import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

faker_th = Faker('th_TH')
faker_en = Faker('en_US')

# ค่าคงที่
RENEWAL_DATE = datetime(2026, 8, 15)  # 15 สิงหาคม 2569
MONTHS_TH = ["มกราคม","กุมภาพันธ์","มีนาคม","เมษายน","พฤษภาคม","มิถุนายน",
             "กรกฎาคม","สิงหาคม","กันยายน","ตุลาคม","พฤศจิกายน","ธันวาคม"]

def buddhist_year(year):
    return year + 543

def format_date(date_obj):
    return f"{date_obj.day} {MONTHS_TH[date_obj.month-1]} {buddhist_year(date_obj.year)}"

def calc_age(birthdate, ref_date=RENEWAL_DATE):
    delta = ref_date - birthdate
    years = delta.days // 365
    days = delta.days % 365
    return f"{years} ปี {days} วัน"

def generate_thai_id():
    digits = [random.randint(0,9) for _ in range(12)]
    checksum = sum([(13-i)*digits[i] for i in range(12)]) % 11
    last_digit = (11 - checksum) % 10
    digits.append(last_digit)
    return ''.join(map(str,digits))

def generate_phone():
    return "08" + ''.join([str(random.randint(0,9)) for _ in range(8)])

def generate_holder():
    first_name_th = faker_th.first_name()
    last_name_th = faker_th.last_name()
    first_name_en = faker_en.first_name()
    # อายุระหว่าง 30 ถึง 65 ปี
    start_date = RENEWAL_DATE - timedelta(days=23725)  # 65 ปี
    end_date = RENEWAL_DATE - timedelta(days=10950)   # 30 ปี
    birthdate = start_date + timedelta(days=random.randint(0,(end_date-start_date).days))
    return f"""ชื่อ: {first_name_th} {last_name_th}
เลขบัตรประชาชน: {generate_thai_id()}
เบอร์โทรศัพท์: {generate_phone()}
อีเมล: {first_name_en.lower()}@email.com
ว/ด/ป เกิด: {format_date(birthdate)}
อายุ: {calc_age(birthdate)}"""

def generate_member(role="คู่สมรส", status="มีชีวิต", child=False, overage=False, advance_days=0):
    first_name_th = faker_th.first_name()
    last_name_th = faker_th.last_name()

    if child:
        if overage:
            # ช่วงวันเกิดสำหรับบุตรอายุเกิน
            start_date = datetime(2010, 8, 16) + timedelta(days=advance_days)
            end_date = datetime(2011, 8, 15)
            birthdate = start_date + timedelta(days=random.randint(0,(end_date-start_date).days))
        else:
            # ช่วงวันเกิดสำหรับบุตรปกติ
            start_date = datetime(2013,1,1)
            end_date = datetime(2025,12,31)
            birthdate = start_date + timedelta(days=random.randint(0,(end_date-start_date).days))
    else:
        if overage:
            # ช่วงวันเกิดสำหรับคู่สมรสอายุเกิน
            start_date = datetime(1960,8,16) + timedelta(days=advance_days)
            end_date = datetime(1961,8,15)
            birthdate = start_date + timedelta(days=random.randint(0,(end_date-start_date).days))
        else:
            # ปกติ: อายุ 30-40 ปี
            birthdate = RENEWAL_DATE - timedelta(days=random.randint(10950,14600))

    return f"""{role}: {status}
ชื่อ: {first_name_th} {last_name_th}
ว/ด/ป เกิด: {format_date(birthdate)}
อายุ: {calc_age(birthdate)}"""

def calc_status(timeline):
    if "90 - 30" in timeline:
        days = random.randint(30,90)
    elif "29 - 1" in timeline:
        days = random.randint(1,29)
    else:
        days = 0
    end_date = RENEWAL_DATE + timedelta(days=days)
    start_date = end_date - timedelta(days=365)
    return days, f"""จำนวนวันที่ต่ออายุล่วงหน้า: {days} วัน
วันที่ต่ออายุ: {format_date(RENEWAL_DATE)}
วันสิ้นสุดความคุ้มครอง: {format_date(end_date)}
วันเริ่มสัญญาฉบับปัจจุบัน: {format_date(start_date)}"""

# อ่าน CSV
df = pd.read_csv("SCK insurance - Sheet1.csv")

output_rows = []
for idx,row in df.iterrows():
    holder_info = generate_holder()
    member_info = ""
    family_case = str(row['Family'])
    advance_days, status_info = calc_status(row['Timeline'])

    # กรณีปกติ
    if "คนซื้อ + คู่สมรส" in family_case and "ลูก" not in family_case:
        member_info = generate_member("คู่สมรส", advance_days=advance_days)
    elif "คู่สมรส + ลูก 1" in family_case:
        member_info = generate_member("คู่สมรส", advance_days=advance_days) + "\n\n" + generate_member("บุตรคนที่ 1", child=True, advance_days=advance_days)
    elif "คู่สมรส + ลูก 2" in family_case:
        member_info = generate_member("คู่สมรส", advance_days=advance_days) + "\n\n" + generate_member("บุตรคนที่ 1", child=True, advance_days=advance_days) + "\n\n" + generate_member("บุตรคนที่ 2", child=True, advance_days=advance_days)
    elif "ลูก 1" in family_case and "คู่สมรส" not in family_case:
        member_info = generate_member("บุตรคนที่ 1", child=True, advance_days=advance_days)
    elif "ลูก 2" in family_case and "คู่สมรส" not in family_case:
        member_info = generate_member("บุตรคนที่ 1", child=True, advance_days=advance_days) + "\n\n" + generate_member("บุตรคนที่ 2", child=True, advance_days=advance_days)

    # กรณีอายุเกิน
    elif "บุตรและคู่สมรสอายุเกิน" in family_case:
        member_info = generate_member("คู่สมรส", overage=True, advance_days=advance_days) + "\n\n" + generate_member("บุตร", child=True, overage=True, advance_days=advance_days)
    elif "บุตร 1 คนอายุเกินและคู่สมรสอายุเกิน" in family_case:
        member_info = generate_member("คู่สมรส", overage=True, advance_days=advance_days) + "\n\n" + generate_member("บุตรคนที่ 1", child=True, overage=True, advance_days=advance_days)
    elif "คู่สมรสอายุเกิน" in family_case:
        member_info = generate_member("คู่สมรส", overage=True, advance_days=advance_days)
    elif "บุตร 1 คน อายุเกิน" in family_case:
        member_info = generate_member("บุตรคนที่ 1", child=True, overage=True, advance_days=advance_days)
    elif "บุตร 2 คน อายุเกิน" in family_case:
        member_info = generate_member("บุตรคนที่ 1", child=True, overage=True, advance_days=advance_days) + "\n\n" + generate_member("บุตรคนที่ 2", child=True, overage=True, advance_days=advance_days)

        # กรณีเสียชีวิต
    elif "บุตรและคู่สมรสเสียชีวิต" in family_case:
        member_info = generate_member("คู่สมรส", status="เสียชีวิต", advance_days=advance_days) + "\n\n" + generate_member("บุตร", child=True, status="เสียชีวิต", advance_days=advance_days)
    elif "คู่สมรสเสียชีวิต และบุตรอายุเกิน 1 คน" in family_case:
        member_info = generate_member("คู่สมรส", status="เสียชีวิต", advance_days=advance_days) + "\n\n" + generate_member("บุตรคนที่ 1", child=True, overage=True, advance_days=advance_days)
    elif "คู่สมรสเสียชีวิต และบุตรอายุเกิน 2 คน" in family_case:
        member_info = generate_member("คู่สมรส", status="เสียชีวิต", advance_days=advance_days) + "\n\n" + generate_member("บุตรคนที่ 1", child=True, overage=True, advance_days=advance_days) + "\n\n" + generate_member("บุตรคนที่ 2", child=True, overage=True, advance_days=advance_days)
    elif "คู่สมรสเสียชีวิต" in family_case:
        member_info = generate_member("คู่สมรส", status="เสียชีวิต", advance_days=advance_days)
    elif "บุตรเสียชีวิต" in family_case:
        member_info = generate_member("บุตร", child=True, status="เสียชีวิต", advance_days=advance_days)

    # เพิ่มลงในผลลัพธ์
    output_rows.append({
        "Timeline": row['Timeline'],
        "Bundle": row['Bundle'],
        "Family": row['Family'],
        "ข้อมูลผู้ถือกรมธรรม์": holder_info,
        "ข้อมูลสมาชิกในกรมธรรม์": member_info,
        "Status": status_info
    })

# เขียนออกเป็น CSV
out_df = pd.DataFrame(output_rows)
out_df.to_csv("SCK_insurance_output.csv", encoding="utf-8-sig", index=False)
