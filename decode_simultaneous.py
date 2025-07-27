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
    Returns the decoded output as a string, or an empty string on error.
    """
    try:
        result = subprocess.run(['ITGDec', log_path], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error decoding {log_path}:\n{result.stderr}")
            return ""
        return result.stdout
    except Exception as e:
        print(f"Failed to decode {log_path}: {e}")
        return ""

def parse_decoded_output(output):
    """
    Parses the decoded output from ITGDec and extracts relevant metrics.
    Only processes lines after the 'TOTAL RESULTS' section.
    Returns a dictionary with the extracted data.
    """
    lines = output.splitlines()
    data = {}
    in_total_section = False

    for line in lines:
        # Start parsing after 'TOTAL RESULTS'
        if "TOTAL RESULTS" in line:
            in_total_section = True
            continue

        if in_total_section and "=" in line:
            key, value = line.split("=", 1)
            key = key.strip().lower()
            value = value.strip().split(" ")[0]  # get numeric value

            # Map output keys to dictionary fields
            if "total time" in key:
                data['total_time'] = value
            elif "total packets" in key:
                data['total_packets'] = value
            elif "minimum delay" in key:
                data['min_delay'] = value
            elif "maximum delay" in key:
                data['max_delay'] = value
            elif "average delay" in key:
                data['avg_delay'] = value
            elif "average jitter" in key:
                data['jitter'] = value
            elif "delay standard deviation" in key:
                data['delay_std_dev'] = value
            elif "bytes received" in key:
                data['total_bytes'] = value
            elif "average bitrate" in key:
                data['avg_bitrate'] = value
            elif "average packet rate" in key:
                data['packet_rate'] = value
            elif "packets dropped" in key:
                data['packet_loss'] = value
            elif "average loss-burst size" in key:
                data['loss_burst'] = value
            elif "error lines" in key:
                data['error_lines'] = value

    return data

def walk_new_script_logs(ip_version):
    """
    Walks through the log directory for the given IP version (IPV4 or IPV6),
    decodes each 'recv.log' file, parses the output, and collects the results in a list.
    Adds metadata such as IP version, protocol, packet size, and log file name.
    """
    rows = []
    base_dir = os.path.join(LOG_ROOT, ip_version.upper())
    if not os.path.isdir(base_dir):
        return rows

    for protocol in os.listdir(base_dir):
        protocol_dir = os.path.join(base_dir, protocol)
        if not os.path.isdir(protocol_dir):
            continue

        for size in os.listdir(protocol_dir):
            size_dir = os.path.join(protocol_dir, size)
            recv_log = os.path.join(size_dir, "recv.log")

            if os.path.isfile(recv_log):
                print(f"Decoding {recv_log}")
                decoded = decode_log_file(recv_log)
                parsed = parse_decoded_output(decoded)
                if parsed:
                    parsed.update({
                        "ip_version": ip_version.upper(),
                        "protocol": protocol.upper(),
                        "packet_size": size,
                        "log_file": "recv.log"
                    })
                    rows.append(parsed)
    return rows

def save_to_csv(data, filename):
    """
    Saves the list of dictionaries to a CSV file with specified columns.
    """
    if not data:
        print(f"No data to write to {filename}")
        return
    keys = [
        'ip_version', 'protocol', 'packet_size', 'log_file',
        'total_time', 'total_packets', 'min_delay', 'max_delay', 'avg_delay',
        'jitter', 'delay_std_dev', 'total_bytes', 'avg_bitrate',
        'packet_rate', 'packet_loss', 'loss_burst', 'error_lines'
    ]
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

def main():
    """
    Main function to process IPv4 and IPv6 logs and save results to CSV files.
    """
    ipv4_data = walk_new_script_logs("IPV4")
    ipv6_data = walk_new_script_logs("IPV6")

    save_to_csv(ipv4_data, OUTPUT_CSV_V4)
    save_to_csv(ipv6_data, OUTPUT_CSV_V6)

    print(f"Decoded logs saved to:\n - {OUTPUT_CSV_V4}\n - {OUTPUT_CSV_V6}")

if __name__ == "__main__":
    main()
