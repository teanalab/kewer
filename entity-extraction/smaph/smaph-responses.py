#!/usr/bin/env python3

import requests
import json
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--outfile', required=True)
args = parser.parse_args()

url = "https://smaph.d4science.org/smaph/annotate"
headers = {'accept': 'application/json'}
responses = {}

# Follow instructions on https://github.com/marcocor/smaph to obtain below credentials
cse_id = ''
google_key = ''
smaph_token = ''

with open('../queries-v2.txt') as qf:
    for line in qf:
        qid, qtext = line.rstrip().split('\t')
        # print(qid, qtext, sep=' === ')
        while True:
            r = requests.get(url, headers=headers, params={'q': qtext,
                'gcube-token': smaph_token, 'google-cse-id': cse_id, 'google-api-key': google_key})
            if r.status_code == requests.codes.ok:
                break
            else:
                print('status not ok!')
        response = r.json()
        print(qid, qtext, response)
        responses[qid] = response

with open(args.outfile, 'w') as f:
    json.dump(responses, f, sort_keys=True,
            indent=4, separators=(',', ': '))
