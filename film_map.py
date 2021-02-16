'''
In this module user enters year and coordinates
Make a map with 10 marked nearby places in location country
     where films were shot in given year
'''
import math
from time import perf_counter
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable


def calc_distance(lat1, lon1, lat2, lon2):
    '''
    Return distance between (lat1, lon1) and (lat2, lon2)

    This function is taken from: https://cutt.ly/GkN43NR

    >>> calc_distance(49.842180, 24.025011, 50.447739, 30.516820)
    467.4656467572212
    >>> calc_distance(30.246414, -97.735555, 49.842180, 24.025011)
    9425.232027173279
    '''
    R = 6373.0
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat/2)**2 +\
        math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    distance = R * c
    return distance


def find_nearby_films(lat1, lon1, year):
    '''
    location - (lat1, lon1)

    Return up to 10 nearby places in location country
     where films were shot in given year
    If location is not in country, return None
    '''
    t_start = perf_counter()
    films = open('locations.list', 'r', encoding='UTF-8', errors='ignore')
    geolocator = Nominatim(user_agent="film_map")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    nearby_films = []
    curr_location = geolocator.reverse(str(lat1) + ',' + str(lon1), language='en')
    if not curr_location:
        return None
    print("Map is generating...")
    print("Please wait...")
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
        film[0] = film[0].split('(')[0].strip()
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


def get_map(lat1, lon1, year):
    '''
    Get Film_map.html
    Film_map.html - a map with markers of nearby films
    If there are no films, return "No films were shot in this country in {year}"
    If location is not in country, return "Bad location"
    '''
    nearby_films = find_nearby_films(lat1, lon1, year)
    if not isinstance(nearby_films, list):
        return "Bad location"
    if len(nearby_films) == 0:
        return f"No films were shot in this country in {year}"
    nearby_films.sort(key=lambda x: x[1])
    nearby_films = list(map(list, nearby_films))
    i = 1
    while i != len(nearby_films):
        if nearby_films[i][1] == nearby_films[i-1][1]:
            nearby_films[i-1][2] += f', {nearby_films[i][2]}'
            nearby_films.pop(i)
            continue
        i += 1
    f_map = folium.Map(location=[lat1, lon1],
                     zoom_start=5)
    fg = folium.FeatureGroup(name="Films")
    for _, coords, name in nearby_films:
        fg.add_child(folium.Marker(location=coords,
                                   popup=name,
                                   icon=folium.Icon()))
    f_map.add_child(folium.Marker(location=[lat1, lon1],
                                popup='Your location',
                                icon=folium.Icon(color='red')))
    f_map.add_child(fg)
    f_map.add_child(folium.LayerControl())
    f_map.save('Film_map.html')
    return 'Map is generated successfully. Open Film_map.html in browser'


def main():
    '''
    Main function, which starts program.
    '''
    year = int(input('Please enter a year you would like to have a map for: '))
    lat = float(input('Please enter latitude: '))
    lon = float(input('Please enter longitude: '))
    print(get_map(lat, lon, year))


if __name__ == "__main__":
    main()
