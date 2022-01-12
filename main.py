import sys
import os.path
import pandas as pd
from time import sleep
from utilities_scanner import file_scanner, track_detector
from utilities_analysis import track_importer, track_analysis, modality_analysis

print("Python version: ", sys.version)
print("Version info: ", sys.version_info)


loop_counter = 0
data_path = 'data'
data_mod_path = 'data_mod'
data_results = 'results'
file_all_data = 'all_data.csv'
file_all_tracks = 'all_tracks.csv'
file_all_modalities = 'all_modalities.csv'
file_type = '.pkl'
d_files = {}

while True:
    # #### Scanning for files and adding/removing them from dictionary #################################################
    d_files, loop_counter = file_scanner(loop_counter, data_path, data_mod_path, file_type, d_files)
    # #### TODO! File splitter/ Track splitter/ Analysis of the files whether they contain more than one track:
    #track_detector()
    # #### Import raw data and only use necessary data from that and save to modified csv data #########################
    track_importer(d_files)
    # #### all_tracks.csv: analysis of KPI's for each track ############################################################
    # check for files of alltracks:
    fp_alltracks = os.path.join(data_results, file_all_tracks)
    if os.path.exists(fp_alltracks):
        print('%s exists! Reading file...' % file_all_tracks)
        df_alltracks = pd.read_csv(fp_alltracks)
    else:
        print('%s does not exist! Creating new DF...' % file_all_tracks)
        df_alltracks = pd.DataFrame(columns=(
            'track_id', 'len_raw', 'len_dropnageo', 'len_dropcondup', 'time_start', 'time_stop', 'modality',
            'time_total_s', 'track_distance', 'total_avg_speed', 'mean_speed', 'median_speed', 'var_speed', 'p85_speed',
            'p85_speed_top3', 'p95_speed', 'max_speed', 'mean_accel', 'median_accel', 'var_accel', 'p85_accel',
            'p85_accel_top3', 'p95_accel', 'max_accel', 'stoprate'))
    # check for files of alldata:
    fp_alldata = os.path.join(data_results, file_all_data)
    if os.path.exists(fp_alldata):
        print('%s exists! Reading file...' % file_all_data)
        df_alldata = pd.read_csv(fp_alldata)
    else:
        print('%s does not exist! Creating new DF...' % file_all_data)
        df_alldata = pd.DataFrame(columns=('time', 'longitude', 'latitude', 'hdop', 'altitude', 'track_id', 'modality',
                                           'speed_gps', 'geometry', 'time_diff', 'distance_diff', 'speed_clc',
                                           'speed_ma', 'speed_rolling_median', 'speed_rolling_median_kph', 'accel_clc',
                                           'accel_rolling_median', 'time_id_hour', 'time_id_day_week',
                                           'time_id_day_month', 'time_id_kw', 'time_id_month', 'time_id_year'))
    # do the calculation stuff:
    for key in d_files:
        if key not in df_alltracks.track_id.tolist():
            d_dat, gdf_dat = track_analysis(key,
                                            d_files[key]['path_mod'],
                                            d_files[key]['path_save'],
                                            d_files[key]['path_cont'])
            # append the KPI to alltracks
            df_alltracks = df_alltracks.append(d_dat, ignore_index=True)
            # append the resampled data to alldata
            df_alldata = df_alldata.append(gdf_dat, ignore_index=True)
    df_alltracks = df_alltracks.set_index('track_id')
    df_alltracks.to_csv(fp_alltracks)
    df_alldata = df_alldata.set_index('time')
    df_alldata.to_csv(fp_alldata)
    # #### all_modalities.csv: analysis of KPI's for each modality #####################################################
    fp_allmodalities = os.path.join(data_results, file_all_modalities)
    df_allmodalities = modality_analysis(df_alltracks)
    df_allmodalities.to_csv(fp_allmodalities)
    #break
    sleep(5)
