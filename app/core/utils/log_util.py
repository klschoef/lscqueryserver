import json
import time  # Importiere die Time-Bibliothek

class LogUtil:
    logfile = 'queries.log'

    @staticmethod
    def write_to_queries_log(message):
        LogUtil.write_dict_to_file(LogUtil.logfile, message)

    @staticmethod
    def write_dict_to_file(file_path, message):
        # Holen des aktuellen Unix Timestamp
        timestamp = int(time.time())
        # Open file in append mode, which creates the file if it doesn't exist
        with open(file_path, 'a') as file:
            # Füge den Timestamp vor dem Nachrichteninhalt ein
            file.write(f"{timestamp}: {message}\n")
