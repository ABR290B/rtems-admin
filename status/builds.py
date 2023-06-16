#
# RTEMS Tools Project (http://www.rtems.org/)
# Copyright 2023 Chris Johns (chris@contemporary.software)
# All rights reserved.
#
# This file is part of the RTEMS Tools package in 'rtems-tools'.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

import base64
import datetime
import email
import gzip
import hashlib
import json
import mailbox
import os
import os.path
import shutil
import time
import urllib.request

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

class lists:
    lists_base = 'https://lists.rtems.org'
    mailman_base = lists_base + '/pipermail'
    builds_base = mailman_base + '/build'
    builds_ext = '.txt'

    def __init__(self, data_filename='data/months.json'):
        self.archives = {}
        self.archives_dirty = False
        self.data_filename = data_filename
        self.load()

    def __del__(self):
        self.save()

    def checksum(self, month):
        archive = self.archives[month]
        hasher = hashlib.new('sha512')
        with open(archive['file'], 'rb') as f:
            hasher.update(f.read())
        return base64.b64encode(hasher.digest()).decode('utf-8')

    def check_checksum(self, month):
        if 'sha512' not in self.archives[month]:
            return False
        return self.checksum(month) == self.archives[month]['sha512']

    def file_name(self, month):
        if month not in self.archives:
            raise Exception('unknown month: ' + month)
        return self.archives[month]['file']

    def url(self, month):
        return self.builds_base + '/' + month + self.builds_ext + '.gz'

    def download(self, month):
        req = urllib.request.Request(self.url(month))
        try:
            import ssl
            ssl_context = ssl._create_unverified_context()
            reader = urllib.request.urlopen(req, context=ssl_context)
        except:
            ssl_context = None
        if ssl_context is None:
            reader = urllib.request.urlopen(req)
        info = reader.info()
        load = False
        if month in self.archives:
            archive = self.archives[month]
            if os.path.exists(archive['file']):
                if not self.check_checksum(month):
                    load = True
            else:
                load = True
            if info.get('ETag') != archive['etag']:
                load = True
        else:
            archive = {
                'month': month,
                'etag': info.get('ETag'),
                'size': int(info.get('Content-Length').strip()),
                'sha512': '',
                'file': 'data/' + month + self.builds_ext
            }
            self.archives[month] = archive
            self.archives_dirty = True
            load = True
        if load:
            with open(archive['file'] + '.gz', 'wb') as writer:
                chunk_size = 256 * 1024
                size = archive['size']
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
            with gzip.open(archive['file'] + '.gz', 'rb') as gz:
                with open(archive['file'], 'wb') as txt:
                    shutil.copyfileobj(gz, txt)
            archive['etag'] = info.get('ETag')
            archive['size'] = int(info.get('Content-Length').strip())
            archive['sha512'] = self.checksum(month)
        reader.close()

    def load(self):
        if self.archives_dirty:
            raise Exception('load with dirty archives')
        if os.path.exists(self.data_filename):
            with open(self.data_filename, 'r', encoding='utf-8') as f:
                self.archives = json.loads(f.read())

    
    def save(self):
        if self.archives_dirty or True:
            if not os.path.exists('data'):
                os.makedirs('data')
            s = json.dumps(self.archives, sort_keys=True, indent=2)
            with open(self.data_filename, 'w', encoding='utf-8') as f:
                f.write(s)

class results:
    def __init__(self, passes, fails):
        self.passes = passes
        self.fails = fails

    @staticmethod
    def _get_list(key, recs):
        return sorted(list(set(r[key] for r in recs)))

    def failed_hosts(self):
        return self._get_list('host', self.fails)

    def failed_archs(self):
        return self._get_list('arch', self.fails)

    def failed_arch_builds(self):
        failed_hosts = self.failed_hosts()
        failed_archs = []
        for arch in self.failed_archs():
            hosts = set([r['host'] for r in self.fails if r['arch'] == arch])
            if not set(failed_hosts).isdisjoint(hosts):
                print(arch, '%d: %r  ' % (len(failed_hosts), failed_hosts),
                      '%d: %r' % (len(hosts), hosts))
                failed_archs += [arch]
        return failed_archs


class emails:
    def __init__(self, month, mbox):
        self.month = month
        self.mbox = mailbox.mbox(mbox, create=False)
        self.data = {
            'messages' : {},
            'from': {},
            'builds' : [],
            'tests' : [],
            'bsp-builds' : [],
            'unknown' : [],
            'pass' : {},
            'fail' : {}
        }

    def __str__(self):
        s = [self.month + ':']
        s += [' messages: ' + str(len(self.data['messages']))]
        s += [' builds: ' + str(len(self.data['builds']))]
        s += [' tests: ' + str(len(self.data['tests']))]
        s += [' bsp-builds: ' + str(len(self.data['bsp-builds']))]
        s += [' unknown: ' + str(len(self.data['unknown']))]
        return os.linesep.join(s)

    def _add_mid(self, bucket, key, mid):
        if key not in bucket:
            bucket[key] = []
        bucket[key] += [mid]

    def _get_message(self, mid):
        if mid not in self.data['messages']:
            raise Exception('message not found: ' + mid)
        return self.data['messages'][mid]

    def _get_subject(self, mid):
        s = self._get_message(mid)['Subject']
        return s.replace(os.linesep, '')

    def parse(self):
        for msg in self.mbox.values():
            e = email.message_from_string(str(msg))
            mid = e['Message-ID']
            if mid in self.data['messages']:
                raise Exception('duplicate message is: ' + mid)
            self.data['messages'][mid] = e
            mfrom = e['From']
            msubject = self._get_subject(mid)
            self._add_mid(self.data['from'], mfrom, mid)
            if msubject.startswith('Build '):
                self.data['builds'] += [mid]
            elif msubject.startswith('[rtems-test] '):
                self.data['tests'] += [mid]
            elif msubject.startswith('[rtems-bsp-builder] '):
                self.data['bsp-builds'] += [mid]
            else:
                self.data['unknown'] += [mid]

    def build_results(self):
        fails = []
        passes = []
        for mid in self.data['builds']:
            s = self._get_subject(mid)
            ss = s.split(':')
            if len(ss) != 2:
                raise Exception('invalid build subject: ' + s)
            srs = ss[1].split()
            if len(srs) < 4:
                raise Exception('invalid build subject: ' + s)
            rec = {
                'result': srs[0].strip(),
                'host': ss[0][len('Build '):].strip(),
                'os': srs[3].strip(),
                'arch': srs[1].strip()
            }
            if rec['result'] == 'PASSED':
                passes += [rec]
            elif rec['result'] == 'FAILED':
                fails += [rec]
            else:
                raise Exception('invalid build result: ' + rec['results'])
        return results(passes, fails)

    def has_unknowns(self):
        return len(self.data['unknown']) != 0

    def list_unknowns(self):
        s = []
        for mid in self.data['unknown']:
            s += [self._get_subject(mid)]
        return s

if __name__ == "__main__":
    mnts = [
        '2022-November',
        '2022-December',
        '2023-January',
        '2023-February',
        #'2023-March',
        #'2023-April',
        #'2023-May',
        #'2023-June'
    ]
    months_data = []
    try:
        t = lists()
        for mnt in mnts:
            if mnt not in t.archives:
                t.download(mnt)
            email_data = emails(mnt, t.file_name(mnt))
            email_data.parse()
            print(email_data)
            if email_data.has_unknowns():
                print(os.linesep.join(email_data.list_unknowns()))
            build_results = email_data.build_results()
            print(build_results.failed_arch_builds())

            # Calculate pass/fail counts for the month
            passes = len(build_results.passes)
            fails = len(build_results.fails)

            # Construct a summary table or data structure
            summary_table = {
                'Month': mnt.split('-')[1],
                'Passes': passes,
                'Fails': fails
            }
            month_data = {
                'year': mnt.split('-')[0],
                'data': [summary_table]
            }
            months_data.append(month_data)


        # Display the table in a web page or save it to a file
        table_json = json.dumps(months_data, sort_keys=True, indent=2)
        print(table_json)

        with open('webpage/summary_table.json', 'w') as f:
            f.write(table_json)


    except Exception as e:
        print(e)
