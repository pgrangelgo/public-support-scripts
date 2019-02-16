#!/usr/bin/env python

import argparse
import requests
import sys
import json
from datetime import date
import pprint

import pdpyras

PARAMETERS = {
    'is_overview': 'true',
    'date_range': 'all',
}

def mass_update_incidents(args):
    session = pdpyras.APISession(args.api_key,
        default_from=args.requester_email)
    if args.user_id:
        PARAMETERS['user_ids[]'] = args.user_id.split(',')
    if args.service_id:
        PARAMETERS['service_ids[]'] = args.service_id.split(',')
    if args.action == 'resolve':
        PARAMETERS['statuses[]'] = ['triggered', 'acknowledged']
    elif args.action == 'acknowledge':
        PARAMETERS['statuses[]'] = ['triggered']
    try:
        total = 0
        for incident in session.list_all('incidents', params=PARAMETERS):
            if args.dry_run:
                print("Not acting on incident %s because -n/--dry-run "
                    "specified."%incident['id'])
                total += 1
                continue
            session.rput(incident['self'], json={
                'type': 'incident_reference',
                'id': incident['id'],
                'status': '{0}d'.format(args.action), # acknowledged or resolved
            })
            print("%sd incident %s"%(args.action, incident['id']))
            total += 1
    except pdpyras.PDClientError as e:
        if e.response is not None:
            print(e.response.text)
        raise e        
    finally:
        print("Total of %d incidents updated."%total)

def main(argv=None):
    ap = argparse.ArgumentParser(description="Mass ack or resolve incidents "
        "either corresponding to a given service, or assigned to a given "
        "user.")
    ap.add_argument('-k', '--api-key', required=True, help="REST API key")
    ap.add_argument('-s', '--service-id', default=None, help="ID of the "
        "service, or comma-separated list of services, for which incidents "
        "should be updated; leave blank to match all services.")
    ap.add_argument('-u', '--user-id', default=None, help="ID of user, "
        "or comma-separated list of users, whose assigned incidents should be "
        "included in the action. Leave blank to match incidents for all users.")
    ap.add_argument('-a', '--action', default='resolve', choices=['acknowldege',
        'resolve'], help="Action to take on incidents en masse")
    ap.add_argument('-e', '--requester-email', required=True, help="Email "
        "address of the user who will be marked as performing the actions.")
    ap.add_argument('-n', '--dry-run', default=False, action='store_true',
        help="Dry run (don't actually do anything but show what would be done")
    args = ap.parse_args()
    mass_update_incidents(args)

if __name__=='__main__':
    sys.exit(main())
