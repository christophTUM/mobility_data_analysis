import geopandas as gpd
import overpy
from shapely.geometry import Point
import helpers as h
import time
import warnings
from shapely.errors import ShapelyDeprecationWarning


# Convert string time to pandas Timestamp
data_df, tracks_df = h.get_dataframes()


# Get dataframe with track id and count intersections with indicator buffers
def add_indicator_count_to_data_df(track_id: int):
    time_start = tracks_df["time_start"][track_id]
    time_stop = tracks_df["time_stop"][track_id]

    # Init GDF and buffer points
    single_track_gdf = gpd.GeoDataFrame(data=data_df[(data_df["time"] >= time_start) &
                                                     (data_df["time"] <= time_stop)])
    # noinspection INSPECTION_NAME
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
    bus_df, sub_df = get_indicators_gdf(track_id=track_id)
    tracks_df.loc[track_id, "bus_count"] = len(gpd.sjoin(bus_df, single_track_gdf, how="inner", op="within").index)
    tracks_df.loc[track_id, "sub_count"] = len(gpd.sjoin(sub_df, single_track_gdf, how="inner", op="within").index)

    return


def get_indicators_gdf(track_id: int):
    rows_list = []

    # Query with bus and subway stations
    overpass_query_begin= '[out:json]; area["name"="München"]->.muc;'
    overpass_query_bus = overpass_query_begin + '(node["highway"="bus_stop"](area.muc););out geom;'
    overpass_query_sub = overpass_query_begin + '(node["railway"="station"]["station"="subway"](area.muc););out geom;'

    op_api = overpy.Overpass()
    time_start = time.time()

    response_bus = op_api.query(overpass_query_bus)
    response_sub = op_api.query(overpass_query_sub)

    # Add lat and lon from response to list and create dataframes
    for node in response_bus.nodes:
        dict_pd = {"geometry": (Point(node.lon, node.lat))}
        rows_list.append(dict_pd)

    bus_df = gpd.GeoDataFrame(rows_list, crs='epsg:4326')
    rows_list = []

    for node in response_sub.nodes:
        dict_pd = {"geometry": (Point(node.lon, node.lat))}
        rows_list.append(dict_pd)

    sub_df = gpd.GeoDataFrame(rows_list, crs="epsg:4326")
    rows_list = []

    print("-- Track %d: Fetching GIS Data took %.2f seconds --" % (track_id, float(time.time() - time_start)))

    return bus_df, sub_df


def main(df: gpd.GeoDataFrame):

    time_main_start = time.time()
    print("--- Starting main GIS Script ---")

    for idx, track in enumerate(df):
        add_indicator_count_to_data_df(idx)

    print("--- Finished main GIS Script in %.2f seconds ---" % float(time.time() - time_main_start))


if __name__ == "__main__":
    main(tracks_df)
    print(tracks_df)


