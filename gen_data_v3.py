import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker

# Initialize Faker with Thai and English locales
faker_th = Faker('th_TH')
faker_en = Faker('en_US')

# Renewal date (constant)
RENEWAL_DATE = datetime(2569 - 543, 8, 15)  # 15 สิงหาคม 2569 (Buddhist year to CE)

def generate_thai_id():
    """Generate a 13-digit Thai ID with mod 11 checksum"""
    # Generate first 12 digits
    id_digits = [random.randint(0, 9) for _ in range(12)]
    
    # Calculate checksum (mod 11)
    checksum = 0
    for i, digit in enumerate(id_digits):
        checksum += digit * (13 - i)
    
    check_digit = (11 - (checksum % 11)) % 10
    id_digits.append(check_digit)
    
    return ''.join(map(str, id_digits))

def calculate_age(birth_date, reference_date):
    """Calculate age in years and days"""
    age_years = reference_date.year - birth_date.year
    
    # Handle leap year dates (e.g., Feb 29)
    try:
        birthday_this_year = birth_date.replace(year=reference_date.year)
    except ValueError:
        # If birth date is Feb 29 and reference year is not leap year, use Feb 28
        birthday_this_year = birth_date.replace(year=reference_date.year, day=28)
    
    age_days = (reference_date - birthday_this_year).days
    
    if age_days < 0:
        age_years -= 1
        age_days += 365 if not is_leap_year(reference_date.year) else 366
    
    return age_years, age_days

def is_leap_year(year):
    """Check if a year is a leap year"""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def get_advance_days(timeline):
    """Calculate advance renewal days based on timeline"""
    if "90 - 30" in timeline:
        return random.randint(30, 90)
    elif "29 - 1" in timeline:
        return random.randint(1, 29)
    elif "ภายในวันที่หมดอายุ" in timeline:
        return 0
    return 0

def generate_person_name_email():
    """Generate Thai name and English email"""
    first_name_th = faker_th.first_name()
    last_name_th = faker_th.last_name()
    first_name_en = faker_en.first_name()
    
    full_name_th = f"{first_name_th} {last_name_th}"
    email = f"{first_name_en.lower()}@email.com"
    
    return full_name_th, email, first_name_en

def generate_phone():
    """Generate Thai phone number (10 digits: 08 + 8 digits)"""
    return f"08{random.randint(10000000, 99999999)}"

def generate_person_data(birth_date_range_start, birth_date_range_end):
    """Generate person data with birth date within range"""
    days_diff = (birth_date_range_end - birth_date_range_start).days
    random_days = random.randint(0, days_diff)
    birth_date = birth_date_range_start + timedelta(days=random_days)
    
    full_name_th, email, _ = generate_person_name_email()
    thai_id = generate_thai_id()
    phone = generate_phone()
    age_years, age_days = calculate_age(birth_date, RENEWAL_DATE)
    
    # Format date as Thai Buddhist year
    birth_date_buddhist = birth_date.year + 543
    formatted_date = f"{birth_date.day} {get_thai_month(birth_date.month)} {birth_date_buddhist}"
    
    return {
        'name': full_name_th,
        'thai_id': thai_id,
        'phone': phone,
        'email': email,
        'birth_date': formatted_date,
        'age': f"{age_years} ปี {age_days} วัน"
    }

def get_thai_month(month):
    """Convert month number to Thai month name"""
    thai_months = [
        "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน",
        "พฤษภาคม", "มิถุนายน", "กรกฎาคม", "สิงหาคม",
        "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
    ]
    return thai_months[month - 1]

def generate_child_normal():
    """Generate child birth date for normal case (1-13 years old)"""
    # 1 มกราคม 2556 ถึง 31 ธันวาคม 2568
    start_date = datetime(2556 - 543, 1, 1)  # 1 Jan 2013
    end_date = datetime(2568 - 543, 12, 31)  # 31 Dec 2025
    return generate_person_data(start_date, end_date)

def generate_child_overage(advance_days):
    """Generate child birth date for overage case (> 15 years old)"""
    # (15 สิงหาคม 2553 + จำนวนวันที่ต่ออายุล่วงหน้า + 1) ถึง 15 สิงหาคม 2554
    start_date = datetime(2553 - 543, 8, 15) + timedelta(days=advance_days + 1)
    end_date = datetime(2554 - 543, 8, 15)
    
    if start_date > end_date:
        start_date = end_date - timedelta(days=1)
    
    return generate_person_data(start_date, end_date)

def generate_adult_normal():
    """Generate adult birth date for normal case"""
    # สุ่มในช่วง (7300 - 10950) วัน ก่อน renewal date
    start_days_ago = 10950
    end_days_ago = 7300
    
    start_date = RENEWAL_DATE - timedelta(days=start_days_ago)
    end_date = RENEWAL_DATE - timedelta(days=end_days_ago)
    
    return generate_person_data(start_date, end_date)

def generate_adult_overage(advance_days):
    """Generate adult birth date for overage case (> 65 years old)"""
    # (15 สิงหาคม 2503 + จำนวนวันที่ต่ออายุล่วงหน้า + 1) ถึง 15 สิงหาคม 2504
    start_date = datetime(2503 - 543, 8, 15) + timedelta(days=advance_days + 1)
    end_date = datetime(2504 - 543, 8, 15)
    
    if start_date > end_date:
        start_date = end_date - timedelta(days=1)
    
    return generate_person_data(start_date, end_date)

def extract_member_info(family_desc, advance_days):
    """Extract and generate member information based on family description"""
    members = {}
    
    # Generate policy holder
    if "อายุเกิน" in family_desc:
        members['holder'] = generate_adult_overage(advance_days)
    else:
        members['holder'] = generate_adult_normal()
    
    # Generate spouse if mentioned
    if "คู่สมรส" in family_desc:
        if "อายุเกิน" in family_desc and "คู่สมรส" in family_desc:
            members['spouse'] = generate_adult_overage(advance_days)
        else:
            members['spouse'] = generate_adult_normal()
        
        # Check for death status
        if "เสียชีวิต" in family_desc:
            members['spouse_status'] = "เสียชีวิต"
        else:
            members['spouse_status'] = "มีชีวิต"
    
    # Generate child 1 if mentioned
    if "ลูก 1" in family_desc or "ลูก 2" in family_desc or "บุตรและคู่สมรส" in family_desc or "บุตร" in family_desc:
        if "อายุเกิน" in family_desc:
            members['child1'] = generate_child_overage(advance_days)
        else:
            members['child1'] = generate_child_normal()
        
        # Check for death status
        if "เสียชีวิต" in family_desc:
            members['child1_status'] = "เสียชีวิต"
        else:
            members['child1_status'] = "มีชีวิต"
    
    # Generate child 2 if mentioned
    if "ลูก 2" in family_desc:
        if "อายุเกิน" in family_desc:
            members['child2'] = generate_child_overage(advance_days)
        else:
            members['child2'] = generate_child_normal()
        
        # Check for death status
        if "เสียชีวิต" in family_desc:
            members['child2_status'] = "เสียชีวิต"
        else:
            members['child2_status'] = "มีชีวิต"
    
    return members

def format_date_buddhist(date_obj):
    """Format date in Thai Buddhist year"""
    buddhist_year = date_obj.year + 543
    return f"{date_obj.day} {get_thai_month(date_obj.month)} {buddhist_year}"

def process_row(timeline, bundle, family):
    """Process one row from input CSV"""
    advance_days = get_advance_days(timeline)
    
    # Calculate coverage dates
    coverage_end = RENEWAL_DATE + timedelta(days=advance_days)
    coverage_start = coverage_end - timedelta(days=365)
    
    renewal_date_formatted = format_date_buddhist(RENEWAL_DATE)
    coverage_end_formatted = format_date_buddhist(coverage_end)
    coverage_start_formatted = format_date_buddhist(coverage_start)
    
    # Extract member information
    members = extract_member_info(family, advance_days)
    
    # Build output row
    output_row = {
        'Timeline': timeline,
        'Bundle': bundle,
        'Family': family,
        'ชื่อผู้ถือกรมธรรม์': members['holder']['name'],
        'เลขบัตรผู้ถือ': members['holder']['thai_id'],
        'เบอร์โทรผู้ถือ': members['holder']['phone'],
        'อีเมลผู้ถือ': members['holder']['email'],
        'วันเกิดผู้ถือ': members['holder']['birth_date'],
        'อายุผู้ถือ': members['holder']['age'],
    }
    
    # Add spouse info if exists
    if 'spouse' in members:
        output_row['ชื่อคู่สมรส'] = members['spouse']['name']
        output_row['เลขบัตรคู่สมรส'] = members['spouse']['thai_id']
        output_row['วันเกิดคู่สมรส'] = members['spouse']['birth_date']
        output_row['อายุคู่สมรส'] = members['spouse']['age']
        output_row['สถานะคู่สมรส'] = members['spouse_status']
    else:
        output_row['ชื่อคู่สมรส'] = ''
        output_row['เลขบัตรคู่สมรส'] = ''
        output_row['วันเกิดคู่สมรส'] = ''
        output_row['อายุคู่สมรส'] = ''
        output_row['สถานะคู่สมรส'] = ''
    
    # Add child 1 info if exists
    if 'child1' in members:
        output_row['ชื่อบุตรคนที่ 1'] = members['child1']['name']
        output_row['เลขบัตรบุตรคนที่ 1'] = members['child1']['thai_id']
        output_row['วันเกิดบุตรคนที่ 1'] = members['child1']['birth_date']
        output_row['อายุบุตรคนที่ 1'] = members['child1']['age']
        output_row['สถานะบุตรคนที่ 1'] = members['child1_status']
    else:
        output_row['ชื่อบุตรคนที่ 1'] = ''
        output_row['เลขบัตรบุตรคนที่ 1'] = ''
        output_row['วันเกิดบุตรคนที่ 1'] = ''
        output_row['อายุบุตรคนที่ 1'] = ''
        output_row['สถานะบุตรคนที่ 1'] = ''
    
    # Add child 2 info if exists
    if 'child2' in members:
        output_row['ชื่อบุตรคนที่ 2'] = members['child2']['name']
        output_row['เลขบัตรบุตรคนที่ 2'] = members['child2']['thai_id']
        output_row['วันเกิดบุตรคนที่ 2'] = members['child2']['birth_date']
        output_row['อายุบุตรคนที่ 2'] = members['child2']['age']
        output_row['สถานะบุตรคนที่ 2'] = members['child2_status']
    else:
        output_row['ชื่อบุตรคนที่ 2'] = ''
        output_row['เลขบัตรบุตรคนที่ 2'] = ''
        output_row['วันเกิดบุตรคนที่ 2'] = ''
        output_row['อายุบุตรคนที่ 2'] = ''
        output_row['สถานะบุตรคนที่ 2'] = ''
    
    # Add status information
    output_row['จำนวนวันที่ต่ออายุล่วงหน้า'] = f"{advance_days} วัน"
    output_row['วันที่ต่ออายุ'] = renewal_date_formatted
    output_row['วันสิ้นสุดความคุ้มครอง'] = coverage_end_formatted
    output_row['วันเริ่มสัญญาฉบับปัจจุบัน'] = coverage_start_formatted
    
    return output_row

def main():
    # Read input CSV
    input_file = "SCK insurance - Sheet1.csv"
    df_input = pd.read_csv(input_file)
    
    # Process each row
    output_rows = []
    for idx, row in df_input.iterrows():
        timeline = row['Timeline']
        bundle = row['Bundle']
        family = row['Family']
        
        # Skip empty rows
        if pd.isna(timeline) or pd.isna(bundle) or pd.isna(family):
            continue
        
        output_row = process_row(timeline, bundle, family)
        output_rows.append(output_row)
    
    # Create output DataFrame
    df_output = pd.DataFrame(output_rows)
    
    # Save to CSV
    output_file = "SCK_insurance_output_v3.csv"
    df_output.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"✓ Generated {len(output_rows)} rows")
    print(f"✓ Output saved to: {output_file}")

if __name__ == "__main__":
    main()
