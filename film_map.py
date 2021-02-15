import math
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable
from time import perf_counter


def calc_distance(lat1, lon1, lat2, lon2):
    '''
    This function is taken from: https://cutt.ly/GkN43NR
    
    '''
    R = 6373.0
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    distance = R * c
    return distance


def find_nearby_films(lat1, lon1, year):
    t_start = perf_counter()
    films = open('locations.list', 'r', encoding='UTF-8', errors='ignore')
    geolocator = Nominatim(user_agent="film_map")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0)
    nearby_films = []
    curr_location = geolocator.reverse(str(lat1) + ',' + str(lon1), language='en')
    curr_location = curr_location.address.split(',')[-1].strip()
    if curr_location == 'United Kingdom':
        curr_location = 'UK'
    elif curr_location == "United States":
        curr_location = 'USA'

    for film in films.readlines()[14:]:
        film = film.split('\t')
        if film[-1][0] == '(':
            film.pop(-1)
        if curr_location not in film[-1]:
            continue
        if f'({year})' not in film[0]:
            continue
        if '{' in film[0]:
            film[0] = film[0].split('{')[0].strip()
        try:
            location = geolocator.geocode(film[-1].strip())
            while not location:
                film[-1] = film[-1].split(',')
                film[-1] = ', '.join(film[-1][1:])
                location = geolocator.geocode(film[-1])
        except GeocoderUnavailable:
            continue
        coords = (location.latitude, location.longitude)
        dist = calc_distance(lat1, lon1, *coords)
        if len(nearby_films) != 10:
            if (dist, coords, film[0]) in nearby_films:
                    continue
            nearby_films.append((dist, coords, film[0]))
        else:
            if dist < max(nearby_films, key=lambda x: x[0])[0]:
                if (dist, coords, film[0]) in nearby_films:
                    continue
                nearby_films.remove(max(nearby_films, key=lambda x: x[0]))
                nearby_films.append((dist, coords, film[0]))
        if perf_counter() - t_start > 165:
            break
    return nearby_films


if __name__ == "__main__":
    print(find_nearby_films(61.485063, 14.392731, 2010))