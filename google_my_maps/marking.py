from enum import StrEnum, IntEnum

line_width_normal: float = 3.5


class StatusColors(StrEnum):
    # Google MyMaps encodes colors in Style's `id` attribute
    # in RGB hex format, with all letters in uppercase.

    TO_VISIT = "1A237E"
    RESTAURANTS = "FF5252"
    VISITED_P_ONLY = "F57C00"
    UNVERIFIED = "0288D1"
    VISITED_A_ONLY = "9C27B0"
    VISITED_AP = "795548"
    REJECTED = "BDBDBD"
    TRANSPORTATION = "000000"
    VISITED_AP_TREKS = "AFB42B"
    VISITED_AP_ROUTES_EVEN = "880E4F"
    TRIP_PLANNING = "4E342E"


class Icons(IntEnum):
    DEFAULT = 1899
    "Pin"

    CIRCLE = 1499
    "Circle"

    STAR = 1502
    "Star"

    DIAMOND = 1501
    "Diamond"

    X = 1898
    "X"

    CYCLING = 1522
    "Cycling"

    KAYAKING = 1615
    "Kayaking"

    PICNIC = 1650
    "Picnic"

    SKIING_DOWNHILL = 1688
    "Skiing (Downhill)"

    SKIING_CROSS_COUNTRY = 1690
    "Skiing (Cross Country)"

    SWIMMING = 1701
    "Swimming"

    BEACH = 1521
    "Beach"

    TREE_CONIFER = 1720
    "Tree (Conifer)"

    TREE_DECIDUOUS = 1886
    "Tree (Deciduous)"

    MOUNTAIN = 1634
    "Mountain"

    HIKING = 1596
    "Hiking"

    VIEWPOINT = 1523
    "Viewpoint"

    CAMPING = 1765
    "Camping"

    RESTAURANT = 1577
    "Restaurant"

    CAFE = 1534
    "Cafe"

    SHOPPING_CART = 1685
    "Shopping Cart"

    CURRENCY_EXCHANGE = 1555
    "Currency Exchange"

    TICKET_STAR = 1713
    "Ticket (Star)"

    PARKING = 1644
    "Parking"

    PARK = 1720
    "Park"

    HOUSE = 1603
    "House"

    LOOKOUT_TOWER = 1621
    "Lookout Tower"

    MONUMENT = 1599
    "Monument"

    MUSEUM = 1636
    "Museum"

    HISTORIC_BUILDING = 1598
    "Historic Building"

    VISTA_PARTIAL = 1728
    "Vista (Partial)"

    HOTEL = 1602
    "Hotel"

    GAS_STATION = 1581
    "Gas Station"

    HARDWARE = 1590
    "Hardware"

    PLACE_OF_WORSHIP = 1671
    "Place of Worship"

    INFORMATION = 1608
    "Information"

    CITY = 1546
    "City"

    DOWNTOWN = 1547
    "Downtown"

    WALKING = 1731
    "Walking"

    BUS = 1532
    "Bus"

    TRAIN = 1716
    "Train"

    TRAIN_STEAM = 1717
    "Train (Steam)"

    VEHICLE_FERRY = 1537
    "Vehicle Ferry"

    AIRPORT = 1504
    "Airport"

    RENTAL_CAR = 1741
    "Rental Car"

    DEATH = 1556
    "Death"

    WATER = 1703
    "Water"

    LAKE = 1723
    "Lake"
