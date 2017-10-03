#!/usr/bin/env python
"""
This script will dump config files in a clean format for developer access
"""
import os
import pwd
import sys
import yaml

CONFIG_FILE = "/usr/local/bin/redacted.yaml"


def load_config():
    '''
    Loads the config file for redacted
    '''
    with open(CONFIG_FILE, "r") as stream:
        try:
            config_data = yaml.load(stream)
        except yaml.YAMLError as err:
            # The redacted config is broken, OPs should quickly verify/fix
            print "Error loading redacted config, ping OPs"
            print err
            sys.exit(-1)

    if len(sys.argv) < 2:
        print "Pass config file to the script. Possible values are:"
        for config_option in config_data["config"]:
            print "- " + config_option["name"]
        sys.exit(-1)

    for config_option in config_data["config"]:
        if config_option["name"] == sys.argv[1]:
            return_data = config_option

    if "return_data" not in vars():
        # this should never really happen but ohh well
        print "There is something wrong, ping OPs"
        sys.exit(-1)

    return return_data


def remove_key(keys, data):
    '''
    Removed nested keys from a dict
    '''
    if not isinstance(data, list) and keys[0] not in data.keys():
        return data

    if isinstance(data, list):
        for num in range(0, len(data)):
            data[num] = remove_key(keys, data[num])
    else:
        if len(keys) == 1:
            data[keys[0]] = "!REDACTED!"
        else:
            data[keys[0]] = remove_key(keys[1:], data[keys[0]])

    return data


def filter_config(data):
    '''
    Loads the requested config file and filters out private data from config
    '''
    with open(data["path"], "r") as stream:
        try:
            config_data = yaml.load(stream)
        except yaml.YAMLError as err:
            # The redacted config is broken, OPs should quickly verify/fix
            print "Error loading cluster config, ping OPs"
            print data["path"]
            print err
            sys.exit(-1)

    for key in data["attributes"]:
        keys = key.split('.')
        config_data = remove_key(keys, config_data)

    return config_data


def main():
    '''
    The main entry point
    '''
    # Checks to see if we are root, I use pwd instead of just checking 0
    # Easier to read this way I think
    if os.getuid() != pwd.getpwnam('root').pw_uid:
        print "You must run this script with sudo"
        sys.exit(-1)

    config = load_config()
    return_data = filter_config(config)
    print yaml.dump(return_data, default_flow_style=False, width=4096)

if __name__ == "__main__":
    main()
