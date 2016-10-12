# pylint: skip-file
'''
   OpenShiftCLI class that wraps the oc commands in a subprocess
'''
# pylint: disable=too-many-lines

#import atexit
#import copy
import json
import os
#import re
#import shutil
#import subprocess
#import yaml
import statuspageio

class StatusPageIOAPIError(Exception):
    '''Exception class for openshiftcli'''
    pass

# pylint: disable=too-few-public-methods
class StatusPageIOAPI(object):
    ''' Class to wrap the command line tools '''
    def __init__(self,
                 api_key,
                 page_id=,
                 org_id=None):
        ''' Constructor for OpenshiftCLI '''
        self.api_key = api_key
        self.page_id = page_id
        self.org_id = org_id
        self.client = statuspageio.Client(api_key=self.api_key, page_id=self.page_id, org_id=self.org_id)

    def _get_incidents(self, scheduled=False, unresolved_only=False):
        '''return a list of incidents'''
        if unresolved_only:
            return self.client.incidents.list_unresolved()

        if unresolved_only:
            return self.client.incidents.list_scheduled()
       
        return self.client.incidents.list()

