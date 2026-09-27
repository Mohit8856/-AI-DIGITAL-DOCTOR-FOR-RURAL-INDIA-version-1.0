from modules.hospital.hospital_finder import find_hospitals

def test_hospital_finder():
    result = find_hospitals(23.2599, 77.4126)
    assert isinstance(result, list)