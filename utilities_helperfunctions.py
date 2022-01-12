import numpy as np


def lat_lon_2_m(latitude_1, longitude_1, latitude_2, longitude_2):
    # Radius of the earth in m
    radius_earth = 6371009
    d_latitude = np.deg2rad(latitude_2 - latitude_1)
    d_longitude = np.deg2rad(longitude_2 - longitude_1)
    latitude_1 = np.deg2rad(latitude_1)
    latitude_2 = np.deg2rad(latitude_2)
    a = (np.sin(d_latitude / 2)) ** 2 + np.cos(latitude_1) * np.cos(latitude_2) * (np.sin(d_longitude / 2)) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    distance = radius_earth * c
    return distance


def calculate_distance_points(points):
    # initialize distance array
    distance = np.zeros(len(points))
    # loop all points
    for i in range(0, len(points) - 1):
        # calculate distance between two consecutive points using lat_lon_2_km function
        d = lat_lon_2_m(
            points[i].x,
            points[i].y,
            points[i+1].x,
            points[i+1].y,)
        # append distance to array
        distance[i + 1] = d
    return distance
