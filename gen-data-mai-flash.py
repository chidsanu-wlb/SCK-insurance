#!/usr/bin/env python3
import random
from datetime import datetime, timedelta
from faker import Faker
import pandas as pd
from typing import Tuple

# Deterministic seed (chosen per user's preference)
SEED = 42
random.seed(SEED)

faker_th = Faker("th_TH")
faker_en = Faker("en_US")
FAKER_SEED = SEED
faker_th.seed_instance(FAKER_SEED)
faker_en.seed_instance(FAKER_SEED)

# Constants
INPUT_CSV = "SCK insurance - Sheet1.csv"
OUTPUT_CSV = "SCK_insurance_output.csv"
RENEWAL_DATE = datetime(2026, 8, 15)
MONTHS_TH = [
    "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"
]

# -------------------------
# Utilities
# -------------------------
def generate_thai_id() -> str:
    digits = [random.randint(0, 9) for _ in range(12)]
    s = sum((13 - i) * digits[i] for i in range(12))
    check = (11 - (s % 11)) % 10
    digits.append(check)
    return "".join(str(d) for d in digits)

def buddhist_date(dt: datetime) -> str:
    return f"{dt.day} {MONTHS_TH[dt.month-1]} {dt.year + 543}"

def calculate_age(birthdate: datetime, as_of: datetime = RENEWAL_DATE) -> Tuple[int, int]:
    delta_days = (as_of - birthdate).days
    years = delta_days // 365
    days = delta_days % 365
    return years, days

def age_str(birthdate: datetime) -> str:
    y, d = calculate_age(birthdate)
    return f"{y} ปี {d} วัน"

def random_phone() -> str:
    return "08" + "".join(str(random.randint(0, 9)) for _ in range(8))

def get_days_before(timeline: str) -> int:
    if "90 - 30" in timeline:
        return random.randint(30, 90)
    if "29 - 1" in timeline:
        return random.randint(1, 29)
    return 0

# -------------------------
# Birthdate samplers (resample to satisfy constraints)
# -------------------------
def sample_adult_normal() -> datetime:
    # between (renewal - 10950 days) and (renewal - 7300 days)
    start = RENEWAL_DATE - timedelta(days=10950)
    end = RENEWAL_DATE - timedelta(days=7300)
    return random_date_between(start, end)

def sample_adult_overage(days_before: int) -> datetime:
    # between (15 Aug 2503 + days_before + 1) and 15 Aug 2504 (BE -> CE)
    # 2503 BE = 1960 CE, 2504 BE = 1961 CE
    start = datetime(1960, 8, 15) + timedelta(days=days_before + 1)
    end = datetime(1961, 8, 15)
    return random_date_between(start, end)

def sample_child_normal() -> datetime:
    # between 1 Jan 2556 (2013) and 31 Dec 2568 (2025)
    start = datetime(2013, 1, 1)
    end = datetime(2025, 12, 31)
    return random_date_between(start, end)

def sample_child_overage(days_before: int) -> datetime:
    # between (15 Aug 2553 + days_before +1) and 15 Aug 2554
    # 2553 BE = 2010 CE, 2554 BE = 2011 CE
    start = datetime(2010, 8, 15) + timedelta(days=days_before + 1)
    end = datetime(2011, 8, 15)
    return random_date_between(start, end)

def random_date_between(start: datetime, end: datetime) -> datetime:
    if start > end:
        start, end = end, start
    span = (end - start).days
    if span <= 0:
        return start
    return start + timedelta(days=random.randint(0, span))

# -------------------------
# Generators (with validation/resample)
# -------------------------
def generate_holder(days_before: int) -> str:
    # adult normal: age approx 20-30 => sample_adult_normal
    # ensure age <= 65 (spec requires adults not over 65 unless overage case)
    for _ in range(50):
        birth = sample_adult_normal()
        years, _ = calculate_age(birth)
        if years <= 65:
            break
    first_th = faker_th.first_name()
    last_th = faker_th.last_name()
    first_en = faker_en.first_name().lower()
    return (
        f"ชื่อ: {first_th} {last_th}\n"
        f"เลขบัตรประชาชน: {generate_thai_id()}\n"
        f"เบอร์โทรศัพท์: {random_phone()}\n"
        f"อีเมล: {first_en}@email.com\n"
        f"ว/ด/ป เกิด: {buddhist_date(birth)}\n"
        f"อายุ: {age_str(birth)}"
    )

def generate_spouse(days_before: int, overage: bool = False, deceased: bool = False) -> str:
    if overage:
        birth = sample_adult_overage(days_before)
    else:
        # normal adult
        for _ in range(50):
            birth = sample_adult_normal()
            years, _ = calculate_age(birth)
            if years <= 65:
                break
    status = "เสียชีวิต" if deceased else "มีชีวิต"
    first_th = faker_th.first_name()
    last_th = faker_th.last_name()
    return (
        f"คู่สมรส: {status}\n"
        f"ชื่อ: {first_th} {last_th}\n"
        f"ว/ด/ป เกิด: {buddhist_date(birth)}\n"
        f"อายุ: {age_str(birth)}"
    )

def generate_child(days_before: int, index: int = 1, overage: bool = False, deceased: bool = False) -> str:
    if overage:
        birth = sample_child_overage(days_before)
    else:
        # normal child range
        for _ in range(50):
            birth = sample_child_normal()
            years, _ = calculate_age(birth)
            if 0 < years <= 15:
                break
    status = "เสียชีวิต" if deceased else "มีชีวิต"
    first_th = faker_th.first_name()
    last_th = faker_th.last_name()
    return (
        f"บุตรคนที่ {index}: {status}\n"
        f"ชื่อ: {first_th} {last_th}\n"
        f"ว/ด/ป เกิด: {buddhist_date(birth)}\n"
        f"อายุ: {age_str(birth)}"
    )

# -------------------------
# Family case parser and assembly
# -------------------------
def build_members_cell(family_case: str, days_before: int, bundle: str) -> str:
    # For SCK Personal, return empty
    if bundle and "Personal" in bundle and "Family" not in bundle:
        return ""

    parts = []
    fc = (family_case or "").strip()

    # Determine spouse flags
    spouse_present = "คู่สมรส" in fc
    spouse_overage = "คู่สมรสอายุเกิน" in fc or "คู่สมรส: อายุเกิน" in fc
    spouse_deceased = "คู่สมรสเสียชีวิต" in fc or "คู่สมรส: เสียชีวิต" in fc or "คู่สมรส: เสียชีวิต" in fc or "คู่สมรสเสียชีวิต" in fc

    # Children detection
    # Cases use strings like "ลูก 1", "ลูก 2", "บุตรเสียชีวิต", "บุตรอายุเกิน"
    child1_present = ("ลูก 1" in fc) or ("บุตร 1" in fc) or ("บุตรคนที่ 1" in fc)
    child2_present = ("ลูก 2" in fc) or ("บุตร 2" in fc) or ("บุตรคนที่ 2" in fc)
    # some cases describe children plural; detect "บุตร" presence when ambiguous
    any_child = "ลูก" in fc or "บุตร" in fc

    # Child states
    child_overage = "บุตรอายุเกิน" in fc or "บุตร 1 คนอายุเกิน" in fc or "บุตร 1 คน อายุเกิน" in fc or "บุตร 2 คนอายุเกิน" in fc
    child_deceased = "บุตรเสียชีวิต" in fc or "บุตร: เสียชีวิต" in fc

    # Build order: spouse -> child1 -> child2
    if spouse_present:
        parts.append(generate_spouse(days_before, overage=spouse_overage, deceased=spouse_deceased))

    # Child 1 handling: If explicit 'ลูก 1' or 'ลูก' with counts implied
    if child1_present:
        parts.append(generate_child(days_before, index=1, overage=child_overage, deceased=child_deceased))
    elif any_child and not spouse_present:
        # case with only children but not labeled as child1/child2: assume 1 child
        parts.append(generate_child(days_before, index=1, overage=child_overage, deceased=child_deceased))

    if child2_present:
        parts.append(generate_child(days_before, index=2, overage=child_overage, deceased=child_deceased))

    # Join with a blank line between persons
    return "\n\n".join(parts)

# -------------------------
# Main CSV pipeline
# -------------------------
def main():
    df = pd.read_csv(INPUT_CSV, encoding="utf-8-sig")
    rows = []
    for _, r in df.iterrows():
        timeline = str(r.get("Timeline", "") or "")
        bundle = str(r.get("Bundle", "") or "")
        family_case = str(r.get("Family", "") or "")
        days_before = get_days_before(timeline)
        # Holder
        holder = generate_holder(days_before)
        # Members
        members = build_members_cell(family_case, days_before, bundle)
        # Status dates
        end_date = RENEWAL_DATE + timedelta(days=days_before)
        start_date = end_date - timedelta(days=365)
        status = (
            f"จำนวนวันที่ต่ออายุล่วงหน้า: {days_before} วัน\n"
            f"วันที่ต่ออายุ: {buddhist_date(RENEWAL_DATE)}\n"
            f"วันสิ้นสุดความคุ้มครอง: {buddhist_date(end_date)}\n"
            f"วันเริ่มสัญญาฉบับปัจจุบัน: {buddhist_date(start_date)}"
        )
        rows.append({
            "Timeline": timeline,
            "Bundle": bundle,
            "Family": family_case,
            "ข้อมูลผู้ถือกรมธรรม์": holder,
            "ข้อมูลสมาชิกในกรมธรรม์": members,
            "Status": status
        })

    out_df = pd.DataFrame(rows, columns=[
        "Timeline", "Bundle", "Family",
        "ข้อมูลผู้ถือกรมธรรม์", "ข้อมูลสมาชิกในกรมธรรม์", "Status"
    ])
    out_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"Wrote {OUTPUT_CSV}")

if __name__ == "__main__":
    main()