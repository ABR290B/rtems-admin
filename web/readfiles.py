import json
import os
import re


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

"""
def parse_subject(subject):
    regex = r'Build (\w+): (FAILED|PASSED) (\w+ \d+/\w+) on (\w+)-(\w+)'
    match = re.match(regex, subject)
    if match:
        build_dict = {
            'Type': match.group(1),
            'Result': match.group(2),
            'OS': match.group(3).split()[0],
            'Arch': match.group(4),
            'Release': match.group(5)
        }
        return build_dict
    return None
"""
def parse_subject(subject):
    try:
        parts = subject.split(':')
        if len(parts) != 2:
            raise Exception('Invalid build subject: ' + subject)
        
        build_type = 'Build'
        host = parts[0][len(build_type):].strip()
        
        srs = parts[1].split()
        if len(srs) < 4:
            raise Exception('Invalid build subject: ' + subject)
        
        result = srs[0].strip()
        arch = srs[1].strip()
        os = srs[3].strip()
        
        build_dict = {
            'Type': build_type,
            'Result': result,
            'OS': os,
            'Arch': arch,
            'Release': ''
        }
        
        return build_dict
    except Exception as e:
        print(f'Error parsing subject: {subject}. {str(e)}')
        return None

def tool_build_parse(tool_build_results):
    tool_build_details = []

    for entry in tool_build_results:
        subject = entry.get('Subject', '')
        print("Subject:", subject)  # Print subject for debugging
        build_details = parse_subject(subject)
        print("Build Details:", build_details)  # Print build details for debugging
        if build_details:
            entry_copy = entry.copy()
            entry_copy['Details'] = build_details
            tool_build_details.append(entry_copy)

    return tool_build_details

script_path = os.path.abspath(__file__)
path_list = script_path.split(os.sep)
script_directory = path_list[0:len(path_list)-2]
rel_path = "data/2023-January.txt"
path = "/".join(script_directory) + "/" + rel_path

# Read data from the file
data = read_data_from_file(path)

# Categorize the data
tool_build_results, test_results, bsp_results = categorize_data(data)

# Parse tool build results
tool_build_details = tool_build_parse(tool_build_results)

# Save parsed data to JSON file
output_file_path = 'web/json-files/tool_build_details.json'
with open(output_file_path, 'w') as output_file:
    json.dump(tool_build_details, output_file, indent=4)
print("Tool Build Details saved to:", output_file_path)
