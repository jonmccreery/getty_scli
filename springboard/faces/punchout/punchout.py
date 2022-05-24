#!/usr/bin/env python
import json
import csv
import requests
import argparse
import getpass
import time
import shutil
import os
import subprocess
import sys
import re

from time import clock, sleep
from datetime import date

from springboard.faces import BaseFace
from springboard import VERSION

from springboard.faces.punchout.provisioners.vmware import VmwareHandler


class PunchoutFace(BaseFace):
    COMMANDS = (
        'punchout',
        'build',
        'validate',
        'status'
    )

    class ArgumentParserWrapper(argparse.ArgumentParser):
        def error(self, message):
            raise PunchoutFace.ArgParseError(message)

    class ArgParseError(argparse.ArgumentError):
        def __init__(self, message):
            print(message)
            print()
            print('run \'{} build help\' for a full list of valid arguments'.
                  format(sys.argv[0])
            )
            exit()

    def __init__(self):
        super().__init__()

        self.DEBUG = False
        self.NOOP = False

        # set up some class wide constants
        self.build_param_map = {
             "certname": "vm_name",
             "domain": "domain",
             "cpu": "cpus",
             "ram": "ram",
             "folder": "folder",
             "vmware_networks": "vlan",
             "ip_address": "ip_address",
             "subnet": "subnet",
             "gateway": "gateway",
             "vm_az": "cluster",
             "vmware_templates": "template",
             "vcenter": "vcenter",
             "dns": "resolvers",
             "dns_search": "search_domains",
             "datastore": "datastore",
             "master": "master",
             "domain_join": "domain_join"
         }

        self.required_phoenix_params = [
            'certname', 'domain', 'cpu', 'ram', 'folder',
            'vmware_networks', 'vm_az', 'vmware_templates', 'vcenter'
        ]

        self.required_csv_columns = [
            'vm_name', 'domain', 'cpus', 'ram', 'folder',
            'vlan', 'template',
        ]

        self.phoenix_version = {}
        self.phoenix_port = '443'
        self.punchout_version = VERSION

        self.vmwaredata = {}   # information about vcenter clusters
        self.loc_data = {}     # information about a physical site

        self.phoenix_create_endpoint = '/api/v1/instance'
        self.phoenix_auth_endpoint = '/api/v1/auth'
        self.phoenix_vmware_endpoint = '/api/v1/vcenter'
        self.phoenix_version_endpoint = '/api/v1/version'
        self.phoenix_location_endpoint = '/api/v1/location'
        self.legacy_puppet_master = 'puppet.amer.gettywan.com'
        self.springboard_puppet_master = 'sea-prod-puppetent-master-01.amer.gettywan.com'

        self.settings = {}
        self.settings['phoenix_host'] = 'springboard.amer.gettywan.com'
        self.settings['phoenix_url'] = 'https://{}:{}'.format(self.settings['phoenix_host'], self.phoenix_port)

        # provisioner code for Vcenter builds
        self.vmhandler = VmwareHandler()

    def help(self, parser):
        parser.print_help()
        exit()

    def solicit_input(self):
        print("You must specify a build file using the -c argument.")
        exit()

    def check_host(self, target):
        FNULL = open(os.devnull, 'w')
        # real_ping = subprocess.check_output('/usr/bin/which ping', shell=True).rstrip().decode("utf-8")
        ping = subprocess.call('{} -c 1 {}'.format('ping', target), stdout=FNULL, shell=True)

        if self.DEBUG:
            print('DEBUG - {}: validating ip address...this may take a moment.'.format(target))

        # the ping check returns 0 if it gets a response
        if ping == 0:
            return False
        else:
            return True

    def translate_csv(self, mycsv):
        job = {}
        job['instances'] = []
        for row in mycsv:
            box = {}

            # bail on this row if vm_name isn't set
            if 'vm_name' in row:
                name = row['vm_name'].strip()
            else:
                continue

            # set some default values
            box['certname'] = name
            # TODO: NO HARD CODE THIS!
            box['provisioner'] = 'vmware'
            if 'vcenter' in row:
                box['vcenter'] = row['vcenter'].strip()
            if 'dns' in row:
                box['dns'] = row['resolvers'].strip()
            if 'domain' in row:
                box['dns_search'] = row['domain'].strip()

            # set up postbuild structure
            box['postbuild'] = {}
            if 'postbuild' in row and row['postbuild'] != '':
                postbuild = {}
                pb = row['postbuild'].split('|')
                step = dict(s.split('=') for s in pb)
                postbuild.update(step)
                box['postbuild'] = postbuild
            else:
                box['postbuild']['type'] = "puppet"  # TODO: make this value variable
                if 'master' in row and row['master'] != '':
                    box['postbuild']['master'] = row['master'].strip()
                elif 'master' in self.settings and self.settings['master'] != '':
                    box['postbuild']['master'] = self.settings['master']
                else:
                    box['postbuild']['master'] = self.springboard_puppet_master

            if 'cert_clean' in row and row['cert_clean'].lower() == 'true':
                box['postbuild']['cert_clean'] = True
            else:
                box['postbuild']['cert_clean'] = False

            # assign csv values that don't require any logic
            for param in self.build_param_map.keys():
                csv_column = self.build_param_map[param]
                if csv_column in row and row[csv_column] != '':
                    # we have to manually cast integer params
                    if csv_column == 'ram' or csv_column == 'cpus':
                        box[param] = int(row[csv_column].strip())
                    else:
                        box[param] = row[csv_column].strip()

                    if self.DEBUG and not self.NOOP:
                        print("DEBUG - ", param, box[param])

            # manage optional disks
            extra_disks = []
            if row['disks'] and row['disks'] != '':
                disks = row['disks'].split('|')
                for d in disks:
                    extra_disks.append({'size': int(d)})
            box['disks'] = extra_disks

            # is this a windows build?
            if 'windows' in row:
                if row['windows'].lower() == 'true':
                    box['windows'] = True
                else:
                    box['windows'] = False

            # is this windows box joining the domain?
            if 'domain_join' in row and row['domain_join'] != '':
                    box['domain_join'] = True

            # set resolvers by location
            if 'location' in row and row['location'] != '':
                box['location'] = row['location'].strip().lower()
                box['vcenter'] = self.loc_data[box['location']]['vmware']['vcenter']
                box['dns'] = self.loc_data[box['location']]['vmware']['domain'][box['domain']]['dns']
                box['dns_search'] = self.loc_data[box['location']]['vmware']['domain'][box['domain']]['dns_search']

            # build a fact structure
            facts = {}
            facts['phoenix_api_version'] = self.phoenix_version['phoenix']
            facts['punchout_version'] = self.punchout_version
            if 'facts' in row and row['facts'] != '':
                for f in row['facts'].split('|'):
                    k, v = f.split("=", 1)
                    facts[k] = v
            #    facts.update(row['facts']).split  # TODO: check this!
            if row['role'] and row['role'] != '':
                facts['puppet_hiera_role'] = row['role'].strip()
            box['facts'] = facts

            # validate ip address, then validate param info.
            # if we have a valid server, add it to the build list.
            # otherwise, keep going.
            if not self.settings['noping'] and 'ip_address' in box:
                valid_ip = self.check_host(box['ip_address'])
                if valid_ip is False:
                    print('{}: IP ({}) is invalid or already in use.  Skipping.'.format(box['ip_address'], box['certname']))
                    continue

            # this is the entry point for input validation.  we verify that the
            # union of global defaults, command line arguments, and values set in
            # the csv input file yeild enough information to build a server.
            validated_box = self.check_params(box, row, name)
            if validated_box is not False:
                job['instances'].append(validated_box)

        job['name'] = self.save_build_info(self.settings['input_file'], job)
        return job

    def check_params(self, box, row, name):
        if self.DEBUG and not self.NOOP:
            print("DEBUG - ", box)

        for param in self.required_csv_columns:
            if param not in row or row[param] == '':
                print('{}: missing csv column - {}. Skipping.'.format(name, param))
                return False
            else:
                if self.DEBUG:
                    print('DEBUG - {}: {}'.format(param, row[param]))

        for param in self.required_phoenix_params:
            if param not in box:
                print('{}: missing parameter - {}. Skipping.'.format(name, param))
                return False

        if 'vcenter' in box:
            if self.vmhandler.check_vmware_vcenter(box['vcenter'], self.vmware_data) is False:
                print('{}: vcenter does not exist!').format(name)
                return False

        v_cluster = self.vmhandler.check_vmware_cluster(box['vm_az'], box['vcenter'], self.vmware_data)
        if v_cluster is False:
            print('{}: cluster {} does not exist in {}!').format(name, box['vm_az'], box['vcenter'])
            return False
        else:
            box['vm_az'] = v_cluster

        if 'datastore' in box:
            v_datastore = self.vmhandler.check_vmware_datastore(box['datastore'], box['vcenter'], self.vmware_data)
            if v_datastore is False:
                print('{}: datastore {} does not exist in {}!').format(name, box['datastore'], box['vcenter'])
                return False
            else:
                box['datastore'] = v_datastore

        v_vlan = self.vmhandler.check_vmware_vlan(box['vmware_networks'], box['vcenter'], self.vmware_data)
        if v_vlan is False:
            print('{}: vlan {} does not exist in {}!').format(name, box['vmware_networks'], box['vcenter'])
            return False
        else:
            box['vmware_networks'] = v_vlan

        if 'folder' in box:
            if self.vmhandler.check_vmware_folder(box['folder'], box['vcenter'], self.vmware_data) is False:
                print(('{}: folder {} does not exist in {}!').format(name, box['folder'], box['vcenter']))
                return False

        return box

    def usage(self):
        return '{} build [-p PHOENIX] [--debug] [help] input_file'.format(sys.argv[0])

    def parse_arguments(self, face_args):
        parser = self.ArgumentParserWrapper(add_help=False, usage=self.usage())
        parser.add_argument('pos_arg', nargs='?')
        parser.add_argument("-p", "--phoenix", help="Phoenix server URL")
        parser.add_argument(
            "--noping",
            action='store_true',
            help="disable ping checking hosts"
        )
        parser.add_argument(
            "--debug",
            action='store_true',
            help="Dump build information to the console"
        )

        args = parser.parse_args(face_args[1:])

        if len(face_args) < 2:
            self.help(parser)

        if hasattr(args, 'pos_arg') and args.pos_arg == 'help':
            self.help(parser)
        elif hasattr(args, 'pos_arg'):
            self.settings['input_file'] = args.pos_arg

        if args.phoenix:
            self.settings['phoenix_url'] = 'http://' + args.phoenix

        # handle flags
        if args.debug:
            self.DEBUG = True
        if face_args[0] == 'validate':
            self.NOOP = True

        if args.noping:
            self.settings['noping'] = True
        else:
            self.settings['noping'] = False

    def get_version_info(self, session):
        headers = {'Content-type': 'application/json'}
        version_data = session.get(
            self.settings['phoenix_url'] + self.phoenix_version_endpoint,
            headers=headers
        )

        return version_data.json()

    def execute(self, session):
        # add csv settings row by row. after this point, our global job
        # structure should be complete.
        if 'input_file' in self.settings:
            # make sure we've been given a file that -looks- like a csv
            if not re.match('^.*csv', self.settings['input_file']):
                print('Only CSV build files are currently supported')
                exit()

            with open(self.settings['input_file'], 'rU') as fp:
                input = csv.DictReader(fp)

                self.phoenix_version = self.get_version_info(session)
                output = self.translate_csv(input)
                payload = json.dumps(output, indent=4, separators=(',', ': '))

                if self.DEBUG:
                    print('DEBUG - payload: {}'.format(payload))

        else:  # XXX: we should never get here.  csv param required
            self.solicit_input()

        if self.NOOP is False:
            br_resp = self.submit_build_request(payload, session)
            self.status_check(br_resp, session)

    def submit_build_request(self, payload, session):
        headers = {'Content-type': 'application/json'}
        r = session.post(
            self.settings['phoenix_url'] + self.phoenix_create_endpoint,
            headers=headers,
            data=payload
        )
        resp = r.json()

        if self.DEBUG:
            print("DEBUG - build request response: " + str(resp))

        return resp['status_href']

    def status_check(self, href, session):
        # Give it a few seconds to get all the instances registered
        sleep(3)
        while True:
            r = session.get(self.settings['phoenix_url'] + href)
            resp = r.json()
            print('Instance Group: {}'.format(resp['id']))
            done = True
            for i in resp['instances']:
                idone = True
                print("{} ({})".format(i['name'], i['primary_ip']))
                for s in i['status']:
                    print(" - {} - {} - {}".format(s['description'], s['status'], s['percent_complete']))
                    if s['percent_complete'] != 100.0:
                        idone = False

                if not idone:
                    done = False
                print('-' * 70)
            if done:
                break

            print('=' * 70)

            sleep(5)

    def authenticate(self, session):
        headers = {'content-type': 'application/json'}
        auth_payload = {}
        while True:
            auth_payload['username'] = input('Username: ')
            auth_payload['password'] = getpass.getpass()

            try:
                r = session.post(
                    self.settings['phoenix_url'] + self.phoenix_auth_endpoint,
                    headers=headers,
                    data=json.dumps(auth_payload)
                )

                if self.DEBUG:
                    print("DEBUG - user: {} pass: {}".format(auth_payload['username'], auth_payload['password']))
                    print("DEBUG - auth headers: " + str(r.headers))
                    print("DEBUG - response: {}".format(r.text))

                r.raise_for_status()
                self.settings['user'] = auth_payload['username']
                self.settings['pass'] = auth_payload['password']
                break
            except requests.HTTPError as e:
                print('Credentials invalid.  Try again (ctrl-c to exit).')

    def cleanup_session(self, session):
        headers = {'content-type': 'application/json'}
        session.delete(self.settings['phoenix_url'] + self.phoenix_auth_endpoint,
                       headers=headers)

    def save_build_info(self, input_file, job):
        # collect information to construct path and file names
        user_name = self.settings['user']
        build_date = (date.today()).strftime("%Y%m%d")
        build_time = time.strftime("%H%M%S")
        pwd = os.getcwd()

        # set script root and the build directory root
        build_dir = pwd + '/.builds'
        target_dir = '{}/{}'.format(build_dir, build_date)

        # get the file name without extension
        infile_base_name = os.path.splitext(os.path.basename(input_file))[0]

        # build the job name, save it to outfile in the .builds directory
        outfile_base_name = '{}_{}'.format(infile_base_name, build_time)
        file_name = outfile_base_name + '.csv'  # TODO: THIS NEEDS TO BE UN-CSVd
        file_full_name = '{}/{}'.format(target_dir, file_name)

        # force our file path to be absolute
        if input_file[0] == '/':
            infile = input_file
        else:
            infile = pwd + '/' + input_file

        # if we're not in noop mode, save our output file
        if self.NOOP is False:
            # create the build directory if it does not exist
            if not os.path.isdir(build_dir):
                os.mkdir(build_dir)
            if not os.path.isdir(target_dir):
                os.mkdir(target_dir)

            shutil.copy(infile, file_full_name)

        job_name = '{}_{}_{}_{}'.format(user_name, build_date, infile_base_name, build_time)
        job['name'] = job_name

        if 'json' in self.settings and self.settings['json']:
            json_name = outfile_base_name + '.json'
            with open(os.path.join(target_dir, json_name), 'w') as f:
                json.dump(job, f)

        return job_name

    def run_face(self, *args):
        print('\nPunchOut for Python v{}'.format(self.punchout_version.strip()))
        print('-' * 30)
        print('')

        # start off by setting config values from command line args
        self.parse_arguments(args)

        # authenticate against AD
        session = requests.Session()
        self.authenticate(session)
        if self.DEBUG and not self.NOOP:
            print("DEBUG - session data: " + str(session.cookies))

        start = clock()

        # pull vcenter information from Phoenix
        self.vmware_data = self.vmhandler.get_vmware_cache(session, self.settings, self.phoenix_vmware_endpoint)
        self.loc_data = self.vmhandler.get_vmware_locations(session, self.settings, self.phoenix_location_endpoint)
        if self.DEBUG:
            print("DEBUG - vcenter info: {}".format(json.dumps(self.vmware_data, indent=4, separators=(',', ': '))))
            print("DEBUG - location info: {}".format(json.dumps(self.loc_data, indent=4, separators=(',', ': '))))

        # and build the systems
        self.execute(session)

        end = clock()

        print('\n')
        print('=' * 70)
        print('Complete!  Took {} seconds'.format(end - start))
