import hashlib
import json
import os
import base64
import gzip
import urllib.request
import datetime
import shutil

def download_archive(month):
    lists_base = 'https://lists.rtems.org'
    mailman_base = lists_base + '/pipermail'
    builds_base = mailman_base + '/build'
    builds_ext = '.txt'

    url = builds_base + '/' + month + builds_ext + '.gz'
    file_name = f'data/{month}{builds_ext}'

    if os.path.exists(file_name):
        print(f"The archive {month}{builds_ext} already exists. Skipping download.")
        return

    print(f"Downloading {month}{builds_ext}...")
    try:
        req = urllib.request.Request(url)
        try:
            import ssl
            ssl_context = ssl._create_unverified_context()
            reader = urllib.request.urlopen(req, context=ssl_context)
        except:
            ssl_context = None
        if ssl_context is None:
            reader = urllib.request.urlopen(req)
        info = reader.info()
        with open(file_name + '.gz', 'wb') as writer:
            chunk_size = 256 * 1024
            size = int(info.get('Content-Length').strip())
            have = 0
            while True:
                chunk = reader.read(chunk_size)
                if not chunk:
                    break
                writer.write(chunk)
                have += chunk_size
                percent = round((float(have) / size) * 100, 2)
                if percent > 100:
                    percent = 100
                print('\r' + month + ': %0.0f%% ' % (percent), end='')
            print()
        with gzip.open(file_name + '.gz', 'rb') as gz:
            with open(file_name, 'wb') as txt:
                shutil.copyfileobj(gz, txt)
        reader.close()
    except Exception as e:
        print(f"Error downloading the archive {month}{builds_ext}: {e}")


def months(year, month):
    today = datetime.datetime.today()
    mnths = []
    while year <= today.year and month < today.month + 1:
        mnths.append(datetime.date(year, month, 1).strftime('%Y-%B'))
        month += 1
        if month > 12:
            year += 1
            month = 1
    return mnths


if __name__ == "__main__":
    year = int(input("Please enter the year for which you wish to see the reports: "))
    month_name = input("Please enter the name of the month for which the report is to be generated: ")
    month = f"{year}-{month_name.capitalize()}"
    download_archive(month)
