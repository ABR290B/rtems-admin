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
        #print("Subject:", subject)  # Print subject for debugging
        build_details = parse_subject(subject)
        #print("Build Details:", build_details)  # Print build details for debugging
        if build_details:
            entry_copy = entry.copy()
            entry_copy['Details'] = build_details
            tool_build_details.append(entry_copy)

    return tool_build_details

def visualise_tool_results(tool_build_details):
    # Sort the tool_build_details by date
    tool_build_details = sorted(tool_build_details, key=lambda entry: entry['Date'])

    host_summary = []

    # Get unique hosts
    hosts = set(entry['Host'] for entry in tool_build_details)

    # Calculate summary for each host
    for host in hosts:
        host_entries = [entry for entry in tool_build_details if entry['Host'] == host]
        total_entries = len(host_entries)
        passed_entries = len([entry for entry in host_entries if entry['Details']['Result'] == 'PASSED'])
        failed_entries = len([entry for entry in host_entries if entry['Details']['Result'] == 'FAILED'])
        failed_archs = [entry['Details']['Arch'] for entry in host_entries if entry['Details']['Result'] == 'FAILED']

        # Find the last occurrence of PASSED result for each arch
        last_passed_entries = {}
        for entry in reversed(host_entries):
            if entry['Details']['Result'] == 'PASSED':
                arch = entry['Details']['Arch']
                if arch in failed_archs and arch not in last_passed_entries:
                    last_passed_entries[arch] = entry

        # Create Fixed and Unfixed lists
        fixed_archs = [entry['Details']['Arch'] for entry in last_passed_entries.values()]
        unfixed_archs = list(set(failed_archs) - set(fixed_archs))

        host_summary.append({
            'Host': host,
            'TotalEntries': total_entries,
            'PassedEntries': passed_entries,
            'FailedEntries': failed_entries,
            'FailedArchs': failed_archs,
            'Fixed': fixed_archs,
            'Unfixed': unfixed_archs
        })

    return host_summary

def Monthly_Build_Summary(tool_build_details):
    month_build_summary = []

    for entry in tool_build_details:
        date = entry['Date'].split(',')[1].strip()
        os = entry['Details']['OS']
        arch = entry['Details']['Arch']
        release = ""
        if "/" in arch:
            release, arch = arch.split("/", 1)

        release = release.strip()
        arch = arch.strip().split("/")[0]
        result = entry['Details']['Result']

        build_summary = {
            'Date': date,
            'OS': os,
            'Arch': arch,
            'Release': release,
            'Result': result
        }

        month_build_summary.append(build_summary)

    return month_build_summary


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
host_tool = visualise_tool_results(tool_build_details)
print(host_tool)
output_file_path = 'web/json-files/host-tool.json'
with open(output_file_path, 'w') as output_file:
    json.dump(host_tool, output_file, indent=4)

month_build_summary_list = Monthly_Build_Summary(tool_build_details)

output_file_path = 'web/visualization/public/month_build_summary.json'
with open(output_file_path, 'w') as output_file:
    json.dump(month_build_summary_list, output_file, indent=4)
