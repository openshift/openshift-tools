# pylint: skip-file

import os

class Utils(object):
    ''' zabbix utilities class'''

    @staticmethod
    def exists(content, key='result'):
	''' Check if key exists in content or the size of content[key] > 0 '''
	if not content.has_key(key):
	    return False

	if not content[key]:
	    return False

	return True
