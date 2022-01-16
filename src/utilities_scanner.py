import os.path
from datetime import datetime


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


def track_detector():
    pass  # test
    #all_data['timegap'] = (all_data.time - all_data.time.shift(1,fill_value = 0)).dt.total_seconds()
    #print(len(all_data[all_data.timegap > 1].index.tolist()))
    #all_data[all_data.timegap > 1]
