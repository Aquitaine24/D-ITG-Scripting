import os
import subprocess
import csv

# Root directory containing log files
LOG_ROOT = "/home/client-2/Desktop/LOGS"
# Output CSV filenames for IPv4 and IPv6 results
OUTPUT_CSV_V4 = "ditg_ipv4_results.csv"
OUTPUT_CSV_V6 = "ditg_ipv6_results.csv"

def decode_log_file(log_path):
    """
    Runs the ITGDec command-line tool to decode a log file.
    Returns the decoded output as a string.
    """
    try:
        result = subprocess.run(['ITGDec', log_path], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        print(f"Failed to decode {log_path}: {e}")
        return ""

def parse_decoded_output(output):
    """
    Parses the decoded output from ITGDec and extracts relevant metrics.
    Returns a dictionary with the extracted data.
    """
    lines = output.splitlines()
    data = {}

    for line in lines:
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip().lower()
        value = value.strip().split(" ")[0]  # get numeric value

        # Map output keys to dictionary fields
        if "total time" in key:
            data['total_time'] = value
        elif "total packets" in key:
            data['total_packets'] = value
        elif "average delay" in key and "standard" not in key:
            data['avg_delay'] = value
        elif "average jitter" in key:
            data['jitter'] = value
        elif "bytes received" in key:
            data['total_bytes'] = value
        elif "average bitrate" in key:
            data['avg_bitrate'] = value
        elif "packets dropped" in key:
            data['packet_loss'] = value
        elif "average packet rate" in key:
            data['packet_rate'] = value

    return data

def walk_logs_and_parse(root, is_ipv6=False):
    """
    Walks through the log directory, decodes each log file,
    parses the output, and collects the results in a list.
    """
    rows = []
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if filename.startswith("run-") and filename.endswith(".log"):
                full_path = os.path.join(dirpath, filename)
                print(f"Decoding {full_path}")
                decoded = decode_log_file(full_path)
                parsed = parse_decoded_output(decoded)
                if parsed:
                    # Extract metadata from the file path
                    parts = full_path.split(os.sep)
                    try:
                        protocol = parts[-3]
                        pkt_size = parts[-2]
                        run = parts[-1].replace("run-", "").replace(".log", "")
                        parsed.update({
                            "protocol": protocol,
                            "packet_size": pkt_size,
                            "run_number": run,
                        })
                        rows.append(parsed)
                    except IndexError:
                        print(f"Unexpected path structure for: {full_path}")
    return rows

def save_to_csv(data, filename):
    """
    Saves the list of dictionaries to a CSV file with specified columns.
    """
    if not data:
        print(f"No data to write to {filename}")
        return
    keys = [
        'protocol', 'packet_size', 'run_number',
        'total_time', 'total_packets', 'avg_delay',
        'jitter', 'total_bytes', 'avg_bitrate',
        'packet_rate', 'packet_loss'
    ]
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

def main():
    """
    Main function to process IPv4 and IPv6 logs and save results to CSV files.
    """
    ipv4_data = walk_logs_and_parse(os.path.join(LOG_ROOT, "IPV4"))
    ipv6_data = walk_logs_and_parse(os.path.join(LOG_ROOT, "IPV6"), is_ipv6=True)

    save_to_csv(ipv4_data, OUTPUT_CSV_V4)
    save_to_csv(ipv6_data, OUTPUT_CSV_V6)

    print(f"Decoded data saved to {OUTPUT_CSV_V4} and {OUTPUT_CSV_V6}")

if __name__ == "__main__":
    main()
