import json


class LogUtil:
    logfile = 'queries.log'

    @staticmethod
    def write_to_queries_log(message):
        LogUtil.write_dict_to_file(LogUtil.logfile, message)


    @staticmethod
    def write_dict_to_file(file_path, message):
        # Open file in append mode, which creates the file if it doesn't exist
        with open(file_path, 'a') as file:
            # Write the dictionary to a new line
            file.write(message + '\n')