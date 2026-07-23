# ============================================================
# Part 1 : Imports, Constants, Utilities
# spec_v5.md
# ============================================================

import random
from datetime import date, timedelta

import pandas as pd
from faker import Faker

# ------------------------------------------------------------
# Faker
# ------------------------------------------------------------
fake_th = Faker("th_TH")
fake_en = Faker("en_US")

random.seed()

# ------------------------------------------------------------
# Constants
# ------------------------------------------------------------

RENEWAL_DATE = date(2026, 8, 15)

THAI_MONTHS = {
    1: "มกราคม",
    2: "กุมภาพันธ์",
    3: "มีนาคม",
    4: "เมษายน",
    5: "พฤษภาคม",
    6: "มิถุนายน",
    7: "กรกฎาคม",
    8: "สิงหาคม",
    9: "กันยายน",
    10: "ตุลาคม",
    11: "พฤศจิกายน",
    12: "ธันวาคม",
}

# ------------------------------------------------------------
# Timeline
# ------------------------------------------------------------

def get_advance_days(timeline: str) -> int:
    """
    Convert Timeline text to advance days.
    """

    if pd.isna(timeline):
        return 0

    timeline = str(timeline).strip()

    if timeline == "90 - 30 วันล่วงหน้า":
        return random.randint(30, 90)

    elif timeline == "29 - 1 วันล่วงหน้า":
        return random.randint(1, 29)

    elif timeline == "ภายในวันที่หมดอายุ":
        return 0

    return 0


# ------------------------------------------------------------
# Contract Dates
# ------------------------------------------------------------

def get_contract_dates(advance_days: int):

    end_date = RENEWAL_DATE + timedelta(days=advance_days)

    start_date = end_date - timedelta(days=365)

    return start_date, end_date


# ------------------------------------------------------------
# Thai Date Format
# ------------------------------------------------------------

def thai_date(dt: date) -> str:
    """
    Example:
    15 สิงหาคม 2569
    """

    return f"{dt.day} {THAI_MONTHS[dt.month]} {dt.year + 543}"


# ------------------------------------------------------------
# Age
# ------------------------------------------------------------

def calculate_age(birthday: date, reference: date):
    """
    Return (years, days)
    """

    years = reference.year - birthday.year

    if (reference.month, reference.day) < (birthday.month, birthday.day):
        years -= 1

    last_birthday = birthday.replace(year=birthday.year + years)

    days = (reference - last_birthday).days

    return years, days


# ------------------------------------------------------------
# Random Birthday
# ------------------------------------------------------------

def random_birthday(min_age: int, max_age: int):

    age = random.randint(min_age, max_age)

    birthday = (
        RENEWAL_DATE
        - timedelta(days=age * 365 + random.randint(0, 364))
    )

    return birthday


# ------------------------------------------------------------
# Over Age Birthday
# ------------------------------------------------------------

def over_age_birthday(limit_age: int, advance_days: int):
    """
    Generate birthday for over-age member.

    Range:
        limit_age + advance_days + 1 day
        until
        limit_age + 1 year
    """

    min_days = limit_age * 365 + advance_days + 1

    max_days = (limit_age + 1) * 365

    offset = random.randint(min_days, max_days)

    return RENEWAL_DATE - timedelta(days=offset)


# ------------------------------------------------------------
# Thai Phone
# ------------------------------------------------------------

def generate_phone():

    return "08" + "".join(random.choices("0123456789", k=8))


# ------------------------------------------------------------
# Thai National ID (Modulo 11)
# ------------------------------------------------------------

def generate_thai_id():

    digits = [random.randint(1, 9)]

    for _ in range(11):
        digits.append(random.randint(0, 9))

    total = 0

    for i in range(12):
        total += digits[i] * (13 - i)

    check = (11 - (total % 11)) % 10

    digits.append(check)

    return "".join(map(str, digits))


# ------------------------------------------------------------
# English Email
# ------------------------------------------------------------

def generate_email(first_name_en):

    first = first_name_en.lower().replace(" ", "")

    return f"{first}@email.com"


# ------------------------------------------------------------
# Name Generator
# ------------------------------------------------------------

def generate_name():

    th_name = fake_th.name().split()

    if len(th_name) >= 2:
        first_th = th_name[0]
        last_th = th_name[-1]
    else:
        first_th = fake_th.first_name()
        last_th = fake_th.last_name()

    first_en = fake_en.first_name()

    return {
        "first_th": first_th,
        "last_th": last_th,
        "first_en": first_en,
    }

# ============================================================
# Part 2 : Person & Member Generator
# spec_v5.md
# Requires Part 1
# ============================================================

# ------------------------------------------------------------
# Create Person
# ------------------------------------------------------------

def create_person(role: str, mode: str, advance_days: int):
    """
    role
        policyholder
        spouse
        child

    mode
        normal
        over_age
        dead
    """

    name = generate_name()

    # ----------------------------
    # Birthday
    # ----------------------------
    if role in ("policyholder", "spouse"):

        if mode == "normal":
            birthday = random_birthday(20, 30)

        else:
            birthday = over_age_birthday(65, advance_days)

    else:

        if mode == "normal":
            birthday = random_birthday(1, 13)

        else:
            birthday = over_age_birthday(15, advance_days)

    years, days = calculate_age(
        birthday,
        RENEWAL_DATE
    )

    person = {
        "role": role,
        "status": "เสียชีวิต" if mode == "dead" else "มีชีวิต",

        "first_th": name["first_th"],
        "last_th": name["last_th"],
        "first_en": name["first_en"],

        "birthday": birthday,
        "age_years": years,
        "age_days": days,

        "thai_id": generate_thai_id(),
        "phone": generate_phone(),
        "email": generate_email(name["first_en"]),
    }

    return person


# ------------------------------------------------------------
# Policyholder
# ------------------------------------------------------------

def create_policyholder(advance_days: int):

    return create_person(
        role="policyholder",
        mode="normal",
        advance_days=advance_days
    )


# ------------------------------------------------------------
# Spouse
# ------------------------------------------------------------

def create_spouse(status: str, advance_days: int):
    """
    status
        normal
        over_age
        dead
    """

    return create_person(
        role="spouse",
        mode=status,
        advance_days=advance_days
    )


# ------------------------------------------------------------
# Child
# ------------------------------------------------------------

def create_child(status: str, advance_days: int):

    return create_person(
        role="child",
        mode=status,
        advance_days=advance_days
    )


# ------------------------------------------------------------
# Policyholder Text (Column 4)
# ------------------------------------------------------------

def format_policyholder(person):

    return (
        f"ชื่อ: {person['first_th']} {person['last_th']}\n"
        f"เลขบัตรประชาชน: {person['thai_id']}\n"
        f"เบอร์โทรศัพท์: {person['phone']}\n"
        f"อีเมล: {person['email']}\n"
        f"ว/ด/ป เกิด: {thai_date(person['birthday'])}\n"
        f"อายุ: {person['age_years']} ปี {person['age_days']} วัน"
    )


# ------------------------------------------------------------
# Member Text
# ------------------------------------------------------------

def format_member(person, title):

    return (
        f"{title}: {person['status']}\n"
        f"ชื่อ: {person['first_th']} {person['last_th']}\n"
        f"ว/ด/ป เกิด: {thai_date(person['birthday'])}\n"
        f"อายุ: {person['age_years']} ปี {person['age_days']} วัน"
    )


# ------------------------------------------------------------
# Column 5 Builder
# ------------------------------------------------------------

def build_member_text(spouse=None, child1=None, child2=None):

    members = []

    if spouse is not None:
        members.append(
            format_member(
                spouse,
                "คู่สมรส"
            )
        )

    if child1 is not None:
        members.append(
            format_member(
                child1,
                "บุตรคนที่ 1"
            )
        )

    if child2 is not None:
        members.append(
            format_member(
                child2,
                "บุตรคนที่ 2"
            )
        )

    return "\n\n".join(members)

# ============================================================
# Part 3 : Family Mapping Engine
# spec_v5.md
# Requires Part 1 & Part 2
# ============================================================

# ------------------------------------------------------------
# Family Mapping
# ------------------------------------------------------------

# status
#   normal
#   over_age
#   dead
#   None = ไม่มีสมาชิก

FAMILY_MAPPING = {

    # =========================================================
    # คู่สมรสปกติ
    # =========================================================
    "คู่สมรสปกติ ไม่มีบุตร": {
        "spouse": "normal",
        "child1": None,
        "child2": None,
    },

    "คู่สมรสปกติ บุตร 1 คน": {
        "spouse": "normal",
        "child1": "normal",
        "child2": None,
    },

    "คู่สมรสปกติ บุตร 2 คน": {
        "spouse": "normal",
        "child1": "normal",
        "child2": "normal",
    },

    # =========================================================
    # ไม่มีคู่สมรส
    # =========================================================
    "ไม่มีคู่สมรส บุตร 1 คน": {
        "spouse": None,
        "child1": "normal",
        "child2": None,
    },

    "ไม่มีคู่สมรส บุตร 2 คน": {
        "spouse": None,
        "child1": "normal",
        "child2": "normal",
    },

    "ไม่มีคู่สมรส บุตร 1 คนอายุเกิน": {
        "spouse": None,
        "child1": "over_age",
        "child2": None,
    },

    "ไม่มีคู่สมรส บุตร 2 คนอายุเกิน": {
        "spouse": None,
        "child1": "over_age",
        "child2": "over_age",
    },

    "ไม่มีคู่สมรส บุตรเสียชีวิต 1 คน": {
        "spouse": None,
        "child1": "dead",
        "child2": None,
    },

    "ไม่มีคู่สมรส บุตรเสียชีวิต 2 คน": {
        "spouse": None,
        "child1": "dead",
        "child2": "dead",
    },

    # =========================================================
    # คู่สมรสอายุเกิน
    # =========================================================
    "คู่สมรสอายุเกิน บุตร 2 คน": {
        "spouse": "over_age",
        "child1": "normal",
        "child2": "normal",
    },

    "คู่สมรสอายุเกิน บุตร 1 คนอายุเกิน": {
        "spouse": "over_age",
        "child1": "over_age",
        "child2": None,
    },

    "คู่สมรสอายุเกิน บุตร 2 คนอายุเกิน": {
        "spouse": "over_age",
        "child1": "over_age",
        "child2": "over_age",
    },

    "คู่สมรสอายุเกิน บุตรเสียชีวิต 1 คน": {
        "spouse": "over_age",
        "child1": "dead",
        "child2": None,
    },

    "คู่สมรสอายุเกิน บุตรเสียชีวิต 2 คน": {
        "spouse": "over_age",
        "child1": "dead",
        "child2": "dead",
    },

    # =========================================================
    # คู่สมรสเสียชีวิต
    # =========================================================
    "คู่สมรสเสียชีวิต บุตร 2 คน": {
        "spouse": "dead",
        "child1": "normal",
        "child2": "normal",
    },

    "คู่สมรสเสียชีวิต บุตร 1 คนอายุเกิน": {
        "spouse": "dead",
        "child1": "over_age",
        "child2": None,
    },

    "คู่สมรสเสียชีวิต บุตร 2 คนอายุเกิน": {
        "spouse": "dead",
        "child1": "over_age",
        "child2": "over_age",
    },

    "คู่สมรสเสียชีวิต บุตรเสียชีวิต 1 คน": {
        "spouse": "dead",
        "child1": "dead",
        "child2": None,
    },

    "คู่สมรสเสียชีวิต บุตรเสียชีวิต 2 คน": {
        "spouse": "dead",
        "child1": "dead",
        "child2": "dead",
    },
}


# ------------------------------------------------------------
# Build Family
# ------------------------------------------------------------

def build_family(bundle, family, advance_days):
    bundle = "" if pd.isna(bundle) else str(bundle).strip()
    family = "" if pd.isna(family) else str(family).strip()

    # SCK Personal ไม่มีสมาชิกเสมอ
    if bundle == "SCK Personal":
        return None, None, None

    # Family ว่าง ไม่มีสมาชิก
    if family == "":
        return None, None, None

    config = FAMILY_MAPPING.get(family)

    if config is None:
        raise ValueError(f"Unknown Family Mapping: {family}")

    spouse = None
    child1 = None
    child2 = None

    # -------------------------------
    # Spouse
    # -------------------------------
    if config["spouse"] is not None:
        spouse = create_spouse(
            config["spouse"],
            advance_days
        )

    # -------------------------------
    # Child 1
    # -------------------------------
    if config["child1"] is not None:
        child1 = create_child(
            config["child1"],
            advance_days
        )

    # -------------------------------
    # Child 2
    # -------------------------------
    if config["child2"] is not None:
        child2 = create_child(
            config["child2"],
            advance_days
        )

    return spouse, child1, child2


# ------------------------------------------------------------
# Build Column 5
# ------------------------------------------------------------

def build_member_column(bundle, family, advance_days):
    """
    Generate member objects and formatted text.

    Returns
    -------
    member_text
    spouse
    child1
    child2
    """

    spouse, child1, child2 = build_family(
        bundle,
        family,
        advance_days
    )

    text = build_member_text(
        spouse,
        child1,
        child2
    )

    return text, spouse, child1, child2

# ============================================================
# Part 4 : Main Program
# spec_v5.md
# Requires Part 1, Part 2, Part 3
# ============================================================

INPUT_FILE = "SCK insurance - Sheet2.csv"
OUTPUT_FILE = "SCK insurance - Output.csv"


# ------------------------------------------------------------
# Status Column
# ------------------------------------------------------------

def build_status(advance_days):

    start_date, end_date = get_contract_dates(advance_days)

    return (
        f"จำนวนวันที่ต่ออายุล่วงหน้า: {advance_days} วัน\n"
        f"วันที่ต่ออายุ: {thai_date(RENEWAL_DATE)}\n"
        f"วันสิ้นสุดความคุ้มครอง: {thai_date(end_date)}\n"
        f"วันเริ่มสัญญาฉบับปัจจุบัน: {thai_date(start_date)}"
    )


# ------------------------------------------------------------
# Process
# ------------------------------------------------------------

def process():

    df = pd.read_csv(INPUT_FILE)

    outputs = []

    for _, row in df.iterrows():

        # -----------------------------
        # Input
        # -----------------------------
        timeline = row["Timeline"]
        bundle = row["Bundle"]
        family = row["Family"]

        # -----------------------------
        # Timeline
        # -----------------------------
        advance_days = get_advance_days(timeline)

        # -----------------------------
        # Policyholder
        # -----------------------------
        policyholder = create_policyholder(
            advance_days
        )

        policyholder_text = format_policyholder(
            policyholder
        )

        # -----------------------------
        # Members
        # -----------------------------
        member_text, spouse, child1, child2 = \
            build_member_column(
                bundle,
                family,
                advance_days
            )

        # -----------------------------
        # Status
        # -----------------------------
        status_text = build_status(
            advance_days
        )

        # -----------------------------
        # Output Row
        # -----------------------------
        outputs.append({

            "Timeline": timeline,

            "Bundle": bundle,

            "Family": family,

            "ข้อมูลผู้ถือกรมธรรม์":
                policyholder_text,

            "ข้อมูลสมาชิกในกรมธรรม์":
                member_text,

            "Status":
                status_text

        })

    # -------------------------------------------------
    # Export
    # -------------------------------------------------

    output_df = pd.DataFrame(outputs)

    output_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print("=" * 60)
    print("Finished")
    print(f"Rows : {len(output_df)}")
    print(f"Output : {OUTPUT_FILE}")
    print("=" * 60)


# ------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------

if __name__ == "__main__":
    process()