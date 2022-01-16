import os.path
import pandas as pd
from datetime import datetime, timedelta


def file_scanner(loop_counter, data_path, data_mod_path, file_type, d_files):
    print('[Loop %i, Time: %s] Scanning for files:' % (loop_counter, datetime.now().strftime("%H:%M:%S")))
    list_found_files = []

    # Walk through dir and add new files to dictionary
    for dirpath, dirnames, filenames in os.walk(data_path):
        for filename in [f for f in filenames if f.endswith(file_type)]:
            if '.pkl' in filename:  # --> import with FTM data:
                file_id = filename.replace('.pkl' , '')
            elif '.csv' in filename:  # --> import with London data:
                file_id = filename.replace('.csv', '')
            else:
                raise FileNotFoundError
            list_found_files.append(file_id)
            if file_id in d_files:
                pass
            else:
                d_files[file_id] = {'filename': filename,
                                    'path': os.path.join(dirpath, filename),
                                    'path_mod': os.path.join(data_mod_path, file_id + '_mod' + '.csv'),
                                    'path_save': os.path.join(data_mod_path, file_id + '_save' + '.csv'),
                                    'path_cont': os.path.join(data_mod_path, file_id + '_cont' + '.csv'),
                                    'modified': False}
                print('New file found: %s added!' % filename)

    # Remove files which have been removed from directory
    for key in list(d_files):
        if key not in list_found_files:
            print('Missing file: %s removed!' % key)
            d_files.pop(key, None)
    list_found_files.clear()
    loop_counter += 1

    return d_files, loop_counter


def track_detector(d_allfiles):
    timegaptresh = 0.9
    list_multiple = []
    for key_file in d_allfiles:
        datafile_path = d_allfiles[key_file]['path']
        if '.pkl' in datafile_path:  # --> import with FTM data:
            datafile = pd.DataFrame(pd.read_pickle(datafile_path)[4])  # --> for FTM data if containing a List
            #datafile = pd.DataFrame(pd.read_pickle(datafile_path))  # --> for FTM data if NOT containing a List
        elif '.csv' in datafile_path:  # --> import with London data:
            datafile = pd.DataFrame(pd.read_csv(datafile_path))
        else:
            raise FileNotFoundError
        datafile['time'] = pd.to_datetime(datafile['time'])
        datafile['timegap'] = (datafile.time - datafile.time.shift(1)).dt.total_seconds()
        datafile.loc[datafile.iloc[0].name, 'timegap'] = 10  # timedelta(seconds=10)  --> to detect first track 10s!
        tracks_found_index = datafile[datafile.timegap > timegaptresh].index.tolist()
        length_tracks_found = len(tracks_found_index)
        datafile = datafile.set_index('time')
        if length_tracks_found > 1:
            list_multiple.append(key_file)
            print("Found multiple tracks (%i) in file %s." % (length_tracks_found, datafile_path))
            for m in range(0, length_tracks_found):  # for all found timegaps
                start_index = tracks_found_index[m]
                if m == length_tracks_found-1:
                    end_index = len(datafile)  # for the last slice, get last index
                else:
                    end_index = tracks_found_index[m+1]
                new_file_path = datafile_path.replace('.', ('_' + str(m) + '.'))
                datafile.iloc[start_index:end_index].to_csv(new_file_path)
                print('New segment from index %i to %i: %s. ' % (start_index, end_index, new_file_path))
    # Check if there were files with multiple tracks. Remove them, if true. Otherwise get checked again in next loop.
    if len(list_multiple) != 0:
        for item_key in list_multiple:
            os.remove(d_allfiles[item_key]['path'])  # deletes the original file
            d_allfiles.pop(item_key)  # remove the key from d_files, actually not rly necessary
            print("Removed original key and file: %s." % str(item_key))
    else:
        print('No files with multiple tracks have been found.')
