from dataclasses import dataclass
from enum import StrEnum

from pyexcel_ods3 import get_data

class EntryType(StrEnum):
    FIELD_REGULAR = "P"
    FIELD_AGRICULTURE = "PO"
    ORCHARD = "S"
    ORCHARD_SMALL = "Sm"
    GARDEN = "O"
    GARDEN_SMALL = "Om"
    BUSHES = "K"
    OWNER = "G"
    MEADOW = "Ł"
    MEADOW_WETLAND = "Łm"
    MEADOW_GRAZE = "Pa"

@dataclass
class Dimensions:
    length: float
    width: float

class Owner:
    idNum: int
    name: str
    surname: str

class LandPiece:
    owner

data = get_data("/home/pawel/Projects/MszanaDln/_SOURCES/metryka_jozefinska.ods")
metr = data['M_Joseph']

x = metr[0]

import json
print(json.dumps(data))