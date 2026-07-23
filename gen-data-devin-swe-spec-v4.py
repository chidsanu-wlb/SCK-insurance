import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker

# Initialize faker instances
faker_th = Faker('th_TH')
faker_en = Faker('en_US')

# Constants
RENEWAL_DATE = datetime(2569 - 543, 8, 15)  # 15 August 2569 (convert to Gregorian)
RENEWAL_DATE_STR = "15 สิงหาคม 2569"

# Thai month names
THAI_MONTHS = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

# Family case definitions
FAMILY_CASES = {
    "คู่สมรสปกติ ไม่มีบุตร": {"spouse": "normal", "children": 0, "child_status": None},
    "คู่สมรสปกติ บุตร 1 คน": {"spouse": "normal", "children": 1, "child_status": "normal"},
    "คู่สมรสปกติ บุตร 2 คน": {"spouse": "normal", "children": 2, "child_status": "normal"},
    "ไม่มีคู่สมรส บุตร 1 คน": {"spouse": None, "children": 1, "child_status": "normal"},
    "ไม่มีคู่สมรส บุตร 2 คน": {"spouse": None, "children": 2, "child_status": "normal"},
    "ไม่มีคู่สมรส บุตร 1 คนอายุเกิน": {"spouse": None, "children": 1, "child_status": "over_age"},
    "ไม่มีคู่สมรส บุตร 2 คนอายุเกิน": {"spouse": None, "children": 2, "child_status": "over_age"},
    "ไม่มีคู่สมรส บุตรเสียชีวิต 1 คน": {"spouse": None, "children": 1, "child_status": "deceased"},
    "ไม่มีคู่สมรส บุตรเสียชีวิต 2 คน": {"spouse": None, "children": 2, "child_status": "deceased"},
    "คู่สมรสอายุเกิน บุตร 2 คน": {"spouse": "over_age", "children": 2, "child_status": "normal"},
    "คู่สมรสอายุเกิน บุตร 1 คนอายุเกิน": {"spouse": "over_age", "children": 1, "child_status": "over_age"},
    "คู่สมรสอายุเกิน บุตร 2 คนอายุเกิน": {"spouse": "over_age", "children": 2, "child_status": "over_age"},
    "คู่สมรสอายุเกิน บุตรเสียชีวิต 1 คน": {"spouse": "over_age", "children": 1, "child_status": "deceased"},
    "คู่สมรสอายุเกิน บุตรเสียชีวิต 2 คน": {"spouse": "over_age", "children": 2, "child_status": "deceased"},
    "คู่สมรสเสียชีวิต บุตร 2 คน": {"spouse": "deceased", "children": 2, "child_status": "normal"},
    "คู่สมรสเสียชีวิต บุตร 1 คนอายุเกิน": {"spouse": "deceased", "children": 1, "child_status": "over_age"},
    "คู่สมรสเสียชีวิต บุตร 2 คนอายุเกิน": {"spouse": "deceased", "children": 2, "child_status": "over_age"},
    "คู่สมรสเสียชีวิต บุตรเสียชีวิต 1 คน": {"spouse": "deceased", "children": 1, "child_status": "deceased"},
    "คู่สมรสเสียชีวิต บุตรเสียชีวิต 2 คน": {"spouse": "deceased", "children": 2, "child_status": "deceased"},
}


def generate_thai_id():
    """Generate a valid 13-digit Thai ID with mod 11 checksum."""
    while True:
        # Generate first 12 digits randomly
        id_str = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        
        # Calculate checksum
        checksum = 0
        for i in range(12):
            checksum += int(id_str[i]) * (13 - i)
        checksum = checksum % 11
        if checksum < 2:
            checksum = 1 - checksum
        else:
            checksum = 11 - checksum
        
        id_str += str(checksum)
        
        # Validate the ID
        if validate_thai_id(id_str):
            return id_str


def validate_thai_id(id_str):
    """Validate Thai ID checksum."""
    if len(id_str) != 13 or not id_str.isdigit():
        return False
    
    checksum = 0
    for i in range(12):
        checksum += int(id_str[i]) * (13 - i)
    checksum = checksum % 11
    if checksum < 2:
        checksum = 1 - checksum
    else:
        checksum = 11 - checksum
    
    return checksum == int(id_str[12])


def generate_phone():
    """Generate a Thai phone number starting with 08."""
    return '08' + ''.join([str(random.randint(0, 9)) for _ in range(8)])


def format_date_thai(date_obj):
    """Format date as: day month_name buddhist_year."""
    day = date_obj.day
    month = THAI_MONTHS[date_obj.month - 1]
    year = date_obj.year + 543  # Convert to Buddhist year
    return f"{day} {month} {year}"


def calculate_age(birth_date, reference_date):
    """Calculate age in years and days from birth date to reference date."""
    age_delta = reference_date - birth_date
    total_days = age_delta.days
    years = total_days // 365
    days = total_days % 365
    return years, days


def format_age(years, days):
    """Format age as: X ปี Y วัน."""
    return f"{years} ปี {days} วัน"


def get_days_before_renewal(timeline):
    """Calculate random days before renewal based on timeline."""
    if "90 - 30 วันล่วงหน้า" in timeline:
        return random.randint(30, 90)
    elif "29 - 1 วันล่วงหน้า" in timeline:
        return random.randint(1, 29)
    elif "ภายในวันที่หมดอายุ" in timeline:
        return 0
    else:
        return 0


def generate_birth_date_adult_normal(renewal_date, days_before):
    """Generate birth date for normal adult (40-48 years old)."""
    # Age approximately 40-48 years from renewal date
    min_days = 40 * 365
    max_days = 48 * 365
    days_offset = random.randint(min_days, max_days)
    birth_date = renewal_date - timedelta(days=days_offset)
    return birth_date


def generate_birth_date_adult_over_age(renewal_date, days_before):
    """Generate birth date for adult over 65 years."""
    # Born between 15 Aug 2503 + days_before + 1 to 15 Aug 2504
    # Convert to Gregorian: 2503 = 1960, 2504 = 1961
    start_date = datetime(1960, 8, 15) + timedelta(days=days_before + 1)
    end_date = datetime(1961, 8, 15)
    
    random_days = random.randint(0, (end_date - start_date).days)
    birth_date = start_date + timedelta(days=random_days)
    return birth_date


def generate_birth_date_child_normal():
    """Generate birth date for normal child (1-13 years old)."""
    # Between 1 Jan 2556 and 31 Dec 2568
    # Convert to Gregorian: 2556 = 2013, 2568 = 2025
    start_date = datetime(2013, 1, 1)
    end_date = datetime(2025, 12, 31)
    
    random_days = random.randint(0, (end_date - start_date).days)
    birth_date = start_date + timedelta(days=random_days)
    return birth_date


def generate_birth_date_child_over_age(renewal_date, days_before):
    """Generate birth date for child over 15 years."""
    # Born between 15 Aug 2553 + days_before + 1 to 15 Aug 2554
    # Convert to Gregorian: 2553 = 2010, 2554 = 2011
    start_date = datetime(2010, 8, 15) + timedelta(days=days_before + 1)
    end_date = datetime(2011, 8, 15)
    
    random_days = random.randint(0, (end_date - start_date).days)
    birth_date = start_date + timedelta(days=random_days)
    return birth_date


def generate_policy_holder(days_before):
    """Generate policy holder information."""
    first_name_th = faker_th.first_name()
    last_name_th = faker_th.last_name()
    first_name_en = faker_en.first_name()
    
    thai_id = generate_thai_id()
    phone = generate_phone()
    email = f"{first_name_en.lower()}@email.com"
    
    # Generate birth date (normal adult)
    birth_date = generate_birth_date_adult_normal(RENEWAL_DATE, days_before)
    birth_date_str = format_date_thai(birth_date)
    
    # Calculate age at renewal date
    years, days = calculate_age(birth_date, RENEWAL_DATE)
    age_str = format_age(years, days)
    
    policy_holder = f"""ชื่อ: {first_name_th} {last_name_th}
เลขบัตรประชาชน: {thai_id}
เบอร์โทรศัพท์: {phone}
อีเมล: {email}
ว/ด/ป เกิด: {birth_date_str}
อายุ: {age_str}"""
    
    return policy_holder


def generate_spouse(spouse_status, days_before):
    """Generate spouse information based on status."""
    if spouse_status is None:
        return None
    
    first_name_th = faker_th.first_name()
    last_name_th = faker_th.last_name()
    
    if spouse_status == "normal":
        birth_date = generate_birth_date_adult_normal(RENEWAL_DATE, days_before)
    elif spouse_status == "over_age":
        birth_date = generate_birth_date_adult_over_age(RENEWAL_DATE, days_before)
    else:  # deceased
        birth_date = generate_birth_date_adult_normal(RENEWAL_DATE, days_before)
    
    birth_date_str = format_date_thai(birth_date)
    years, days = calculate_age(birth_date, RENEWAL_DATE)
    age_str = format_age(years, days)
    
    status_str = "มีชีวิต" if spouse_status != "deceased" else "เสียชีวิต"
    
    spouse = f"""คู่สมรส: {status_str}
ชื่อ: {first_name_th} {last_name_th}
ว/ด/ป เกิด: {birth_date_str}
อายุ: {age_str}"""
    
    return spouse


def generate_child(child_status, child_num, days_before):
    """Generate child information based on status."""
    first_name_th = faker_th.first_name()
    last_name_th = faker_th.last_name()
    
    if child_status == "normal":
        birth_date = generate_birth_date_child_normal()
    elif child_status == "over_age":
        birth_date = generate_birth_date_child_over_age(RENEWAL_DATE, days_before)
    else:  # deceased
        birth_date = generate_birth_date_child_normal()
    
    birth_date_str = format_date_thai(birth_date)
    years, days = calculate_age(birth_date, RENEWAL_DATE)
    age_str = format_age(years, days)
    
    status_str = "มีชีวิต" if child_status != "deceased" else "เสียชีวิต"
    
    child = f"""บุตรคนที่ {child_num}: {status_str}
ชื่อ: {first_name_th} {last_name_th}
ว/ด/ป เกิด: {birth_date_str}
อายุ: {age_str}"""
    
    return child


def generate_family_members(family_case, days_before):
    """Generate family members based on family case."""
    case_info = FAMILY_CASES.get(family_case, {"spouse": None, "children": 0, "child_status": None})
    
    members = []
    
    # Generate spouse if applicable
    if case_info["spouse"] is not None:
        spouse = generate_spouse(case_info["spouse"], days_before)
        if spouse:
            members.append(spouse)
    
    # Generate children
    for i in range(case_info["children"]):
        child = generate_child(case_info["child_status"], i + 1, days_before)
        members.append(child)
    
    # Join with blank lines
    return "\n\n".join(members) if members else ""


def generate_status(days_before, renewal_date):
    """Generate status information."""
    end_coverage_date = renewal_date + timedelta(days=days_before)
    current_contract_start = end_coverage_date - timedelta(days=365)
    
    end_coverage_str = format_date_thai(end_coverage_date)
    current_contract_str = format_date_thai(current_contract_start)
    
    status = f"""จำนวนวันที่ต่ออายุล่วงหน้า: {days_before} วัน
วันที่ต่ออายุ: {RENEWAL_DATE_STR}
วันสิ้นสุดความคุ้มครอง: {end_coverage_str}
วันเริ่มสัญญาฉบับปัจจุบัน: {current_contract_str}"""
    
    return status


def process_row(row):
    """Process a single row of input data."""
    timeline = row['Timeline']
    bundle = row['Bundle']
    family_case = row['Family']
    
    # Calculate days before renewal
    days_before = get_days_before_renewal(timeline)
    
    # Generate policy holder
    policy_holder = generate_policy_holder(days_before)
    
    # Generate family members if applicable
    if "SCK Personal + SCK Family" in bundle:
        family_members = generate_family_members(family_case, days_before)
    else:  # SCK Personal only
        family_members = ""
    
    # Generate status
    status = generate_status(days_before, RENEWAL_DATE)
    
    return {
        'Timeline': timeline,
        'Bundle': bundle,
        'Family': family_case,
        'ข้อมูลผู้ถือกรมธรรม์': policy_holder,
        'ข้อมูลสมาชิกในกรมธรรม์': family_members,
        'Status': status
    }


def main():
    """Main function to process input CSV and generate output."""
    # Read input CSV
    input_file = "SCK insurance - Sheet2.csv"
    output_file = "SCK_insurance_output_spec_v4.csv"
    
    df = pd.read_csv(input_file, encoding='utf-8-sig')
    
    # Process each row
    output_data = []
    for _, row in df.iterrows():
        output_row = process_row(row)
        output_data.append(output_row)
    
    # Create output DataFrame
    output_df = pd.DataFrame(output_data)
    
    # Write output CSV
    output_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"Generated {len(output_data)} records")
    print(f"Output saved to: {output_file}")


if __name__ == "__main__":
    main()
