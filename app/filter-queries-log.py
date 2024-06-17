import argparse
import os
import time

def filter_logs_by_timestamp(input_file, output_file, start_timestamp, end_timestamp):
    if not os.path.exists(input_file):
        print(f"Error: The input file path '{input_file}' does not exist.")
        return

    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            for line in infile:
                if line.strip():  # Make sure line is not empty
                    timestamp, json_data = line.split(':', 1)
                    if start_timestamp <= int(timestamp.strip()) <= end_timestamp:
                        outfile.write(line)
        print(f"Filtered logs saved to '{output_file}'")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description='Filter log entries by timestamp range.')
    parser.add_argument('start_timestamp', type=int, help='Start timestamp (inclusive).')
    parser.add_argument('end_timestamp', type=int, help='End timestamp (inclusive).')
    parser.add_argument('-i', '--input', type=str, default='./queries.log', help='Input file path (default: ./queries.log)')
    parser.add_argument('-o', '--output', type=str, default=f'queries.filtered.{int(time.time())}.log', help='Output file path (default: queries.log.filtered.[current_timestamp])')

    args = parser.parse_args()

    filter_logs_by_timestamp(args.input, args.output, args.start_timestamp, args.end_timestamp)

if __name__ == "__main__":
    main()
