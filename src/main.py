import helpers as h
import os.path
import pandas as pd
from time import sleep
from utilities_scanner import file_scanner, track_detector
from utilities_analysis import track_importer, track_analysis, modality_analysis


def main(do_loop: bool):

    print('---- Main script started ----')
    loop_counter = 1
    d_files = {}

    while True:

        # Scanning for files and adding/removing them from dictionary
        d_files, loop_counter = file_scanner(loop_counter, h.DATA_PATH, h.DATA_MOD_PATH, h.FILE_TYPE, d_files)

        # #### File and track splitter / Analysis of the files whether they contain more than one track. Rescan!!
        track_detector(d_files)
        d_files, loop_counter = file_scanner(loop_counter-1, data_path, data_mod_path, file_type, d_files)

        # Import raw data and only use necessary data from that and save to modified csv data.
        track_importer(d_files)

        # Read all_tracks.csv as pandas dataframe file if existing. Else create file.
        if os.path.exists(h.FILE_ALL_TRACKS):
            print('%s exists! Reading file...' % h.FILE_ALL_TRACKS.name)
            df_all_tracks = pd.read_csv(h.FILE_ALL_TRACKS)
        else:
            print('%s does not exist! Creating new DF...' % h.FILE_ALL_TRACKS.name)
            df_all_tracks = pd.DataFrame(columns=(
                'track_id', 'len_raw', 'len_dropnageo', 'len_dropcondup', 'time_start', 'time_stop', 'modality',
                'time_total_s', 'track_distance', 'total_avg_speed', 'mean_speed', 'median_speed', 'var_speed', 'p85_speed',
                'p85_speed_top3', 'p95_speed', 'max_speed', 'mean_accel', 'median_accel', 'var_accel', 'p85_accel',
                'p85_accel_top3', 'p95_accel', 'max_accel', 'stoprate'))

        # Read all_data.csv as pandas dataframe file if existing. Else create file.
        if os.path.exists(h.FILE_ALL_DATA):
            print('%s exists! Reading file...' % h.FILE_ALL_DATA.name)
            df_all_data = pd.read_csv(h.FILE_ALL_DATA)
        else:
            print('%s does not exist! Creating new DF...' % h.FILE_ALL_DATA.name)
            df_all_data = pd.DataFrame(columns=('time', 'longitude', 'latitude', 'hdop', 'altitude', 'track_id', 'modality',
                                               'speed_gps', 'geometry', 'time_diff', 'distance_diff', 'speed_clc',
                                               'speed_ma', 'speed_rolling_median', 'speed_rolling_median_kph', 'accel_clc',
                                               'accel_rolling_median', 'time_id_hour', 'time_id_day_week',
                                               'time_id_day_month', 'time_id_kw', 'time_id_month', 'time_id_year'))

        # do the calculation stuff:
        for key in d_files:
            if key not in df_all_tracks.track_id.tolist():
                d_dat, gdf_dat = track_analysis(key,
                                                d_files[key]['path_mod'],
                                                d_files[key]['path_save'],
                                                d_files[key]['path_cont'])
                # append the KPI to all_tracks
                df_all_tracks = df_all_tracks.append(d_dat, ignore_index=True)
                # append the resampled data to all_data
                df_all_data = df_all_data.append(gdf_dat, ignore_index=True)
        df_all_tracks = df_all_tracks.set_index('track_id')
        df_all_tracks.to_csv(h.FILE_ALL_TRACKS)
        df_all_data = df_all_data.set_index('time')
        df_all_data.to_csv(h.FILE_ALL_DATA)

        # all_modalities.csv: analysis of KPI's for each modality
        if len(d_files) != 0:
            df_all_modalities = modality_analysis(df_all_tracks)
            df_all_modalities.to_csv(h.FILE_ALL_MODALITIES)

        if not do_loop:
            break
        sleep(10)


if __name__ == "__main__":
    main(do_loop=False)
