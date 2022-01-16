import pandas as pd
import geopandas as gpd
import numpy as np
from datetime import datetime, timedelta
from helpers import calculate_distance_points
import classifier as clf
import warnings
from shapely.errors import ShapelyDeprecationWarning


def track_importer(files):
    for key in files:
        fp = files[key]['path']
        if '.pkl' in fp:  # --> import with FTM data:
            vehicle_id, track_id, modality, modality_precision, dats = pd.read_pickle(fp)
            # add Vehicle_ID and track_id and modality as dataframe columns
            dats['Vehicle_ID'] = vehicle_id
            dats['track_id'] = track_id
            # if modality is None and 'Logger' in fp:
            if modality is None:
                modality = 'car'
            dats['modality'] = modality
            dats['modality_prec'] = modality_precision
            dats = dats.rename(columns={'latitude': 'longitude', 'longitude': 'latitude',  # bcuz mixed in data
                                        'speed': 'speed_gps'})
            dats = dats[['time', 'longitude', 'latitude', 'hdop', 'altitude', 'track_id', 'modality', 'speed_gps']]
        elif '.csv' in fp:  # --> import with London data:
            dats = pd.read_csv(fp)
            dats = dats.rename(columns={'track': 'track_id'})
            dats = dats[['time', 'longitude', 'latitude', 'altitude', 'track_id', 'modality']]
        # add source as dataframe columns
        if 'Smartphone' in fp:
            s = 'Smartphone'
        elif 'Logger' in fp:
            s = 'Logger'
        else:
            s = 'unknown'
        dats['source'] = s
        dats = dats.set_index('time')
        dats.to_csv(files[key]['path_mod'])


def track_analysis(track_id, filepath, filepath_save, filepath_cont):
    pd_df = pd.read_csv(filepath)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)
        gdf_track_data = gpd.GeoDataFrame(pd_df, crs="EPSG:4326",
                                          geometry=gpd.points_from_xy(pd_df.longitude, pd_df.latitude))
    gdf_track_data['time'] = pd.to_datetime(gdf_track_data['time'])
    gdf_track_data = gdf_track_data.set_index('time', drop=False)
    modality = gdf_track_data.modality.unique()[0]
    len_raw = len(gdf_track_data)
    time_start = gdf_track_data.time.iloc[0]
    time_stop = gdf_track_data.time.iloc[-1]
    # ######### FILTER #################################################################################################
    # drop all rows with no geometrical data
    gdf_track_data = gdf_track_data.dropna(subset=['latitude'])
    len_dropnageo = len(gdf_track_data)
    # drop all rows which are consecutive duplicates
    if len(gdf_track_data.geometry.unique()) == 1:
        gdf_track_data = gdf_track_data.iloc[[0, -1]]
    else:
        gdf_track_data = gdf_track_data.loc[gdf_track_data.geometry.shift(1) != gdf_track_data.geometry]
    len_dropcondup = len(gdf_track_data)
    # ######### CLC on data ############################################################################################
    window_ma = 15
    window_rw = 5
    gdf_track_data['time_diff'] = gdf_track_data.time - gdf_track_data.time.shift(1)
    gdf_track_data.loc[gdf_track_data.iloc[0].name, 'time_diff'] = timedelta(seconds=0)
    gdf_track_data['distance_diff'] = calculate_distance_points(gdf_track_data.geometry)
    gdf_track_data['speed_clc'] = (gdf_track_data.distance_diff / (gdf_track_data.time_diff.dt.total_seconds()))
    gdf_track_data.loc[gdf_track_data.iloc[0].name, 'speed_clc'] = 0.0
    if len_dropcondup <= window_ma:
        gdf_track_data['speed_ma'] = np.empty(len_dropcondup)
    else:
        weights = np.repeat(1.0, window_ma) / window_ma
        gdf_track_data['speed_ma'] = np.convolve(gdf_track_data.speed_clc, weights, 'same')
    gdf_track_data['speed_rolling_median'] = gdf_track_data.speed_ma.rolling(window_rw, center=True).median()
    gdf_track_data['speed_rolling_median_kph'] = gdf_track_data.speed_rolling_median * 3.6
    gdf_track_data['accel_clc'] = (gdf_track_data.speed_rolling_median - gdf_track_data.speed_rolling_median.shift(
        1)) / (gdf_track_data.time_diff.dt.total_seconds())
    gdf_track_data['accel_rolling_median'] = gdf_track_data.accel_clc.rolling(window_rw, center=True).median()
    gdf_track_data = gdf_track_data.fillna(
        value={"accel_clc": 0, "speed_rolling_median": 0, "speed_rolling_median_kph": 0, "accel_rolling_median": 0})
    # ######### CLC for KPI ############################################################################################
    stoprate_v_treshold = 1  # in m/s
    time_total_s = (time_stop - time_start).total_seconds()
    track_distance = gdf_track_data.distance_diff.sum()
    total_avg_speed = track_distance / time_total_s
    mean_speed = gdf_track_data.speed_rolling_median.mean()
    median_speed = gdf_track_data.speed_rolling_median.median()
    var_speed = gdf_track_data.speed_rolling_median.var()
    p85_speed = gdf_track_data.speed_rolling_median.quantile(q=0.85)
    p85_speed_top3 = str(gdf_track_data[gdf_track_data.speed_rolling_median < p85_speed].nlargest(3,
                                                                                                  'speed_rolling_median').speed_rolling_median.tolist())
    p95_speed = gdf_track_data.speed_rolling_median.quantile(q=0.95)
    max_speed = gdf_track_data.speed_rolling_median.max()
    mean_accel = gdf_track_data.accel_rolling_median.mean()
    median_accel = gdf_track_data.accel_rolling_median.median()
    var_accel = gdf_track_data.accel_rolling_median.var()
    p85_accel = gdf_track_data.accel_rolling_median.quantile(q=0.85)
    p85_accel_top3 = str(gdf_track_data[gdf_track_data.accel_rolling_median < p85_accel].nlargest(3,
                                                                                                  'accel_rolling_median').accel_rolling_median.tolist())
    p95_accel = gdf_track_data.accel_rolling_median.quantile(q=0.95)
    max_accel = gdf_track_data.accel_rolling_median.max()
    stoprate = len(gdf_track_data[gdf_track_data.speed_rolling_median < stoprate_v_treshold]) / len_dropcondup
    # ######### additional info ########################################################################################
    gdf_track_data['time_id_hour'] = gdf_track_data.time.dt.hour  # 0 to 23
    gdf_track_data['time_id_day_week'] = gdf_track_data.time.dt.dayofweek  # number of day in week, 0 (Mon) to 6 (Sun)
    gdf_track_data['time_id_day_month'] = gdf_track_data.time.dt.day  # number of day in respect to month
    gdf_track_data['time_id_kw'] = gdf_track_data.time.dt.isocalendar().week  # calendar week (0 to 53)
    gdf_track_data['time_id_month'] = gdf_track_data.time.dt.month  # 1 (Jan) to 12 (Dec)
    gdf_track_data['time_id_year'] = gdf_track_data.time.dt.year  # year

    kpi_dict = {'track_id': track_id,
                'len_raw': len_raw,
                'len_dropnageo': len_dropnageo,
                'len_dropcondup': len_dropcondup,
                'time_start': time_start,
                'time_stop': time_stop,
                'time_total_s': time_total_s,
                'track_distance': track_distance,
                'total_avg_speed': total_avg_speed,
                'mean_speed': mean_speed,
                'median_speed': median_speed,
                'var_speed': var_speed,
                'p85_speed': p85_speed,
                'p85_speed_top3': p85_speed_top3,
                'p95_speed': p95_speed,
                'max_speed': max_speed,
                'mean_accel': mean_accel,
                'median_accel': median_accel,
                'var_accel': var_accel,
                'p85_accel': p85_accel,
                'p85_accel_top3': p85_accel_top3,
                'p95_accel': p95_accel,
                'max_accel': max_accel,
                'stoprate': stoprate
                }

    # Modality detection Christoph
    predicted_modality = clf.predict(kpi_dict=kpi_dict)
    kpi_dict["modality"] = predicted_modality
    gdf_track_data['modality'] = predicted_modality

    # ######### Resampling #############################################################################################
    time_range = pd.date_range(time_start, time_stop, freq='5s')
    gdf_track_data_cont = gpd.GeoDataFrame({}, index=time_range)
    gdf_track_data_cont = pd.merge_asof(gdf_track_data_cont, gdf_track_data.sort_index(),
                                        left_index=True, right_index=True)
    # ######### Save ###################################################################################################
    gdf_track_data.to_csv(filepath_save)
    gdf_track_data_cont.to_csv(filepath_cont)
    # ######### Return #################################################################################################
    return kpi_dict, gdf_track_data_cont


def modality_analysis(dfa):
    dfm = pd.DataFrame(None, index=['car', 'pedestrian', 'still'])
    dfm['no_tracks'] = [sum(dfa.modality == 'car'),
                        sum(dfa.modality == 'pedestrian'),
                        sum(dfa.modality == 'still')]
    total_time_s_mod_car = dfa[dfa.modality == 'car'].time_total_s.sum()
    total_time_s_mod_ped = dfa[dfa.modality == 'pedestrian'].time_total_s.sum()
    total_time_s_mod_sti = dfa[dfa.modality == 'still'].time_total_s.sum()
    dfm['total_time_s'] = [total_time_s_mod_car,
                           total_time_s_mod_ped,
                           total_time_s_mod_sti]
    dfm['total_time_td'] = [timedelta(seconds=total_time_s_mod_car),
                            timedelta(seconds=total_time_s_mod_ped),
                            timedelta(seconds=total_time_s_mod_sti)]
    dfm['total_time_hms'] = ['%.2d:%.2d:%.2d' % (
    int(total_time_s_mod_car / 3600), int((total_time_s_mod_car / 60) % 60), round(total_time_s_mod_car % 60)),
                             '%.2d:%.2d:%.2d' % (
                             int(total_time_s_mod_ped / 3600), int((total_time_s_mod_ped / 60) % 60),
                             round(total_time_s_mod_ped % 60)),
                             '%.2d:%.2d:%.2d' % (
                             int(total_time_s_mod_sti / 3600), int((total_time_s_mod_sti / 60) % 60),
                             round(total_time_s_mod_sti % 60))]
    dfm['total_distance_m'] = [dfa[dfa.modality == 'car'].track_distance.sum(),
                               dfa[dfa.modality == 'pedestrian'].track_distance.sum(),
                               dfa[dfa.modality == 'still'].track_distance.sum()]
    dfm['total_distance_km'] = [dfa[dfa.modality == 'car'].track_distance.sum() / 1000,
                                dfa[dfa.modality == 'pedestrian'].track_distance.sum() / 1000,
                                dfa[dfa.modality == 'still'].track_distance.sum() / 1000]
    time_s_mod_car = dfa[dfa.modality == 'car'].time_total_s.mean()
    time_s_mod_ped = dfa[dfa.modality == 'pedestrian'].time_total_s.mean()
    time_s_mod_sti = dfa[dfa.modality == 'still'].time_total_s.mean()
    dfm['mean_time_s_per_track'] = [time_s_mod_car,
                                    time_s_mod_ped,
                                    time_s_mod_sti]
    dfm['mean_time_td_per_track'] = [timedelta(seconds=time_s_mod_car),
                                     timedelta(seconds=time_s_mod_ped),
                                     timedelta(seconds=time_s_mod_sti)]
    dfm['mean_time_hms_per_track'] = [
        '%.2d:%.2d:%.2d' % (int(time_s_mod_car / 3600), int((time_s_mod_car / 60) % 60), round(time_s_mod_car % 60)),
        '%.2d:%.2d:%.2d' % (int(time_s_mod_ped / 3600), int((time_s_mod_ped / 60) % 60), round(time_s_mod_ped % 60)),
        '%.2d:%.2d:%.2d' % (int(time_s_mod_sti / 3600), int((time_s_mod_sti / 60) % 60), round(time_s_mod_sti % 60))]
    dfm['total_avg_speed_per_track_mps'] = [dfa[dfa.modality == 'car'].total_avg_speed.mean(),
                                            dfa[dfa.modality == 'pedestrian'].total_avg_speed.mean(),
                                            dfa[dfa.modality == 'still'].total_avg_speed.mean()]
    dfm['total_avg_speed_per_track_kph'] = [dfa[dfa.modality == 'car'].total_avg_speed.mean() * 3.6,
                                            dfa[dfa.modality == 'pedestrian'].total_avg_speed.mean() * 3.6,
                                            dfa[dfa.modality == 'still'].total_avg_speed.mean() * 3.6]
    dfm['total_mean_speed_per_track_mps'] = [dfa[dfa.modality == 'car'].mean_speed.mean(),
                                             dfa[dfa.modality == 'pedestrian'].mean_speed.mean(),
                                             dfa[dfa.modality == 'still'].mean_speed.mean()]
    dfm['total_mean_speed_per_track_kph'] = [dfa[dfa.modality == 'car'].mean_speed.mean() * 3.6,
                                             dfa[dfa.modality == 'pedestrian'].mean_speed.mean() * 3.6,
                                             dfa[dfa.modality == 'still'].mean_speed.mean() * 3.6]
    dfm['mean_dist_per_track_m'] = [dfa[dfa.modality == 'car'].track_distance.mean(),
                                    dfa[dfa.modality == 'pedestrian'].track_distance.mean(),
                                    dfa[dfa.modality == 'still'].track_distance.mean()]
    dfm['mean_dist_per_track_km'] = [dfa[dfa.modality == 'car'].track_distance.mean() / 1000,
                                     dfa[dfa.modality == 'pedestrian'].track_distance.mean() / 1000,
                                     dfa[dfa.modality == 'still'].track_distance.mean() / 1000]
    return dfm
