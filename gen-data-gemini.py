import os
import random
import re
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

# ==========================================
# 1. Initialization & Constants
# ==========================================
faker_th = Faker('th_TH')
faker_en = Faker('en_US')

THAI_MONTHS = [
    "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

# วันที่ต่ออายุคงที่: 15 สิงหาคม 2569 (2026)
RENEWAL_DATE = datetime(2026, 8, 15)

# ==========================================
# 2. Helper Functions & Age Validation
# ==========================================

def format_thai_date(dt: datetime) -> str:
    """แปลง datetime เป็นรูปแบบ 'วัน เดือน (ไทย) ปี (พ.ศ.)'"""
    day = dt.day
    month = THAI_MONTHS[dt.month]
    year_be = dt.year + 543
    return f"{day} {month} {year_be}"

def calculate_age(dob: datetime, ref_date: datetime = RENEWAL_DATE):
    """คำนวณอายุเป็น X ปี Y วัน ณ วันต่ออายุ (15 สิงหาคม 2569)"""
    years = ref_date.year - dob.year
    if (ref_date.month, ref_date.day) < (dob.month, dob.day):
        years -= 1
    
    try:
        last_birthday = datetime(dob.year + years, dob.month, dob.day)
    except ValueError:  # รองรับกรณี 29 ก.พ.
        last_birthday = datetime(dob.year + years, dob.month, dob.day - 1)
        
    days = (ref_date - last_birthday).days
    return years, days

def generate_thai_id() -> str:
    """สร้างเลขบัตรประชาชน 13 หลัก พร้อม Checksum mod 11"""
    first_digit = str(random.choice([1, 2, 3, 4, 5, 6, 7, 8]))
    middle_11 = "".join([str(random.randint(0, 9)) for _ in range(11)])
    digits = [int(x) for x in (first_digit + middle_11)]
    
    total = sum(digits[i] * (13 - i) for i in range(12))
    mod = total % 11
    check_digit = (11 - mod) % 10
    return "".join(map(str, digits)) + str(check_digit)

def generate_phone() -> str:
    """สร้างเบอร์โทรศัพท์มือถือ 10 หลัก ขึ้นต้นด้วย 08"""
    return "08" + "".join([str(random.randint(0, 9)) for _ in range(8)])

def random_date(start_date: datetime, end_date: datetime) -> datetime:
    """สุ่ม datetime ระหว่างช่วง start_date ถึง end_date"""
    delta_days = (end_date - start_date).days
    if delta_days <= 0:
        return start_date
    rand_days = random.randint(0, delta_days)
    return start_date + timedelta(days=rand_days)

def generate_dob_child(over_age: bool, advance_days: int) -> datetime:
    """สุ่มวันเกิดบุตรตามเกณฑ์อายุ + ตรวจสอบความถูกต้อง"""
    while True:
        if not over_age:
            # กรณีปกติ (อายุไม่เกิน 15 ปี): 1 ม.ค. 2556 (2013) ถึง 31 ธ.ค. 2568 (2025)
            start = datetime(2013, 1, 1)
            end = datetime(2025, 12, 31)
            dob = random_date(start, end)
        else:
            # กรณีอายุเกินเกณฑ์ (> 15 ปี):
            # (15 ส.ค. 2553 [2010] + advance_days + 1) ถึง 15 ส.ค. 2554 [2011]
            start = datetime(2010, 8, 15) + timedelta(days=advance_days + 1)
            end = datetime(2011, 8, 15)
            if start > end:
                start = end
            dob = random_date(start, end)
            
        # Post-validation:
        new_contract_date = RENEWAL_DATE + timedelta(days=advance_days)
        age_at_new_contract = new_contract_date.year - dob.year - (
            (new_contract_date.month, new_contract_date.day) < (dob.month, dob.day)
        )
        if over_age and age_at_new_contract > 15:
            return dob
        elif not over_age and age_at_new_contract <= 15:
            return dob

def generate_dob_adult(over_age: bool, advance_days: int) -> datetime:
    """สุ่มวันเกิดผู้ใหญ่ (ผู้ถือ/คู่สมรส) ตามเกณฑ์อายุ + ตรวจสอบความถูกต้อง"""
    while True:
        if not over_age:
            # กรณีปกติ (อายุไม่เกิน 65 ปี, ประมาณ 40-48 ปี):
            # (RENEWAL_DATE - 17520 วัน) ถึง (RENEWAL_DATE - 14600 วัน)
            start = RENEWAL_DATE - timedelta(days=17520)
            end = RENEWAL_DATE - timedelta(days=14600)
            dob = random_date(start, end)
        else:
            # กรณีอายุเกินเกณฑ์ (> 65 ปี):
            # (15 ส.ค. 2503 [1960] + advance_days + 1) ถึง 15 ส.ค. 2504 [1961]
            start = datetime(1960, 8, 15) + timedelta(days=advance_days + 1)
            end = datetime(1961, 8, 15)
            if start > end:
                start = end
            dob = random_date(start, end)
            
        # Post-validation:
        years, _ = calculate_age(dob)
        if over_age and years > 65:
            return dob
        elif not over_age and years <= 65:
            return dob

# ==========================================
# 3. Component Builders
# ==========================================

def build_holder_info() -> str:
    """สร้าง Text สำหรับ Column 4: ข้อมูลผู้ถือกรมธรรม์"""
    fname_th = faker_th.first_name()
    lname_th = faker_th.last_name()
    fname_en = faker_en.first_name()
    
    cid = generate_thai_id()
    phone = generate_phone()
    email = f"{fname_en.lower()}@email.com"
    
    # ผู้ถือกรมธรรม์เป็นผู้ใหญ่อายุปกติ (ไม่เกิน 65 ปี)
    dob = generate_dob_adult(over_age=False, advance_days=0)
    dob_str = format_thai_date(dob)
    years, days = calculate_age(dob)
    
    lines = [
        f"ชื่อ: {fname_th} {lname_th}",
        f"เลขบัตรประชาชน: {cid}",
        f"เบอร์โทรศัพท์: {phone}",
        f"อีเมล: {email}",
        f"ว/ด/ป เกิด: {dob_str}",
        f"อายุ: {years} ปี {days} วัน"
    ]
    return "\n".join(lines)

def build_status_info(advance_days: int) -> str:
    """สร้าง Text สำหรับ Column 6: Status"""
    end_cov = RENEWAL_DATE + timedelta(days=advance_days)
    # วันเริ่มสัญญาฉบับปัจจุบัน = วันสิ้นสุดความคุ้มครอง - 1 ปี
    start_cov = datetime(end_cov.year - 1, end_cov.month, end_cov.day)
    
    lines = [
        f"จำนวนวันที่ต่ออายุล่วงหน้า: {advance_days} วัน",
        f"วันที่ต่ออายุ: {format_thai_date(RENEWAL_DATE)}",
        f"วันสิ้นสุดความคุ้มครอง: {format_thai_date(end_cov)}",
        f"วันเริ่มสัญญาฉบับปัจจุบัน: {format_thai_date(start_cov)}"
    ]
    return "\n".join(lines)

def generate_member_block(role_title: str, status_str: str, is_adult: bool, over_age: bool, advance_days: int) -> str:
    """สร้างข้อมูลสมาชิกลูกย่อย 1 คน"""
    fname = faker_th.first_name()
    lname = faker_th.last_name()
    
    if is_adult:
        dob = generate_dob_adult(over_age=over_age, advance_days=advance_days)
    else:
        dob = generate_dob_child(over_age=over_age, advance_days=advance_days)
        
    dob_str = format_thai_date(dob)
    years, days = calculate_age(dob)
    
    lines = [
        f"{role_title}: {status_str}",
        f"ชื่อ: {fname} {lname}",
        f"ว/ด/ป เกิด: {dob_str}",
        f"อายุ: {years} ปี {days} วัน"
    ]
    return "\n".join(lines)

def build_family_info(bundle: str, family_case: str, advance_days: int) -> str:
    """สร้าง Text สำหรับ Column 5: ข้อมูลสมาชิกในกรมธรรม์"""
    if str(bundle).strip() == "SCK Personal" or pd.isna(family_case):
        return ""
    
    # ทำความสะอาดข้อความเพื่อเปรียบเทียบ
    case_clean = re.sub(r'\s+', '', str(family_case))
    members = []
    
    # -------------------------------------------------------------
    # ครอบคลุมการจับคู่ทั้ง 15 Family Cases
    # -------------------------------------------------------------
    if "กรณีปกติ1" in case_clean:
        members.append(generate_member_block("คู่สมรส", "มีชีวิต", True, False, advance_days))
        
    elif "กรณีปกติ2" in case_clean:
        members.append(generate_member_block("คู่สมรส", "มีชีวิต", True, False, advance_days))
        members.append(generate_member_block("บุตรคนที่ 1", "มีชีวิต", False, False, advance_days))
        
    elif "กรณีปกติ3" in case_clean:
        members.append(generate_member_block("คู่สมรส", "มีชีวิต", True, False, advance_days))
        members.append(generate_member_block("บุตรคนที่ 1", "มีชีวิต", False, False, advance_days))
        members.append(generate_member_block("บุตรคนที่ 2", "มีชีวิต", False, False, advance_days))
        
    elif "กรณีปกติ4" in case_clean:
        members.append(generate_member_block("บุตรคนที่ 1", "มีชีวิต", False, False, advance_days))
        
    elif "กรณีปกติ5" in case_clean:
        members.append(generate_member_block("บุตรคนที่ 1", "มีชีวิต", False, False, advance_days))
        members.append(generate_member_block("บุตรคนที่ 2", "มีชีวิต", False, False, advance_days))
        
    elif "กรณีบุตรและคู่สมรสอายุเกิน" in case_clean:
        members.append(generate_member_block("คู่สมรส", "มีชีวิต", True, True, advance_days))
        members.append(generate_member_block("บุตรคนที่ 1", "มีชีวิต", False, True, advance_days))
        
    elif "กรณีบุตรและคู่สมรสเสียชีวิต" in case_clean:
        members.append(generate_member_block("คู่สมรส", "เสียชีวิต", True, False, advance_days))
        members.append(generate_member_block("บุตรคนที่ 1", "เสียชีวิต", False, False, advance_days))
        
    elif "กรณีบุตร1คนอายุเกินและคู่สมรสอายุเกิน" in case_clean:
        members.append(generate_member_block("คู่สมรส", "มีชีวิต", True, True, advance_days))
        members.append(generate_member_block("บุตรคนที่ 1", "มีชีวิต", False, True, advance_days))
        
    elif "กรณีคู่สมรสอายุเกิน" in case_clean:
        members.append(generate_member_block("คู่สมรส", "มีชีวิต", True, True, advance_days))
        
    elif "กรณีบุตร1คนอายุเกิน" in case_clean:
        members.append(generate_member_block("บุตรคนที่ 1", "มีชีวิต", False, True, advance_days))
        
    elif "กรณีบุตร2คนอายุเกิน" in case_clean:
        members.append(generate_member_block("บุตรคนที่ 1", "มีชีวิต", False, True, advance_days))
        members.append(generate_member_block("บุตรคนที่ 2", "มีชีวิต", False, True, advance_days))
        
    elif "กรณีคู่สมรสเสียชีวิตและบุตรอายุเกิน1คน" in case_clean:
        members.append(generate_member_block("คู่สมรส", "เสียชีวิต", True, False, advance_days))
        members.append(generate_member_block("บุตรคนที่ 1", "มีชีวิต", False, True, advance_days))
        
    elif "กรณีคู่สมรสเสียชีวิตและบุตรอายุเกิน2คน" in case_clean:
        members.append(generate_member_block("คู่สมรส", "เสียชีวิต", True, False, advance_days))
        members.append(generate_member_block("บุตรคนที่ 1", "มีชีวิต", False, True, advance_days))
        members.append(generate_member_block("บุตรคนที่ 2", "มีชีวิต", False, True, advance_days))
        
    elif "กรณีคู่สมรสเสียชีวิต" in case_clean:
        members.append(generate_member_block("คู่สมรส", "เสียชีวิต", True, False, advance_days))
        
    elif "กรณีบุตรเสียชีวิต" in case_clean:
        members.append(generate_member_block("บุตรคนที่ 1", "เสียชีวิต", False, False, advance_days))

    # แต่ละคนแยกด้วย blank line (เว้น 1 บรรทัด)
    return "\n\n".join(members)

# ==========================================
# 4. Main Processing
# ==========================================

def process_insurance_data(input_csv_path: str, output_csv_path: str):
    df = pd.read_csv(input_csv_path)
    
    out_holders = []
    out_members = []
    out_statuses = []
    
    for idx, row in df.iterrows():
        timeline = str(row['Timeline']).strip()
        bundle = str(row['Bundle']).strip()
        family = row['Family']
        
        # 1. คำนวณจำนวนวันต่ออายุล่วงหน้า ตาม Timeline
        if timeline == "90 - 30 วันล่วงหน้า":
            advance_days = random.randint(30, 90)
        elif timeline == "29 - 1 วันล่วงหน้า":
            advance_days = random.randint(1, 29)
        else:  # ภายในวันที่หมดอายุ
            advance_days = 0
            
        # 2. สร้างข้อมูล Column 4: ข้อมูลผู้ถือกรมธรรม์
        holder_text = build_holder_info()
        
        # 3. สร้างข้อมูล Column 5: ข้อมูลสมาชิกในกรมธรรม์
        member_text = build_family_info(bundle, family, advance_days)
        
        # 4. สร้างข้อมูล Column 6: Status
        status_text = build_status_info(advance_days)
        
        out_holders.append(holder_text)
        out_members.append(member_text)
        out_statuses.append(status_text)
        
    # บันทึกลง DataFrame
    df['ข้อมูลผู้ถือกรมธรรม์'] = out_holders
    df['ข้อมูลสมาชิกในกรมธรรม์'] = out_members
    df['Status'] = out_statuses
    
    # Export ไฟล์เป็น UTF-8-SIG สำหรับ Excel ภาษาไทย
    df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
    print(f"ประมวลผลเสร็จสิ้น! บันทึกไฟล์ผลลัพธ์ที่: {output_csv_path}")

if __name__ == "__main__":
    input_file = "SCK insurance - Sheet1.csv"
    output_file = "SCK_insurance_Output.csv"
    
    process_insurance_data(input_file, output_file)