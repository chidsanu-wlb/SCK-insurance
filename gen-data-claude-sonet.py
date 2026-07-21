"""
SCK Insurance Test Data Generator
==================================
Generates mock renewal-processing data for SCK Personal / SCK Personal + SCK Family
insurance products, based on the business rules described in the project spec.

Usage:
    python generate_sck_data.py input.csv output.csv

Requires:
    pip install faker
"""

import random
import sys
from datetime import date, timedelta

import pandas as pd
from faker import Faker

# ---------------------------------------------------------------------------
# Faker setup
# ---------------------------------------------------------------------------
faker_th = Faker("th_TH")
faker_en = Faker("en_US")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
RENEWAL_DATE = date(2026, 8, 15)  # 15 สิงหาคม 2569 (2569 - 543 = 2026)
BUDDHIST_YEAR_OFFSET = 543

THAI_MONTHS = [
    "", "มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
    "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม",
]

# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------

def thai_date_str(d: date) -> str:
    """Format a Gregorian date as 'วัน เดือน(ไทย) ปี(พ.ศ.)'."""
    return f"{d.day} {THAI_MONTHS[d.month]} {d.year + BUDDHIST_YEAR_OFFSET}"


def random_date(start: date, end: date) -> date:
    """Random date within [start, end] inclusive. Swaps if start > end."""
    if start > end:
        start, end = end, start
    delta_days = (end - start).days
    if delta_days <= 0:
        return start
    return start + timedelta(days=random.randint(0, delta_days))


def age_years_days(birth_date: date, ref_date: date) -> tuple[int, int]:
    """Return (years, days) age of birth_date as of ref_date."""
    years = ref_date.year - birth_date.year
    try:
        anniversary = birth_date.replace(year=birth_date.year + years)
    except ValueError:
        # handles Feb 29 birthdays
        anniversary = birth_date.replace(year=birth_date.year + years, day=28)
    if anniversary > ref_date:
        years -= 1
        try:
            anniversary = birth_date.replace(year=birth_date.year + years)
        except ValueError:
            anniversary = birth_date.replace(year=birth_date.year + years, day=28)
    days = (ref_date - anniversary).days
    return years, days


def generate_thai_id() -> str:
    """Generate a 13-digit Thai national ID with a valid mod-11 checksum."""
    digits = [random.randint(0, 9) for _ in range(12)]
    # first digit should not be 0 for realism
    if digits[0] == 0:
        digits[0] = random.randint(1, 9)
    total = sum(d * (13 - i) for i, d in enumerate(digits))
    check_digit = (11 - (total % 11)) % 10
    digits.append(check_digit)
    return "".join(str(d) for d in digits)


def generate_phone() -> str:
    return "08" + "".join(str(random.randint(0, 9)) for _ in range(8))


# ---------------------------------------------------------------------------
# Timeline -> days-in-advance
# ---------------------------------------------------------------------------

def days_in_advance(timeline: str) -> int:
    timeline = (timeline or "").strip()
    if timeline.startswith("90"):
        return random.randint(30, 90)
    if timeline.startswith("29"):
        return random.randint(1, 29)
    if "หมดอายุ" in timeline:
        return 0
    # fallback
    return 0


# ---------------------------------------------------------------------------
# Age-constrained birth-date generators
# ---------------------------------------------------------------------------
#
# The date ranges below are taken directly from the spec's own formulas
# (section "กฎเกณฑ์เรื่องอายุ"). The spec supplies these ranges as
# ready-to-use random windows ("การสุ่มวันเกิด: ต้องอยู่ในช่วงที่กำหนด
# เท่านั้น" — the sampled date must stay inside the given range, full stop).
# So we sample a single uniform date directly from [start, end] with no
# retrying and no adjusting the date afterwards — any post-hoc "correction"
# risks pushing the date outside the very range the spec hands us, and (as
# tested) can also collapse many rows onto one repeated, non-random date
# when the requested inequality is not achievable for every point in the
# range. Trusting the given range keeps every date in-bounds and properly
# randomized, matching the spec's own constraint above everything else.

def _sample_birthdate_in_range(start: date, end: date) -> date:
    return random_date(start, end)


def child_birthdate(exceeded: bool, days_advance: int) -> date:
    """
    Normal case:   1 Jan 2013 - 31 Dec 2025                        -> age 1-13 yrs
    Exceeded case: (15 Aug 2010 + days_advance + 1) - 15 Aug 2011  -> age > 15 yrs
    """
    if not exceeded:
        start = date(2013, 1, 1)
        end = date(2025, 12, 31)
    else:
        start = date(2010, 8, 15) + timedelta(days=days_advance + 1)
        end = date(2011, 8, 15)
    return _sample_birthdate_in_range(start, end)


def adult_birthdate(exceeded: bool, days_advance: int) -> date:
    """
    Normal case:   (renewal - 10950d) - (renewal - 7300d)         -> age ~20-30 yrs
    Exceeded case: (15 Aug 2503 BE=1960 + days_advance + 1) - 15 Aug 2504 BE=1961 -> age > 65 yrs
    """
    if not exceeded:
        start = RENEWAL_DATE - timedelta(days=10950)
        end = RENEWAL_DATE - timedelta(days=7300)
    else:
        start = date(1960, 8, 15) + timedelta(days=days_advance + 1)
        end = date(1961, 8, 15)
    return _sample_birthdate_in_range(start, end)


# ---------------------------------------------------------------------------
# Person builders
# ---------------------------------------------------------------------------

def make_person(is_child: bool, exceeded: bool, days_advance: int):
    if is_child:
        bd = child_birthdate(exceeded, days_advance)
    else:
        bd = adult_birthdate(exceeded, days_advance)
    first = faker_th.first_name()
    last = faker_th.last_name()
    years, days = age_years_days(bd, RENEWAL_DATE)
    return {
        "first_name": first,
        "last_name": last,
        "birth_date": bd,
        "age_years": years,
        "age_days": days,
    }


def format_policyholder(person: dict) -> str:
    first_en = faker_en.first_name()
    lines = [
        f"ชื่อ: {person['first_name']} {person['last_name']}",
        f"เลขบัตรประชาชน: {generate_thai_id()}",
        f"เบอร์โทรศัพท์: {generate_phone()}",
        f"อีเมล: {first_en.lower()}@email.com",
        f"ว/ด/ป เกิด: {thai_date_str(person['birth_date'])}",
        f"อายุ: {person['age_years']} ปี {person['age_days']} วัน",
    ]
    return "\n".join(lines)


def format_member_block(label: str, status: str, person: dict) -> str:
    lines = [
        f"{label}: {status}",
        f"ชื่อ: {person['first_name']} {person['last_name']}",
        f"ว/ด/ป เกิด: {thai_date_str(person['birth_date'])}",
        f"อายุ: {person['age_years']} ปี {person['age_days']} วัน",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Family-case definitions
# ---------------------------------------------------------------------------
# Each case defines the member list to build, in output order:
# spouse (optional), child 1 (optional), child 2 (optional).
# tuple = (has_spouse, spouse_status, spouse_exceeded,
#          num_children, child_status, child_exceeded_flags)

FAMILY_CASES = {
    "กรณีปกติ 1. คนซื้อ + คู่สมรส": dict(
        spouse=("มีชีวิต", False), children=[]),
    "กรณีปกติ 2. คนซื้อ + คู่สมรส + ลูก 1": dict(
        spouse=("มีชีวิต", False), children=[("มีชีวิต", False)]),
    "กรณีปกติ 3. คนซื้อ + คู่สมรส + ลูก 2": dict(
        spouse=("มีชีวิต", False), children=[("มีชีวิต", False), ("มีชีวิต", False)]),
    "กรณีปกติ 4. คนซื้อ + ลูก 1": dict(
        spouse=None, children=[("มีชีวิต", False)]),
    "กรณีปกติ 5. คนซื้อ + ลูก 2": dict(
        spouse=None, children=[("มีชีวิต", False), ("มีชีวิต", False)]),
    "กรณีบุตรและคู่สมรสอายุเกิน": dict(
        spouse=("มีชีวิต", True), children=[("มีชีวิต", True)]),
    "กรณีบุตรและคู่สมรสเสียชีวิต": dict(
        spouse=("เสียชีวิต", False), children=[("เสียชีวิต", False)]),
    "กรณีบุตร 1 คนอายุเกินและคู่สมรสอายุเกิน": dict(
        spouse=("มีชีวิต", True), children=[("มีชีวิต", True)]),
    "กรณีคู่สมรสอายุเกิน": dict(
        spouse=("มีชีวิต", True), children=[]),
    "กรณีบุตร 1 คน อายุเกิน": dict(
        spouse=None, children=[("มีชีวิต", True)]),
    "กรณีบุตร 2 คน อายุเกิน": dict(
        spouse=None, children=[("มีชีวิต", True), ("มีชีวิต", True)]),
    "กรณีคู่สมรสเสียชีวิต และบุตรอายุเกิน 1 คน": dict(
        spouse=("เสียชีวิต", False), children=[("มีชีวิต", True)]),
    "กรณีคู่สมรสเสียชีวิต และบุตรอายุเกิน 2 คน": dict(
        spouse=("เสียชีวิต", False), children=[("มีชีวิต", True), ("มีชีวิต", True)]),
    "กรณีคู่สมรสเสียชีวิต": dict(
        spouse=("เสียชีวิต", False), children=[]),
    "กรณีบุตรเสียชีวิต": dict(
        spouse=None, children=[("เสียชีวิต", False)]),
}


def build_members_text(family_case: str, days_advance: int) -> str:
    """Build column 5 text for a given family-case label. Returns '' if no case."""
    case = FAMILY_CASES.get(family_case.strip()) if isinstance(family_case, str) else None
    if case is None:
        return ""

    blocks = []

    if case["spouse"] is not None:
        status, exceeded = case["spouse"]
        # a deceased spouse's age isn't really constrained by the "exceeded"
        # rule, but we still generate a plausible adult birth date
        spouse_person = make_person(is_child=False, exceeded=exceeded, days_advance=days_advance)
        blocks.append(format_member_block("คู่สมรส", status, spouse_person))

    for idx, (status, exceeded) in enumerate(case["children"], start=1):
        child_person = make_person(is_child=True, exceeded=exceeded, days_advance=days_advance)
        blocks.append(format_member_block(f"บุตรคนที่ {idx}", status, child_person))

    return "\n\n".join(blocks)


# ---------------------------------------------------------------------------
# Row processing
# ---------------------------------------------------------------------------

def process_row(row: pd.Series) -> pd.Series:
    timeline = row["Timeline"]
    bundle = row["Bundle"]
    family = row["Family"]

    adv_days = days_in_advance(timeline)

    coverage_end = RENEWAL_DATE + timedelta(days=adv_days)
    contract_start = coverage_end - timedelta(days=365)

    policyholder = make_person(is_child=False, exceeded=False, days_advance=adv_days)
    policyholder_text = format_policyholder(policyholder)

    is_family_bundle = isinstance(bundle, str) and "Family" in bundle
    if is_family_bundle and isinstance(family, str) and family.strip():
        members_text = build_members_text(family, adv_days)
    else:
        members_text = ""

    status_text = "\n".join([
        f"จำนวนวันที่ต่ออายุล่วงหน้า: {adv_days} วัน",
        f"วันที่ต่ออายุ: {thai_date_str(RENEWAL_DATE)}",
        f"วันสิ้นสุดความคุ้มครอง: {thai_date_str(coverage_end)}",
        f"วันเริ่มสัญญาฉบับปัจจุบัน: {thai_date_str(contract_start)}",
    ])

    return pd.Series({
        "Timeline": timeline,
        "Bundle": bundle,
        "Family": family,
        "ข้อมูลผู้ถือกรมธรรม์": policyholder_text,
        "ข้อมูลสมาชิกในกรมธรรม์": members_text,
        "Status": status_text,
    })


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    in_path = sys.argv[1] if len(sys.argv) > 1 else "SCK insurance - Sheet1.csv"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "SCK_insurance_output.csv"

    df = pd.read_csv(in_path, encoding="utf-8-sig")

    out_rows = [process_row(row) for _, row in df.iterrows()]
    out_df = pd.DataFrame(out_rows)

    out_df.to_csv(out_path, index=False, encoding="utf-8-sig", lineterminator="\n")
    print(f"Wrote {len(out_df)} rows to {out_path}")


if __name__ == "__main__":
    main()