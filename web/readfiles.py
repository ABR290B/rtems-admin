import json
import os


def categorize_data(data):
    tool_build_results = []
    test_results = []
    bsp_results = []

    for entry in data:
        subject = entry.get('Subject', '')
        if subject.startswith('Build'):
            tool_build_results.append(entry)
        elif subject.startswith('[rtems-test]'):
            test_results.append(entry)
        elif subject.startswith('[rtems-bsp-builder]'):
            bsp_results.append(entry)

    return tool_build_results, test_results, bsp_results


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
                if current_entry:
                    if current_entry.get('Subject', '').startswith('Build'):
                        data.append(current_entry)
                current_entry = {}

    if current_entry:
        if current_entry.get('Subject', '').startswith('Build'):
            data.append(current_entry)

    return data

script_path = os.path.abspath(__file__)
path_list = script_path.split(os.sep)
script_directory = path_list[0:len(path_list)-2]
rel_path = "data/2023-January.txt"
path = "/".join(script_directory) + "/" + rel_path

# Read data from the file
data = read_data_from_file(path)

# Categorize the data
tool_build_results, test_results, bsp_results = categorize_data(data)


# Save categorized data to JSON files
output_file_path = 'web/json-files/tool_build_results.json'
with open(output_file_path, 'w') as output_file:
    json.dump(tool_build_results, output_file, indent=4)
print("Tool Build Results saved to:", output_file_path)

output_file_path = 'web/json-files/test_results.json'
with open(output_file_path, 'w') as output_file:
    json.dump(test_results, output_file, indent=4)
print("Test Results saved to:", output_file_path)

output_file_path = 'web/json-files/bsp_results.json'
with open(output_file_path, 'w') as output_file:
    json.dump(bsp_results, output_file, indent=4)
print("BSP Results saved to:", output_file_path)
