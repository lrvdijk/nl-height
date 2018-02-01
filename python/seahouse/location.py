from geopy.geocoders import Nominatim


def get_coordinates(location):
    geolocator = Nominatim()
    result = geolocator.geocode(location)

    if not result:
        raise Exception("Could not get geocoding results from Google Maps "
                        "API")

    return result.longitude, result.latitude
