import geopandas as gpd
import overpy
from overpy.exception import OverpassTooManyRequests
from shapely.geometry import Point
import helpers as h
import time
import warnings
from shapely.errors import ShapelyDeprecationWarning


# Get dataframe with track id and count intersections with indicator buffers
def add_indicator_count_to_tracks_df(track_id: int, data_df, tracks_gdf, bus_df, sub_df):
    time_start = tracks_gdf["time_start"][track_id]
    time_stop = tracks_gdf["time_stop"][track_id]

    # Init GDF and buffer points
    single_track_gdf = gpd.GeoDataFrame(data=data_df[(data_df["time"] >= time_start) &
                                                     (data_df["time"] <= time_stop)])
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)
        single_track_gdf["geometry"] = gpd.points_from_xy(single_track_gdf.longitude, single_track_gdf.latitude,
                                                          crs="EPSG:4326")

    single_track_gdf = single_track_gdf.reset_index(drop=True)
    single_track_gdf = single_track_gdf.to_crs("EPSG:3857")
    single_track_gdf["geometry"] = single_track_gdf.geometry.buffer(h.BUFFER_RADIUS)
    single_track_gdf = single_track_gdf.to_crs("EPSG:4326")

    single_track_gdf = single_track_gdf[["time", "modality", "geometry"]]

    # Get GDF with indicators and count when indicator lies within buffer area
    bus_gdf, sub_gdf = bus_df, sub_df
    tracks_gdf.loc[track_id, "bus_count"] = len(gpd.sjoin(bus_gdf, single_track_gdf, how="inner", op="within").index)
    tracks_gdf.loc[track_id, "sub_count"] = len(gpd.sjoin(sub_gdf, single_track_gdf, how="inner", op="within").index)

    return tracks_gdf


def get_indicators_gdf():
    print("-- Starting GIS Extraction --")
    rows_list = []

    # Query with bus and subway stations
    overpass_query_begin = '[out:json]; area["name"="Oberbayern"]->.muc;'
    overpass_query_bus = overpass_query_begin + '(node["highway"="bus_stop"](area.muc););out geom;'
    overpass_query_sub = overpass_query_begin + '(node["railway"="station"]["station"="subway"](area.muc););out geom;'

    op_api = overpy.Overpass()
    time_start = time.time()

    while True:
        try:
            response_bus = op_api.query(overpass_query_bus)
            time.sleep(0.5)
            response_sub = op_api.query(overpass_query_sub)
            break
        except OverpassTooManyRequests:
            print("Encountered TooManyRequests Exception! Restarting...")
            continue

    # Add lat and lon from response to list and create dataframes
    for node in response_bus.nodes:
        dict_pd = {"geometry": (Point(node.lon, node.lat))}
        rows_list.append(dict_pd)

    bus_gdf = gpd.GeoDataFrame(rows_list, crs='epsg:4326')
    rows_list = []

    for node in response_sub.nodes:
        dict_pd = {"geometry": (Point(node.lon, node.lat))}
        rows_list.append(dict_pd)

    sub_gdf = gpd.GeoDataFrame(rows_list, crs="epsg:4326")
    rows_list = []

    print("-- Fetching GIS Data took %.2f seconds --" % float(time.time() - time_start))

    return bus_gdf, sub_gdf


def main(data_gdf: gpd.GeoDataFrame, tracks_gdf: gpd.GeoDataFrame):

    time_main_start = time.time()
    print("--- Starting main GIS Script ---")

    bus_gdf, sub_gdf = get_indicators_gdf()
    print("-- Starting to add GIS info to tracks. --")

    for i in range(0, len(tracks_gdf)):
        tracks_gdf = add_indicator_count_to_tracks_df(i, data_gdf, tracks_gdf, bus_gdf, sub_gdf)
        if (i % 20) == 0 or i == len(tracks_gdf) - 1:
            print("- Finished Track %d. -" % i)

    print("-- Finished adding info to all tracks. --")
    print("--- Finished main GIS Script in %.2f seconds ---" % float(time.time() - time_main_start))

    return tracks_gdf


if __name__ == "__main__":
    print("Starting GIS Extraction Main.")


