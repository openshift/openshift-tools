#!/usr/bin/python
# vim: expandtab:tabstop=4:shiftwidth=4
#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name
''' Generate a single combined yaml file to load into
    OpenShift as a secret '''

import base64
import yaml

def main():
    ''' Create single generated-secrets.yml' that can be loaded
        as a secret into OpenShift '''
    yaml_files = ['scriptrunner.yml', 'zabbix-server-vars.yml',
                  'zagg-server-vars.yml']

    yaml_dict = {}
    gen_yaml = None

    with open('generated-secrets.yml', 'r') as f:
        gen_yaml = yaml.safe_load(f)

    for yfile in yaml_files:
        yfile_yaml = open(yfile, 'r').read()
        yfile_b64 = base64.b64encode(yfile_yaml)
        yaml_dict[yfile] = yfile_b64

    for yfile, yfile_b64 in yaml_dict.iteritems():
        gen_yaml['data'][yfile] = yfile_b64

    with open('generated-secrets.yml', 'w') as f:
        yaml.dump(gen_yaml, f, default_flow_style=False)

    print "Saved as generated-secrets.yml"
    print "Load into OpenShift with 'oc create -f generated-secrets.yml'"

if __name__ == '__main__':
    main()
