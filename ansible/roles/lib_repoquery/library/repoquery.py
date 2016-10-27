#!/usr/bin/env python
#     ___ ___ _  _ ___ ___    _ _____ ___ ___
#    / __| __| \| | __| _ \  /_\_   _| __|   \
#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |
#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____
#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|
#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |
#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|
'''
   class that wraps the repoquery commands in a subprocess
'''
# pylint: disable=too-many-lines

from collections import defaultdict
from distutils.version import LooseVersion
import subprocess

class RepoqueryCLIError(Exception):
    '''Exception class for repoquerycli'''
    pass

# pylint: disable=too-few-public-methods
class RepoqueryCLI(object):
    ''' Class to wrap the command line tools '''
    def __init__(self,
                 verbose=False):
        ''' Constructor for RepoqueryCLI '''
        self.verbose = verbose
        self.verbose = True

    def _repoquery_cmd(self, cmd, output=False, output_type='json'):
        '''Base command for repoquery '''
        cmds = ['/usr/bin/repoquery', '--quiet']

        cmds.extend(cmd)

        rval = {}
        results = ''
        err = None

        if self.verbose:
            print ' '.join(cmds)

        proc = subprocess.Popen(cmds,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        stdout, stderr = proc.communicate()
        rval = {"returncode": proc.returncode,
                "results": results,
                "cmd": ' '.join(cmds),
               }

        if proc.returncode == 0:
            if output:
                if output_type == 'raw':
                    rval['results'] = stdout

            if self.verbose:
                print stdout
                print stderr

            if err:
                rval.update({"err": err,
                             "stderr": stderr,
                             "stdout": stdout,
                             "cmd": cmds
                            })

        else:
            rval.update({"stderr": stderr,
                         "stdout": stdout,
                         "results": {},
                        })

        return rval

class Repoquery(RepoqueryCLI):
    ''' Class to wrap the repoquery
    '''
    # pylint: disable=too-many-arguments
    def __init__(self,
                 name,
                 query_type,
                 show_duplicates,
                 match_version,
                 verbose
                ):
        ''' Constructor for YumList '''
        super(Repoquery, self).__init__(None)
        self.name = name
        self.query_type = query_type
        self.show_duplicates = show_duplicates
        self.match_version = match_version
        self.verbose = verbose

        if self.match_version:
            self.show_duplicates = True

        self.query_format = "%{version}|%{release}|%{arch}|%{repo}|%{version}-%{release}"

    def build_cmd(self):
        ''' build the repoquery cmd options '''

        repo_cmd = []

        repo_cmd.append("--pkgnarrow=" + self.query_type)
        repo_cmd.append("--queryformat=" + self.query_format)

        if self.show_duplicates:
            repo_cmd.append('--show-duplicates')

        repo_cmd.append(self.name)

        return repo_cmd

    @staticmethod
    def process_versions(query_output):
        ''' format the package data into something that can be presented '''

        version_dict = defaultdict(dict)

        for version in query_output.split('\n'):
            pkg_info = version.split("|")

            pkg_version = {}
            pkg_version['version'] = pkg_info[0]
            pkg_version['release'] = pkg_info[1]
            pkg_version['arch'] = pkg_info[2]
            pkg_version['repo'] = pkg_info[3]
            pkg_version['version_release'] = pkg_info[4]

            version_dict[pkg_info[4]] = pkg_version

        return version_dict

    def format_versions(self, formatted_versions):
        ''' Gather and present the versions of each package '''

        versions_dict = {}
        versions_dict['available_versions_full'] = formatted_versions.keys()

        # set the match version, if called
        if self.match_version:
            versions_dict['matched_versions_full'] = []
            versions_dict['requested_match_version'] = self.match_version
            versions_dict['matched_versions'] = []

        # get the "full version (version - release)
        versions_dict['available_versions_full'].sort(key=LooseVersion)
        versions_dict['latest_full'] = versions_dict['available_versions_full'][-1]

        # get the "short version (version)
        versions_dict['available_versions'] = []
        for version in versions_dict['available_versions_full']:
            versions_dict['available_versions'].append(formatted_versions[version]['version'])

            if self.match_version:
                if version.startswith(self.match_version):
                    versions_dict['matched_versions_full'].append(version)
                    versions_dict['matched_versions'].append(formatted_versions[version]['version'])

        versions_dict['available_versions'].sort(key=LooseVersion)
        versions_dict['latest'] = versions_dict['available_versions'][-1]

        # finish up the matched version
        if self.match_version:
            if versions_dict['matched_versions_full']:
                versions_dict['matched_version_found'] = True
                versions_dict['matched_versions'].sort(key=LooseVersion)
                versions_dict['matched_version_latest'] = versions_dict['matched_versions'][-1]
                versions_dict['matched_version_full_latest'] = versions_dict['matched_versions_full'][-1]
            else:
                versions_dict['matched_version_found'] = False
                versions_dict['matched_versions'] = []
                versions_dict['matched_version_latest'] = ""
                versions_dict['matched_version_full_latest'] = ""

        return versions_dict

    def repoquery(self):
        '''perform a repoquery '''

        repoquery_cmd = self.build_cmd()

        rval = self._repoquery_cmd(repoquery_cmd, True, 'raw')

        processed_versions = Repoquery.process_versions(rval['results'].strip())
        formatted_versions = self.format_versions(processed_versions)

        rval['versions'] = formatted_versions
        rval['package_name'] = self.name

        if self.verbose:
            rval['raw_versions'] = processed_versions
        else:
            del rval['results']

        return rval

def main():
    '''
    ansible repoquery module
    '''
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='list', type='str', choices=['list']),
            name=dict(default=None, required=True, type='str'),
            query_type=dict(default='repos', required=False, type='str',
                            choices=['installed', 'available', 'recent',
                                     'updates', 'extras', 'all', 'repos']
                           ),
            verbose=dict(default=False, required=False, type='bool'),
            show_duplicates=dict(default=None, required=False, type='bool'),
            match_version=dict(default=None, required=False, type='str'),
        ),
        supports_check_mode=False,
        required_if=[('show_duplicates', True, ['name'])],
    )

    repoquery = Repoquery(module.params['name'],
                          module.params['query_type'],
                          module.params['show_duplicates'],
                          module.params['match_version'],
                          module.params['verbose'],
                         )

    state = module.params['state']

    if state == 'list':
        results = repoquery.repoquery()

        if results['returncode'] != 0:
            module.fail_json(msg=results)

        module.exit_json(changed=False, results=results, state="present")

    module.exit_json(failed=True,
                     changed=False,
                     results='Unknown state passed. %s' % state,
                     state="unknown")

# pylint: disable=redefined-builtin, unused-wildcard-import, wildcard-import, locally-disabled
# import module snippets.  This are required
#if __name__ == '__main__':
#    main()
if __name__ == "__main__":
    from ansible.module_utils.basic import *

    main()
