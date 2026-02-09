import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
import datetime
from enum import StrEnum
from typing import Pattern, Dict, List


class UnitClass(StrEnum):
    MK = "MK"
    LL = "LL"
    S = "S"
    KK = "KK"
    ARS = "ARS"
    "Księgi Sądów: Asesorskiego, Relacyjnego i Sejmowego"
    KS_REF = "Ks. Ref."
    "Księgi Sądu Referendarskiego"
    LUSTRACJE_DZ18 = "Lustracje, dz. XVIII"
    "Lustracje, dz. XVIII"

    @staticmethod
    def from_unit_id(unit_id: str):
        if unit_id.startswith("[A ") or unit_id == "[E 8636]":
            return UnitClass.MK
        if "Tzw. ML dz." in unit_id or unit_id.startswith("(AP Kraków: I.T."):
            return UnitClass.ARS

        for member in UnitClass.__members__.values():
            if unit_id.startswith(f"{member.value}") or unit_id.startswith(f"[{member.value} "):
                return member
        raise ValueError(f"No unit class matches the unit ID: `{unit_id}`")


@dataclass
class DateRange:
    start_date: datetime.date
    end_date: datetime.date


@dataclass
class Unit:
    unit_id: str
    dates: List[DateRange] = field(default_factory=list)

def roman_to_arabic_number(roman: str):
    return {
        'I': 1,
        'II': 2,
        'III': 3,
        'IV': 4,
        'V': 5,
        'VI': 6,
        'VII': 7,
        'VIII': 8,
        'IX': 9,
        'X': 10,
        'XI': 11,
        'XII': 12
    }[roman]

inventory: Dict[UnitClass, List[Unit]] = {}

tree = ET.parse('data/agad_inwentarze_metr_korx.xml')
root = tree.getroot()

comments_re: Pattern = re.compile(r"\(.*?\)")
extra_dates_re: Pattern = re.compile(r"\[.*?]")
for book in root.iter('c02'):
    did = book.find('did')
    unit_id = did.find('unitid').text
    print(f"Unit ID: {unit_id}")

    unit = Unit(unit_id)

    if (dates_elem := did.find('unitdate')) is not None:
        dates_str = did.find('unitdate').text
        dates_str = comments_re.sub(r"", dates_str)
        dates_str = extra_dates_re.sub(r"", dates_str)
        dates = dates_str.split('; ')
        # print("\t" + "\n\t".join(dates))

        for date_str in dates:
            if not date_str.strip():
                break

            print(f"\t{date_str}")
            start_year = int(date_str[:4])
            start_date = datetime.date(start_year, 1, 1)
            end_date = datetime.date(start_year, 12, 31)

            rest = date_str[4:].lstrip()

            if not rest:
                unit.dates.append(DateRange(start_date, end_date))

            parts = rest.split('-')

            if "-" in date_str:
                raise NotImplementedError
            else:
                # np. 9 26 VIII
                raise NotImplementedError
                # # YYYY d M
                # d = date
                # unit.dates.append(DateRange())
        # FIXME: Multiple "-" within one entry!

    unit_class = UnitClass.from_unit_id(unit_id)

    if unit_class not in inventory:
        inventory[unit_class] = []
    inventory[unit_class].append(unit)
