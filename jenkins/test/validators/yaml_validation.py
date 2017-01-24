#!/usr/bin/env python
# flake8: noqa
#
#  python yaml validator for a git commit
#
'''
python yaml validator for a git commit
'''
import sys
import os
import yaml

def validate_yaml(file_list):
    """ Validate yaml syntax for each yaml file in file_list """
    results = []
    for file_mod in file_list.split(","):
        # if the file extensions is not yml or yaml, move along.
        if not file_mod.endswith('.yml') and not file_mod.endswith('.yaml'):
            continue

        # We use symlinks in our repositories, ignore them.
        if os.path.islink(file_mod):
            continue

        print "YAML validation running aginst: %s" % file_mod

        try:
            yaml.load(open(file_mod))
            results.append(True)

        except yaml.scanner.ScannerError as yerr:
            print "YAML validation failed on " + file_mod + ": " + str(yerr)
            results.append(False)

    return results


def usage():
    ''' Print usage '''
    print """usage: yaml_validation.py [file_list...]

    file_list:  The list of files to run yaml validation against

Arguments can be provided through the following environment variables:

    file_list:  PRV_CHANGED_FILES"""

def main():
    '''
    Perform yaml validation
    '''
    if len(sys.argv) == 2:
        file_list = sys.argv[1]
    elif len(sys.argv) > 2:
        print len(sys.argv)-1, "arguments provided, expected 2."
        usage()
        sys.exit(2)
    else:
        file_list = os.getenv("PRV_CHANGED_FILES", "")

    if file_list == "":
        print "file list must be provided"
        usage()
        sys.exit(3)

    results = validate_yaml(file_list)
    if not all(results):
        print "YAML validation failed!"
        sys.exit(1)
    else:
        print "YAML validation succeeded!"

if __name__ == "__main__":
    main()
