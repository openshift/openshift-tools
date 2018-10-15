#!/usr/bin/env python
import json
import argparse
import sys
import pprint
import operator

from tailer import Tailer


def json_load_byteified(file_handle):
  return _byteify(
      json.load(file_handle, object_hook=_byteify),
      ignore_dicts=True
  )

def json_loads_byteified(json_text):
  return _byteify(
      json.loads(json_text, object_hook=_byteify),
      ignore_dicts=True
  )

def _byteify(data, ignore_dicts = False):
  # if this is a unicode string, return its string representation
  if isinstance(data, unicode):
    return data.encode('utf-8')
  # if this is a list of values, return list of byteified values
  if isinstance(data, list):
    return [ _byteify(item, ignore_dicts=True) for item in data ]
  # if this is a dictionary, return dictionary of byteified keys and values
  # but only if we haven't already byteified it
  if isinstance(data, dict) and not ignore_dicts:
    return {
        _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
        for key, value in data.iteritems()
    }
    # if it's anything else, return it in its original form
  return data

def parse_log():
  if args_parsed.follow:
    tailer = Tailer(open(args_parsed.logpath, 'r'))
    tailer.seek_end()
    for line in tailer.follow():
      yield json_loads_byteified(line)
  else:
    with open(args_parsed.logpath, 'r') as fd:
      for line in fd.readlines():
        yield json_loads_byteified(line)


class bcolors:
  HEADER = '\033[95m'
  OKBLUE = '\033[94m'
  OKGREEN = '\033[92m'
  WARNING = '\033[93m'
  FAIL = '\033[91m'
  ENDC = '\033[0m'
  BOLD = '\033[1m'
  UNDERLINE = '\033[4m'


def check_if(log_entry, key, value):
  try:
    keys = key.split('/')
    key_value = log_entry.get(keys[0], False)
    
    # if it didn't exist return false
    if not key_value:
      return False

    if len(keys) <= 1:
      log_entry_key = log_entry.get(keys[0])
      if type(value) is list and type(log_entry_key) is not list:
        if log_entry.get(keys[0]) in value:
          return True
      elif type(value) is list and type(log_entry_key) is list:
        return [i for i in log_entry_key if i in value]
      else:
        if value in log_entry.get(keys[0]):
          return True

    elif len(keys) > 1:
      recurse_result = check_if(key_value, '/'.join(keys[1:]), value)
      return recurse_result

  except AttributeError as e:
    print "checking key: %s has value: %s" % (key, value)
    print log_entry
    print str(e)
    exit(1)
  except TypeError as e:
    print "checking key: %s has value: %s" % (key, value)
    print keys
    print log_entry
    print str(e)
    exit(1)

def count():
  log_dict = parse_log()
  count_dict = dict()
  for log in log_dict:
    # VERB, USER, GROUP, RESOURCE, NAMESPACE
    verb = log.get('verb', "N/A")

    userdata = log.get('user', None)
    if userdata is not None:
      user = userdata.get('username', "N/A")
      group = userdata.get('groups', "N/A")

    objRef = log.get('objectRef', None)
    if objRef is not None:
      resource = objRef.get('resource', "N/A")
      namespace = objRef.get('namespace', "N/A")

    unique_line = "%s_%s_%s_%s_%s" % (verb, user, group, namespace, resource)
    if unique_line in count_dict:
      curr_count_value = count_dict.get(unique_line)
      count_dict[unique_line] = curr_count_value + 1
    else:
      count_dict[unique_line] = 1
  sorted_count = sorted(count_dict.items(), key=operator.itemgetter(1))
  for line in sorted_count:
    _line = line[0].split('_')
    print("%sHITS:%s %s -- %sVERB:%s %s - %sNS/RESOURCE:%s %s/%s - %sUSER:%s %s - %sGROUP:%s %s" % (
      bcolors.HEADER,
      bcolors.ENDC,
      line[-1],
      bcolors.HEADER,
      bcolors.ENDC,
      _line[0],
      bcolors.HEADER,
      bcolors.ENDC,
      _line[3],
      _line[4],
      bcolors.HEADER,
      bcolors.ENDC,
      _line[1],
      bcolors.HEADER,
      bcolors.ENDC,
      _line[2]
      )
   )

def callback(filename, lines):
  for line in lines:
    yield line

def main():
  # Get dictionary of json log
  for log in parse_log():
    
    # ignore if response and response is not set
    if not args_parsed.requests and not args_parsed.responses:
      pass
    # Check if filtering for requests or responses
    else:
      if args_parsed.requests:
        if not check_if(log, 'stage', 'RequestReceived'):
          continue
      elif args_parsed.responses:
        if not check_if(log, 'stage', 'ResponseComplete'):
          continue

    if args_parsed.timestamp:
      if not check_if(log, 'timestamp', args_parsed.timestamp):
        continue

    if args_parsed.sourceips:
      if not check_if(log, 'sourceIPs', args_parsed.sourceips):
        continue

    if args_parsed.verbs:
      if not check_if(log, 'verb', args_parsed.verbs):
        continue

    if args_parsed.users:
      if not check_if(log, 'user/username', args_parsed.users):
        continue

    if args_parsed.groups:
      if not check_if(log, 'user/groups', args_parsed.groups):
        continue

    if args_parsed.namespaces:
      if not check_if(log, 'objectRef/namespace', args_parsed.namespaces):
        continue

    if args_parsed.resources:
      if not check_if(log, 'objectRef/resource', args_parsed.resources):
        continue

    if args_parsed.uri:
      if not check_if(log, 'requestURI', args_parsed.uri):
        continue

    if args_parsed.raw_print:    
      pprint.pprint(log)
    elif args_parsed.count:
      pass
    else:
      try: 
        message = '' + \
bcolors.HEADER + 'TIMESTAMP: ' + bcolors.ENDC + log.get('timestamp') + '\n' + \
bcolors.HEADER + 'STAGE: ' + bcolors.ENDC + log.get('stage') + '\n' + \
bcolors.HEADER + 'URI: ' + bcolors.ENDC + log.get('requestURI') + '\n'

        if log.get('responseStatus'):
          message = message + \
bcolors.HEADER + 'HTTP_RESPONSE: ' + bcolors.ENDC + str(log['responseStatus'].get('code')) + '\n'

        if log.get('user'):
          message = message + \
bcolors.HEADER + 'USER: ' + bcolors.ENDC + log['user'].get('username') + '\n' + \
bcolors.HEADER + 'GROUPS: ' + bcolors.ENDC + ', '.join(log['user'].get('groups')) + '\n'

        if log.get('objectRef'):
          message = message + \
bcolors.HEADER + 'NAMESPACE: ' + bcolors.ENDC + log['objectRef'].get('namespace', '----') + '\n' + \
bcolors.HEADER + 'RESOURCE: ' + bcolors.ENDC + log['objectRef'].get('resource', '----') + '\n'

        message = message + \
bcolors.HEADER + 'VERB: ' + bcolors.ENDC + log.get('verb') + '\n'

        print message
      except:
        print "Failed to parse this log line with following exception: \n" + str(sys.exc_info()[0]) + "\n"
        pprint.pprint(log)
        exit(1)


# Create a parser to get args for filters
parser = argparse.ArgumentParser(description='Python App to parse and filter OCP audit logs in JSON format.')

# count number of unique hits
parser.add_argument('-c', action='store_true', dest='count', required=False, default=False,
                   help='Count the number of unique hits based on VERB, USER, GROUP, RESOURCE, NAMESPACE')

# path to log file
parser.add_argument('-f', action='store', dest='logpath', required=True,
                   help='Log file to load')
# follow the log file
parser.add_argument('-F', action='store_true', dest='follow',
                   help='Follow log file')
# timestamp
parser.add_argument('-t', action='store', dest='timestamp',
                   help='Which time to search')
# verbs
parser.add_argument('-v', action='append', dest='verbs',
                   help='Which verbs to search for "get, list, watch, create, update, patch, delete, deletecollection, and proxy"')
# users
parser.add_argument('-u', action='append', dest='users',
                   help='names of users to search for.')
# groups
parser.add_argument('-g', action='append', dest='groups',
                   help='names of groups to search for.')
# Source IP
parser.add_argument('-s', action='append', dest='sourceips',
                   help='IP(s) to search for.')
# namespaces
parser.add_argument('-n', action='append', dest='namespaces',
                   help='Namespaces to search for.')
# resources
parser.add_argument('-r', action='append', dest='resources',
                   help='Resources to search for.')
# request uri
parser.add_argument('-l', action='store', dest='uri',
                   help='URI to search for.')
# request uri
parser.add_argument('-p', action='store_true', dest='raw_print',
                   help='Raw log format')

# stages
stage_group = parser.add_mutually_exclusive_group()
stage_group.add_argument('--requests', action='store_true',
                        help='Filter for Requests received')
stage_group.add_argument('--responses', action='store_true',
                        help='Filter for Responses transmitted')

args_parsed = parser.parse_args()

if args_parsed.count:
  count()
else:
  main()
