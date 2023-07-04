import json
import os



def read_data_from_file(file_path):
    data = []

    with open(file_path, 'r') as file:
        current_entry = {}
        for line in file:
            line = line.strip()
            if line.startswith(('From', 'Date', 'Subject', 'Message-ID', 'Host')):
                if ':' in line:
                    key, value = line.split(':', 1)
                    current_entry[key.strip()] = value.strip()
                    if key.strip() == 'Host':
                        data.append(current_entry)
                        current_entry = {}
            elif line.startswith('Build Set:') or line.startswith('config:'):
                if current_entry and current_entry.get('Subject', '').startswith('Build'):
                    if 'From ' not in current_entry:
                        data.append(current_entry)
                current_entry = {}

    if current_entry and current_entry.get('Subject', '').startswith('Build'):
        if 'From ' not in current_entry:
            data.append(current_entry)

    return data

script_path = os.path.abspath(__file__)
path_list = script_path.split(os.sep)
script_directory = path_list[0:len(path_list)-2]
rel_path = "data/2023-January.txt"
path = "/".join(script_directory) + "/" + rel_path

# Usage

data = read_data_from_file(path)

# Save data to JSON file
output_file_path = 'web/output.json'  # Replace with the desired output file path
with open(output_file_path, 'w') as output_file:
    json.dump(data, output_file, indent=4)

print("Data saved to:", output_file_path)
