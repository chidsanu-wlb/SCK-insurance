import random
from datetime import datetime, timedelta
import pandas as pd
from faker import Faker

# ==========================================
# 1. CONSTANTS & INITIALIZATION
# ==========================================
RENEWAL_DATE = datetime(2026, 8, 15)

THAI_MONTHS = [
    "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

# Initialize Faker
fake_th = Faker('th_TH')
fake_en = Faker('en_US')

# Family Mapping Table from Specification
FAMILY_MAPPING = {
    "คู่สมรสปกติ ไม่มีบุตร": ("มีชีวิต (ปกติ)", "ไม่มี", "ไม่มี"),
    "คู่สมรสปกติ บุตร 1 คน": ("มีชีวิต (ปกติ)", "มีชีวิต (ปกติ)", "ไม่มี"),
    "คู่สมรสปกติ บุตร 2 คน": ("มีชีวิต (ปกติ)", "มีชีวิต (ปกติ)", "มีชีวิต (ปกติ)"),
    "ไม่มีคู่สมรส บุตร 1 คน": ("ไม่มี", "มีชีวิต (ปกติ)", "ไม่มี"),
    "ไม่มีคู่สมรส บุตร 2 คน": ("ไม่มี", "มีชีวิต (ปกติ)", "มีชีวิต (ปกติ)"),
    "ไม่มีคู่สมรส บุตร 1 คนอายุเกิน": ("ไม่มี", "มีชีวิต (อายุเกิน)", "ไม่มี"),
    "ไม่มีคู่สมรส บุตร 2 คนอายุเกิน": ("ไม่มี", "มีชีวิต (อายุเกิน)", "มีชีวิต (อายุเกิน)"),
    "ไม่มีคู่สมรส บุตรเสียชีวิต 1 คน": ("ไม่มี", "เสียชีวิต", "ไม่มี"),
    "ไม่มีคู่สมรส บุตรเสียชีวิต 2 คน": ("ไม่มี", "เสียชีวิต", "เสียชีวิต"),
    "คู่สมรสอายุเกิน บุตร 2 คน": ("มีชีวิต (อายุเกิน)", "มีชีวิต (ปกติ)", "มีชีวิต (ปกติ)"),
    "คู่สมรสอายุเกิน บุตร 1 คนอายุเกิน": ("มีชีวิต (อายุเกิน)", "มีชีวิต (อายุเกิน)", "ไม่มี"),
    "คู่สมรสอายุเกิน บุตร 2 คนอายุเกิน": ("มีชีวิต (อายุเกิน)", "มีชีวิต (อายุเกิน)", "มีชีวิต (อายุเกิน)"),
    "คู่สมรสอายุเกิน บุตรเสียชีวิต 1 คน": ("มีชีวิต (อายุเกิน)", "เสียชีวิต", "ไม่มี"),
    "คู่สมรสอายุเกิน บุตรเสียชีวิต 2 คน": ("มีชีวิต (อายุเกิน)", "เสียชีวิต", "เสียชีวิต"),
    "คู่สมรสเสียชีวิต บุตร 2 คน": ("เสียชีวิต", "มีชีวิต (ปกติ)", "มีชีวิต (ปกติ)"),
    "คู่สมรสเสียชีวิต บุตร 1 คนอายุเกิน": ("เสียชีวิต", "มีชีวิต (อายุเกิน)", "ไม่มี"),
    "คู่สมรสเสียชีวิต บุตร 2 คนอายุเกิน": ("เสียชีวิต", "มีชีวิต (อายุเกิน)", "มีชีวิต (อายุเกิน)"),
    "คู่สมรสเสียชีวิต บุตรเสียชีวิต 1 คน": ("เสียชีวิต", "เสียชีวิต", "ไม่มี"),
    "คู่สมรสเสียชีวิต บุตรเสียชีวิต 2 คน": ("เสียชีวิต", "เสียชีวิต", "เสียชีวิต")
}

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def generate_thai_id():
    digits = [random.randint(1, 9)] + [random.randint(0, 9) for _ in range(11)]
    sum_val = sum(digits[i] * (13 - i) for i in range(12))
    check_digit = (11 - (sum_val % 11)) % 10
    digits.append(check_digit)
    return "".join(map(str, digits))

def format_thai_date(dt):
    day = dt.day
    month_th = THAI_MONTHS[dt.month]
    year_be = dt.year + 543
    return f"{day} {month_th} {year_be}"

def calculate_age(birth_date, ref_date):
    years = ref_date.year - birth_date.year
    try:
        last_birthday = datetime(ref_date.year, birth_date.month, birth_date.day)
    except ValueError:
        last_birthday = datetime(ref_date.year, birth_date.month, birth_date.day - 1)
    if ref_date < last_birthday:
        years -= 1
        try:
            last_birthday = datetime(ref_date.year - 1, birth_date.month, birth_date.day)
        except ValueError:
            last_birthday = datetime(ref_date.year - 1, birth_date.month, birth_date.day - 1)
    days = (ref_date - last_birthday).days
    return years, days

def get_random_birthdate_for_adult(status_type, advance_days):
    if "อายุเกิน" in status_type:
        min_days = int(65 * 365.25) + advance_days + 1
        max_days = int(66 * 365.25)
    else:
        min_days = int(40 * 365.25)
        max_days = int(60 * 365.25)
    days_ago = random.randint(min_days, max_days)
    return RENEWAL_DATE - timedelta(days=days_ago)

def get_random_birthdate_for_child(status_type, advance_days):
    if "อายุเกิน" in status_type:
        min_days = int(15 * 365.25) + advance_days + 1
        max_days = int(16 * 365.25)
    else:
        min_days = int(1 * 365.25)
        max_days = int(13 * 365.25)
    days_ago = random.randint(min_days, max_days)
    return RENEWAL_DATE - timedelta(days=days_ago)

def create_person_info_str(first_name, last_name, birth_date):
    years, days = calculate_age(birth_date, RENEWAL_DATE)
    date_str = format_thai_date(birth_date)
    return (
        f"ชื่อ: {first_name} {last_name}\n"
        f"ว/ด/ป เกิด: {date_str}\n"
        f"อายุ: {years} ปี {days} วัน"
    )

# ==========================================
# 3. MAIN DATA GENERATION LOGIC
# ==========================================
def process_mock_data(input_file_path, output_file_path):
    df = pd.read_csv(input_file_path)
    
    out_policyholder_list = []
    out_members_list = []
    out_status_list = []
    
    for idx, row in df.iterrows():
        timeline = str(row['Timeline']).strip()
        bundle = str(row['Bundle']).strip() if pd.notna(row['Bundle']) else ""
        family_str = str(row['Family']).strip() if pd.notna(row['Family']) else ""
        
        # ----------------------------------
        # 1. Timeline & Advance Days
        # ----------------------------------
        if timeline == "90 - 30 วันล่วงหน้า":
            advance_days = random.randint(30, 90)
        elif timeline == "29 - 1 วันล่วงหน้า":
            advance_days = random.randint(1, 29)
        elif timeline == "ภายในวันที่หมดอายุ":
            advance_days = 0
        else:
            advance_days = 0
            
        end_coverage_date = RENEWAL_DATE + timedelta(days=advance_days)
        start_contract_date = end_coverage_date - timedelta(days=365)
        
        # ----------------------------------
        # 2. ข้อมูลผู้ถือกรมธรรม์ (Policyholder)
        # ----------------------------------
        ph_first_name_th = fake_th.first_name()
        ph_last_name_th = fake_th.last_name()
        ph_first_name_en = fake_en.first_name()
        ph_id = generate_thai_id()
        ph_phone = f"08{random.randint(10000000, 99999999)}"
        ph_email = f"{ph_first_name_en.lower()}@email.com"
        ph_birth_date = get_random_birthdate_for_adult("ปกติ", advance_days)
        
        ph_years, ph_days = calculate_age(ph_birth_date, RENEWAL_DATE)
        ph_birth_str = format_thai_date(ph_birth_date)
        
        policyholder_text = (
            f"ชื่อ: {ph_first_name_th} {ph_last_name_th}\n"
            f"เลขบัตรประชาชน: {ph_id}\n"
            f"เบอร์โทรศัพท์: {ph_phone}\n"
            f"อีเมล: {ph_email}\n"
            f"ว/ด/ป เกิด: {ph_birth_str}\n"
            f"อายุ: {ph_years} ปี {ph_days} วัน"
        )
        
        # ----------------------------------
        # 3. ข้อมูลสมาชิกในกรมธรรม์ (Members)
        # ----------------------------------
        member_blocks = []
        
        if bundle == "SCK Personal" or not family_str:
            members_text = ""
        else:
            spouse_type, child1_type, child2_type = FAMILY_MAPPING.get(
                family_str, ("ไม่มี", "ไม่มี", "ไม่มี")
            )
            
            # คู่สมรส
            if spouse_type != "ไม่มี":
                status_label = "เสียชีวิต" if spouse_type == "เสียชีวิต" else "มีชีวิต"
                s_first = fake_th.first_name()
                s_dob = get_random_birthdate_for_adult(spouse_type, advance_days)
                info_str = create_person_info_str(s_first, ph_last_name_th, s_dob)
                block = f"คู่สมรส: {status_label}\n{info_str}"
                member_blocks.append(block)
                
            # บุตรคนที่ 1
            if child1_type != "ไม่มี":
                status_label = "เสียชีวิต" if child1_type == "เสียชีวิต" else "มีชีวิต"
                c1_first = fake_th.first_name()
                c1_dob = get_random_birthdate_for_child(child1_type, advance_days)
                info_str = create_person_info_str(c1_first, ph_last_name_th, c1_dob)
                block = f"บุตรคนที่ 1: {status_label}\n{info_str}"
                member_blocks.append(block)
                
            # บุตรคนที่ 2
            if child2_type != "ไม่มี":
                status_label = "เสียชีวิต" if child2_type == "เสียชีวิต" else "มีชีวิต"
                c2_first = fake_th.first_name()
                c2_dob = get_random_birthdate_for_child(child2_type, advance_days)
                info_str = create_person_info_str(c2_first, ph_last_name_th, c2_dob)
                block = f"บุตรคนที่ 2: {status_label}\n{info_str}"
                member_blocks.append(block)
                
            members_text = "\n\n".join(member_blocks)
            
        # ----------------------------------
        # 4. Status Column
        # ----------------------------------
        status_text = (
            f"จำนวนวันที่ต่ออายุล่วงหน้า: {advance_days} วัน\n"
            f"วันที่ต่ออายุ: {format_thai_date(RENEWAL_DATE)}\n"
            f"วันสิ้นสุดความคุ้มครอง: {format_thai_date(end_coverage_date)}\n"
            f"วันเริ่มสัญญาฉบับปัจจุบัน: {format_thai_date(start_contract_date)}"
        )
        
        out_policyholder_list.append(policyholder_text)
        out_members_list.append(members_text)
        out_status_list.append(status_text)
        
    df['ข้อมูลผู้ถือกรมธรรม์'] = out_policyholder_list
    df['ข้อมูลสมาชิกในกรมธรรม์'] = out_members_list
    df['Status'] = out_status_list
    
    # Save output CSV with utf-8-sig for Thai Excel compatibility
    df.to_csv(output_file_path, index=False, encoding='utf-8-sig')
    print(f"Successfully processed {len(df)} rows. Saved to '{output_file_path}'.")

# ==========================================
# 4. ENTRY POINT
# ==========================================
if __name__ == "__main__":
    process_mock_data("SCK insurance - Sheet2.csv", "SCK_insurance_Output_Copilot.csv")
