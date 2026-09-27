# ============================================================
# AI DIGITAL DOCTOR
# HOSPITAL FINDER
# ============================================================

import math
import requests


# ============================================================
# SETTINGS
# ============================================================

SEARCH_RADIUS_KM = 20.0
SEARCH_RADIUS_METERS = 20000

MAX_RESULTS = 20

# We route every candidate returned by Overpass.
# This avoids the old "first 50 only" problem.
MAX_ROUTING_CANDIDATES = 100

OVERPASS_TIMEOUT = 60
OSRM_TIMEOUT = 30


# ============================================================
# OVERPASS SERVERS
# ============================================================

OVERPASS_SERVERS = [
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter"
]


# ============================================================
# OSRM
# ============================================================

OSRM_SERVER = "https://router.project-osrm.org"


# ============================================================
# HTTP SESSION
# ============================================================

session = requests.Session()

session.headers.update({
    "User-Agent": "AI-Digital-Doctor/1.0"
})


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):
    """
    Calculate straight-line distance in kilometres.
    """

    R = 6371.0

    lat1 = float(lat1)
    lon1 = float(lon1)

    lat2 = float(lat2)
    lon2 = float(lon2)

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        +
        math.cos(phi1)
        * math.cos(phi2)
        * math.sin(dlambda / 2) ** 2
    )

    a = max(
        0.0,
        min(1.0, a)
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


# ============================================================
# GET COORDINATES
# ============================================================

def get_coordinates(element):

    element_type = element.get("type")

    # --------------------------------------------------------
    # NODE
    # --------------------------------------------------------

    if element_type == "node":

        lat = element.get("lat")
        lon = element.get("lon")

        if lat is not None and lon is not None:

            return (
                float(lat),
                float(lon)
            )

    # --------------------------------------------------------
    # WAY / RELATION
    # --------------------------------------------------------

    center = element.get("center")

    if center:

        lat = center.get("lat")
        lon = center.get("lon")

        if lat is not None and lon is not None:

            return (
                float(lat),
                float(lon)
            )

    return None, None


# ============================================================
# GET NAME
# ============================================================

def get_name(tags):

    return str(

        tags.get("name")
        or tags.get("official_name")
        or tags.get("short_name")
        or tags.get("operator")
        or "Unnamed Healthcare Facility"

    ).strip()


# ============================================================
# GET ADDRESS
# ============================================================

def get_address(tags):

    parts = []

    keys = [
        "addr:housenumber",
        "addr:street",
        "addr:locality",
        "addr:village",
        "addr:town",
        "addr:city",
        "addr:district",
        "addr:state",
        "addr:postcode"
    ]

    for key in keys:

        value = tags.get(key)

        if value:

            value = str(value).strip()

            if value and value not in parts:

                parts.append(value)

    if parts:

        return ", ".join(parts)

    return (
        tags.get("addr:full")
        or tags.get("description")
        or "Address not available"
    )


# ============================================================
# GET PHONE
# ============================================================

def get_phone(tags):

    return (

        tags.get("phone")
        or tags.get("contact:phone")
        or tags.get("mobile")
        or "Not available"

    )


# ============================================================
# FACILITY TYPE
# ============================================================

def get_facility_type(tags):

    amenity = str(
        tags.get("amenity", "")
    ).lower()

    healthcare = str(
        tags.get("healthcare", "")
    ).lower()

    if (
        amenity == "hospital"
        or healthcare == "hospital"
    ):

        return "Hospital"

    if healthcare == "centre":

        return "Health Centre"

    if healthcare == "clinic":

        return "Clinic"

    return "Healthcare Facility"


# ============================================================
# VETERINARY FILTER
# ============================================================

def is_veterinary(
    tags,
    name
):

    text = (

        name
        + " "
        + str(tags.get("description", ""))
        + " "
        + str(tags.get("healthcare", ""))
        + " "
        + str(tags.get("amenity", ""))

    ).lower()

    veterinary_words = [

        "veterinary",
        "animal hospital",
        "animal clinic",
        "animal care",
        "pet hospital",
        "pet clinic",
        "vet clinic",
        "vet hospital"

    ]

    return any(
        word in text
        for word in veterinary_words
    )


# ============================================================
# GOOGLE MAPS DIRECTIONS
# ============================================================

def create_maps_url(
    latitude,
    longitude
):

    return (

        "https://www.google.com/maps/dir/"
        "?api=1"
        f"&destination={latitude},{longitude}"

    )


# ============================================================
# OVERPASS QUERY
# ============================================================

def create_overpass_query(
    latitude,
    longitude
):

    return f"""
[out:json][timeout:55];

(
    node["amenity"="hospital"](
        around:{SEARCH_RADIUS_METERS},{latitude},{longitude}
    );

    way["amenity"="hospital"](
        around:{SEARCH_RADIUS_METERS},{latitude},{longitude}
    );

    relation["amenity"="hospital"](
        around:{SEARCH_RADIUS_METERS},{latitude},{longitude}
    );

    node["healthcare"="hospital"](
        around:{SEARCH_RADIUS_METERS},{latitude},{longitude}
    );

    way["healthcare"="hospital"](
        around:{SEARCH_RADIUS_METERS},{latitude},{longitude}
    );

    relation["healthcare"="hospital"](
        around:{SEARCH_RADIUS_METERS},{latitude},{longitude}
    );

    node["healthcare"="centre"](
        around:{SEARCH_RADIUS_METERS},{latitude},{longitude}
    );

    way["healthcare"="centre"](
        around:{SEARCH_RADIUS_METERS},{latitude},{longitude}
    );

    relation["healthcare"="centre"](
        around:{SEARCH_RADIUS_METERS},{latitude},{longitude}
    );
);

out center tags;
"""


# ============================================================
# OSRM TABLE
# ============================================================

def get_road_distances(
    user_lat,
    user_lon,
    hospitals
):
    """
    Calculate road distance from user to ALL hospitals
    using OSRM Table service.

    Returns:
        list of dictionaries
    """

    if not hospitals:

        return []


    # --------------------------------------------------------
    # OSRM supports multiple coordinates:
    #
    # longitude,latitude
    # --------------------------------------------------------

    coordinates = [

        f"{user_lon},{user_lat}"

    ]

    for hospital in hospitals:

        coordinates.append(

            f"{hospital['longitude']},"
            f"{hospital['latitude']}"

        )


    coordinate_string = ";".join(
        coordinates
    )


    url = (

        f"{OSRM_SERVER}"
        f"/table/v1/driving/"
        f"{coordinate_string}"

    )


    params = {

        "sources": "0",

        "annotations": "distance,duration"

    }


    print()
    print("=" * 75)
    print("OSRM ROAD DISTANCE TABLE")
    print("=" * 75)

    print(
        f"Routing {len(hospitals)} hospitals..."
    )


    try:

        response = session.get(

            url,

            params=params,

            timeout=OSRM_TIMEOUT

        )


        response.raise_for_status()


        data = response.json()


        # ----------------------------------------------------
        # CHECK OSRM
        # ----------------------------------------------------

        if data.get("code") != "Ok":

            print(
                "OSRM Table error:",
                data.get("code")
            )

            return []


        distances = data.get(
            "distances"
        )

        durations = data.get(
            "durations"
        )


        if not distances:

            print(
                "OSRM returned no distances."
            )

            return []


        # ----------------------------------------------------
        # FIRST ROW
        #
        # Because source = 0,
        # distances[0] contains:
        #
        # [user -> user,
        #  user -> hospital1,
        #  user -> hospital2, ...]
        # ----------------------------------------------------

        distance_row = distances[0]

        duration_row = (

            durations[0]

            if durations
            else []

        )


        routed = []


        for index, hospital in enumerate(
            hospitals
        ):

            table_index = index + 1

            if table_index >= len(
                distance_row
            ):

                continue


            distance_meters = (

                distance_row[
                    table_index
                ]

            )


            if distance_meters is None:

                print(

                    "ROUTE FAILED:",
                    hospital["name"]

                )

                continue


            road_distance = (

                float(distance_meters)
                / 1000.0

            )


            travel_time = None


            if (

                table_index
                <
                len(duration_row)

            ):

                duration_seconds = (

                    duration_row[
                        table_index
                    ]

                )

                if duration_seconds is not None:

                    travel_time = max(

                        1,

                        round(

                            float(
                                duration_seconds
                            )
                            / 60.0

                        )

                    )


            hospital["road_distance"] = round(

                road_distance,

                2

            )


            hospital["distance"] = round(

                road_distance,

                2

            )


            hospital["travel_time"] = (

                travel_time

            )


            routed.append(
                hospital
            )


            print(

                f"{hospital['name']} | "
                f"Road: "
                f"{hospital['road_distance']} km | "
                f"Straight: "
                f"{hospital['straight_distance']} km | "
                f"Time: "
                f"{hospital['travel_time']} min"

            )


        return routed


    except requests.exceptions.Timeout:

        print(
            "OSRM Table request timed out."
        )

        return []


    except requests.exceptions.RequestException as error:

        print(
            "OSRM Table request failed:"
        )

        print(error)

        return []


    except ValueError as error:

        print(
            "Invalid OSRM JSON:"
        )

        print(error)

        return []


    except Exception as error:

        print(
            "Unexpected OSRM error:"
        )

        print(error)

        return []


# ============================================================
# FIND HOSPITALS
# ============================================================

def find_hospitals(
    latitude,
    longitude
):

    # ========================================================
    # VALIDATE GPS
    # ========================================================

    try:

        latitude = float(latitude)
        longitude = float(longitude)

    except (
        TypeError,
        ValueError
    ):

        print(
            "ERROR: Invalid GPS coordinates."
        )

        return []


    if not (
        -90 <= latitude <= 90
    ):

        print(
            "ERROR: Invalid latitude."
        )

        return []


    if not (
        -180 <= longitude <= 180
    ):

        print(
            "ERROR: Invalid longitude."
        )

        return []


    # ========================================================
    # DEBUG
    # ========================================================

    print()
    print("=" * 75)
    print("AI DIGITAL DOCTOR - HOSPITAL SEARCH")
    print("=" * 75)

    print(
        f"User latitude : {latitude}"
    )

    print(
        f"User longitude: {longitude}"
    )

    print(
        f"Search radius : {SEARCH_RADIUS_KM} km"
    )

    print("=" * 75)


    # ========================================================
    # CREATE OVERPASS QUERY
    # ========================================================

    query = create_overpass_query(

        latitude,
        longitude

    )


    # ========================================================
    # TRY OVERPASS SERVERS
    # ========================================================

    for server in OVERPASS_SERVERS:

        print()

        print(
            f"Trying hospital server: {server}"
        )


        try:

            response = session.post(

                server,

                data=query,

                timeout=OVERPASS_TIMEOUT

            )


            response.raise_for_status()


            data = response.json()


            elements = data.get(
                "elements",
                []
            )


            print(
                f"Raw healthcare elements: "
                f"{len(elements)}"
            )


            if not elements:

                continue


            # =================================================
            # CREATE CANDIDATES
            # =================================================

            candidates = []

            seen = set()


            for element in elements:

                tags = element.get(
                    "tags",
                    {}
                )


                # -------------------------------------------------
                # NAME
                # -------------------------------------------------

                name = get_name(
                    tags
                )


                # -------------------------------------------------
                # VETERINARY FILTER
                # -------------------------------------------------

                if is_veterinary(

                    tags,
                    name

                ):

                    continue


                # -------------------------------------------------
                # COORDINATES
                # -------------------------------------------------

                hospital_lat, hospital_lon = (

                    get_coordinates(
                        element
                    )

                )


                if (

                    hospital_lat is None
                    or hospital_lon is None

                ):

                    continue


                # -------------------------------------------------
                # STRAIGHT DISTANCE
                # -------------------------------------------------

                straight_distance = calculate_distance(

                    latitude,
                    longitude,

                    hospital_lat,
                    hospital_lon

                )


                # -------------------------------------------------
                # 20 KM SEARCH FILTER
                # -------------------------------------------------

                if (

                    straight_distance
                    >
                    SEARCH_RADIUS_KM

                ):

                    continue


                # -------------------------------------------------
                # DUPLICATE
                # -------------------------------------------------

                key = (

                    name.lower(),

                    round(
                        hospital_lat,
                        5
                    ),

                    round(
                        hospital_lon,
                        5
                    )

                )


                if key in seen:

                    continue


                seen.add(key)


                # -------------------------------------------------
                # HOSPITAL OBJECT
                # -------------------------------------------------

                hospital = {

                    "name":
                        name,

                    "type":
                        get_facility_type(
                            tags
                        ),

                    "latitude":
                        hospital_lat,

                    "longitude":
                        hospital_lon,

                    "straight_distance":
                        round(
                            straight_distance,
                            2
                        ),

                    # IMPORTANT:
                    # Do not initially put
                    # straight distance here.
                    "distance":
                        None,

                    "road_distance":
                        None,

                    "travel_time":
                        None,

                    "address":
                        get_address(
                            tags
                        ),

                    "phone":
                        get_phone(
                            tags
                        ),

                    "maps_url":
                        create_maps_url(

                            hospital_lat,
                            hospital_lon

                        )

                }


                candidates.append(
                    hospital
                )


            # =================================================
            # NO CANDIDATES
            # =================================================

            if not candidates:

                print(
                    "No healthcare facilities "
                    "within 20 km."
                )

                continue


            # =================================================
            # SORT CANDIDATES BY STRAIGHT DISTANCE
            # =================================================

            candidates.sort(

                key=lambda hospital:

                    hospital[
                        "straight_distance"
                    ]

            )


            # =================================================
            # ROUTING LIMIT
            # =================================================

            routing_candidates = (

                candidates[
                    :MAX_ROUTING_CANDIDATES
                ]

            )


            print()

            print(
                f"Healthcare candidates: "
                f"{len(candidates)}"
            )

            print(
                f"Candidates sent to routing: "
                f"{len(routing_candidates)}"
            )


            # =================================================
            # CALCULATE ROAD DISTANCES
            # =================================================

            routed = get_road_distances(

                latitude,
                longitude,

                routing_candidates

            )


            if not routed:

                print()

                print(
                    "No road routes available."
                )

                return []


            # =================================================
            # SORT BY ROAD DISTANCE
            # =================================================

            routed.sort(

                key=lambda hospital:

                    hospital["road_distance"]

            )


            # =================================================
            # TAKE 20 NEAREST BY ROAD
            # =================================================

            hospitals = routed[
                :MAX_RESULTS
            ]


            # =================================================
            # FINAL OUTPUT
            # =================================================

            print()
            print("=" * 75)
            print("FINAL NEAREST HOSPITALS")
            print("=" * 75)


            for index, hospital in enumerate(

                hospitals,

                start=1

            ):

                print()

                print(

                    f"{index}. "
                    f"{hospital['name']}"

                )

                print(

                    f"   ROAD DISTANCE : "
                    f"{hospital['road_distance']} km"

                )

                print(

                    f"   STRAIGHT      : "
                    f"{hospital['straight_distance']} km"

                )

                print(

                    f"   TRAVEL TIME   : "
                    f"{hospital['travel_time']} min"

                )

                print(

                    f"   GPS           : "
                    f"{hospital['latitude']}, "
                    f"{hospital['longitude']}"

                )

                print(

                    f"   ADDRESS       : "
                    f"{hospital['address']}"

                )

                print("-" * 75)


            print()

            print(
                f"Returning "
                f"{len(hospitals)} hospitals."
            )

            print("=" * 75)


            return hospitals


        # ====================================================
        # OVERPASS TIMEOUT
        # ====================================================

        except requests.exceptions.Timeout:

            print()

            print(
                "Hospital server timed out:"
            )

            print(server)

            continue


        # ====================================================
        # OVERPASS REQUEST ERROR
        # ====================================================

        except requests.exceptions.RequestException as error:

            print()

            print(
                "Hospital server request failed:"
            )

            print(error)

            continue


        # ====================================================
        # JSON ERROR
        # ====================================================

        except ValueError as error:

            print()

            print(
                "Invalid JSON response:"
            )

            print(error)

            continue


        # ====================================================
        # OTHER ERROR
        # ====================================================

        except Exception as error:

            print()

            print(
                "Unexpected hospital error:"
            )

            print(error)

            continue


    # ============================================================
    # ALL SERVERS FAILED
    # ============================================================

    print()

    print("=" * 75)

    print(
        "ALL HOSPITAL SERVERS FAILED"
    )

    print("=" * 75)

    return []