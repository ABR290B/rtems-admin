import json
import os
import re
from download import months, download_archive  # Import the necessary functions from download.py


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


def test_parse(test_results, file_path):
    test_details = []

    for entry in test_results:
        message_id = entry.get('Message-ID', '')
        #print("Message-ID:", message_id)  # Print MessageID for debugging
        #print ("File Path:", file_path)  #File path for debugging
        test_data = test_report(message_id, file_path)
        if test_data:
            test_details.append(test_data)
    
    return test_details

def test_report(message_id, file_path):
    try:
        with open(file_path, 'r') as archive_file:
            archive_data = archive_file.read()

            # Locate the start index of the message ID value
            message_id_idx = archive_data.find(message_id)
            if message_id_idx == -1:
                print(f"Message-ID '{message_id}' not found in the archive.")
                return None
            
            # Locate the start index of the message section
            start_idx = archive_data.rfind("Message-ID:", 0, message_id_idx)

            # Locate the end index of the message section
            end_idx = archive_data.find("From:", start_idx)
            if end_idx == -1:
                end_idx = len(archive_data)

            # Extract the content of the located section
            message_content = archive_data[start_idx:end_idx].strip()

            # Split the content into lines
            lines = message_content.split('\n')
            #print("Message content lines:")
            #for line in lines:
                #print(line)
            # Find the index of the "Summary" and "Failures" sections
            summary_start_idx = lines.index("Summary")
            failures_start_idx = lines.index("Failures:")

            # Extract the "Summary" section
            summary_lines = lines[summary_start_idx + 2:failures_start_idx - 1]
            #print(summary_lines)
            # Find the index of the next section (e.g., "Log")
            next_section_start_idx = lines.index("Log")

            # Extract the "Failures" section
            failures_lines = lines[failures_start_idx + 1:next_section_start_idx - 1]
            
            # Initialize variables to store parsed data
            host = None
            # Initialize variables for each category
            passed_count = 0
            failed_count = 0
            user_input_count = 0
            expected_fail_count = 0
            indeterminate_count = 0
            benchmark_count = 0
            timeout_count = 0
            invalid_count = 0
            wrong_version_count = 0
            wrong_build_count = 0
            wrong_tools_count = 0

            # Initialize lists for failure categories
            failed_failures = []
            user_input_failures = []
            expected_fail_failures = []
            indeterminate_failures = []
            benchmark_failures = []
            timeout_failures = []
            invalid_failures = []
            wrong_version_failures = []
            wrong_build_failures = []
            wrong_tools_failures = []

            for line in lines:
                if line.startswith('Host:'):
                        #print(line)
                        host_line = line.split(':', 1)
                        host = host_line[1].split(None, 1)[0]
            # Iterate through the lines and parse the data
            for line in summary_lines:
                #print(f"Processing line: {line}")  # Print the line for debugging
                    if line.startswith('Passed:'):
                        passed_count = int(line.split(':', 1)[1].strip())
                    elif line.startswith('Failed:'):
                        failed_count = int(line.split(':', 1)[1].strip())
                    elif line.startswith('User Input:'):
                        #print(line)
                        match = re.search(r'(\d+)', line)
                        if match:
                            user_input_count = int(match.group(1))
                        else:
                            print("Error parsing User Input count")
                    elif line.startswith('Expected Fail:'):
                        expected_fail_count = int(line.split(':', 1)[1].strip())
                    elif line.startswith('Indeterminate:'):
                        match = re.search(r'(\d+)', line)
                        if match:
                            indeterminate_count = int(match.group(1))
                        else:
                            print("Error parsing Indeterminate count")
                    elif line.startswith('Benchmark:'):
                        match = re.search(r'(\d+)', line)
                        if match:
                            benchmark_count = int(match.group(1))
                        else:
                            print("Error parsing Benchmark count")
                    elif line.startswith('Timeout:'):
                        match = re.search(r'(\d+)', line)
                        if match:
                            timeout_count = int(match.group(1))
                        else:
                            print("Error parsing Timeout count")
                    elif line.startswith('Invalid:'):
                        match = re.search(r'(\d+)', line)
                        if match:
                            invalid_count = int(match.group(1))
                        else:
                            print("Error parsing Invalid count")
                    elif line.startswith('Wrong Version:'):
                        match = re.search(r'(\d+)', line)
                        if match:
                            wrong_version_count = int(match.group(1))
                        else:
                            print("Error parsing Wrong Version count")
                    elif line.startswith('Wrong Build:'):
                        match = re.search(r'(\d+)', line)
                        if match:
                            wrong_build_count = int(match.group(1))
                        else:
                            print("Error parsing Wrong Build count")
                    elif line.startswith('Wrong Tools:'):
                        match = re.search(r'(\d+)', line)
                        if match:
                            wrong_tools_count = int(match.group(1))
                        else:
                            print("Error parsing Wrong Tools count")
                                # Similarly, handle other failure categories
            
            # Initialize the current category
            current_category = "Failed"

            # Loop through the failure lines and categorize the failures
            for line in failures_lines:
                if line.endswith(":"):
                    current_category = line.strip(":")  # Extract the category name
                elif current_category:
                    # Append the failure to the corresponding category list
                    if current_category == "Failed":
                        failed_failures.append(line)
                    elif current_category == "User Input":
                        user_input_failures.append(line)
                    elif current_category == "Expected Fail":
                        expected_fail_failures.append(line)
                    elif current_category == "Indeterminate":
                        indeterminate_failures.append(line)
                    elif current_category == "Benchmark":
                        benchmark_failures.append(line)
                    elif current_category == "Timeout":
                        timeout_failures.append(line)
                    elif current_category == "Invalid":
                        invalid_failures.append(line)
                    elif current_category == "Wrong Version":
                        wrong_version_failures.append(line)
                    elif current_category == "Wrong Build":
                        wrong_build_failures.append(line)
                    elif current_category == "Wrong Tools":
                        wrong_tools_failures.append(line)
              

            # Create the dictionary with parsed data
            test_dict = {"Host":host, 
                         "Passed Count":passed_count, 
                         "Failed Count":failed_count, 
                         "User Input Count": user_input_count,
                         "Expectd Fail Count": expected_fail_count,
                         "Indeterminate Count": indeterminate_count,
                         "Benchmark Count": benchmark_count,
                         "Timeout Count": timeout_count,
                         "Invalid Count": invalid_count,
                         "Wrong Version Count": wrong_version_count,
                         "Wrong Build Count": wrong_build_count,
                         "Wrong Tools Count": wrong_tools_count,
                         "Failed Tests": failed_failures,
                         "User Input ": user_input_failures,
                         "Expected Fails": expected_fail_failures,
                         "Indeterminate": indeterminate_failures,
                         "Benchmark": benchmark_failures,
                         "Timeout": timeout_failures,
                         "Invalid": invalid_failures,
                         "Wrong Version": wrong_version_failures,
                         "Wrong Build": wrong_build_failures,
                         "Wrong Tools": wrong_tools_failures
                         }
            
            
            return test_dict

    except Exception as e:
        print("An error occurred:", e)
        return None


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


def main():
    try:
        year = int(input("Please enter the year for which you wish to see the reports: "))
        month_name = input("Please enter the name of the month for which the report is to be generated: ")
        month = f"{year}-{month_name.capitalize()}"

        # Download the archive if necessary
        download_archive(month)

        script_path = os.path.abspath(__file__)
        path_list = script_path.split(os.sep)
        script_directory = path_list[0:len(path_list) - 2]
        rel_path = f"data/{month}.txt"
        path = "/".join(script_directory) + "/" + rel_path

        # Read data from the file
        data = read_data_from_file(path)
        
        # Categorize the data
        tool_build_results, test_results, bsp_results = categorize_data(data)

        # Parse tool build results
        tool_build_details = tool_build_parse(tool_build_results)
        # Parse test results
        test_details = test_parse(test_results,path)
        output_file_path = 'web/json-files/tests/test_report.json'
        with open(output_file_path, 'w') as output_file:
            json.dump(test_details, output_file, indent=4)
        print("Test Details saved to:", output_file_path)
        # Save parsed data to JSON file
        output_file_path = 'web/json-files/tools/tool_build_report.json'
        with open(output_file_path, 'w') as output_file:
            json.dump(tool_build_details, output_file, indent=4)
        print("Tool Build Details saved to:", output_file_path)

        # Visualize tool build results and generate host summary
        host_tool = visualise_tool_results(tool_build_details)
        output_file_path = 'web/json-files/host-tool.json'
        with open(output_file_path, 'w') as output_file:
            json.dump(host_tool, output_file, indent=4)

        # Generate and save the monthly build summary
        month_build_summary_list = Monthly_Build_Summary(tool_build_details)
        output_file_path = 'web/visualization/public/month_tool_build_report.json'
        with open(output_file_path, 'w') as output_file:
            json.dump(month_build_summary_list, output_file, indent=4)

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()