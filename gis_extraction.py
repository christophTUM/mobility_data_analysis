import pandas as pd
import geopandas as gpd
import overpy
from shapely.geometry import Point
import numpy as np
import helpers as h


# Convert string time to pandas Timestamp
all_data_df = pd.read_csv(h.ALL_DATA)
tracks_df = pd.read_csv(h.TRACKS)
tracks_df["time_start"] = tracks_df.time_start.astype('datetime64[ns]')
tracks_df["time_stop"] = tracks_df.time_stop.astype('datetime64[ns]')
all_data_df["time"] = all_data_df.time.astype('datetime64[ns]')


# Define functions
def get_single_track_gdf(track_id: int):
    time_start = tracks_df["time_start"][track_id]
    time_stop = tracks_df["time_stop"][track_id]

    # Init GDF and buffer points
    single_track_gdf = gpd.GeoDataFrame(data=all_data_df[(all_data_df["time"] >= time_start) &
                                                         (all_data_df["time"] <= time_stop)],
                                        crs='epsg:4326')
    single_track_gdf["geometry"] = gpd.points_from_xy(single_track_gdf.longitude, single_track_gdf.latitude)
    single_track_gdf["area"] = single_track_gdf.geometry.apply(lambda x: x.buffer(h.BUFFER_RADIUS))
    print(single_track_gdf.geometry)
    # Get GDF with indicators and count when indicator lies within buffer area
    indicator_gdf = get_indicators_gdf()
    count_list = np.zeros(len(single_track_gdf.area.values))

    for idx, (idx_track, row_track) in enumerate(single_track_gdf.iterrows()):
        area = row_track["area"]
        for idx_ind, row_indicator in indicator_gdf.iterrows():
            if row_indicator["geometry"].within(area):
                count_list[idx] += 1

    single_track_gdf["indicators_count"] = count_list

    return single_track_gdf


def get_indicators_gdf():
    rows_list = []

    # Query with bus stations and ...
    overpass_query = '[out:json]; area["name"="München"]->.muc; (node["highway"="bus_stop"](area.muc););out geom;'
    op_api = overpy.Overpass()
    response = op_api.query(overpass_query)

    for node in response.nodes:
        dict_pd = {"geometry": (Point(node.lon, node.lat))}
        rows_list.append(dict_pd)

    osm_df = gpd.GeoDataFrame(rows_list, crs='epsg:4326')

    return osm_df


if __name__ == "__main__":
    get_single_track_gdf(1)
