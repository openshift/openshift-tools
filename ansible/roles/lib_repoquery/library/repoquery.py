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

        self.query_format = "%{name}|%{version}|%{release}|%{arch}|%{repo}"

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
    def format_packages(query_output):
        ''' format the package data into something that can be presented '''

        package_dict = defaultdict(list)

        for version in query_output.split('\n'):
            pkg_info = version.split("|")
            pkg_version = {}
            pkg_version['version'] = pkg_info[1]
            pkg_version['release'] = pkg_info[2]
            pkg_version['arch'] = pkg_info[3]
            pkg_version['repo'] = pkg_info[4]

            package_dict[pkg_info[0]].append(pkg_version)

        return package_dict

    def format_versions(self, formatted_packages):
        ''' Gather and present the versions of each package '''

        versions_dict = {}

        for package, info_list in formatted_packages.iteritems():
            versions_subdict = defaultdict(list)
            for package_info in info_list:
                if package_info['version'] not in versions_subdict['available_versions']:
                    versions_subdict['available_versions'].append(package_info['version'])

                if self.match_version:
                    if package_info['version'].startswith(self.match_version):
                        if package_info['version'] not in versions_subdict['matched_versions']:
                            versions_subdict['matched_versions'].append(package_info['version'])

            versions_dict[package] = versions_subdict
            versions_dict[package]['available_versions'].sort(key=LooseVersion)
            versions_dict[package]['latest'] = versions_subdict['available_versions'][-1]

            if self.match_version:
                versions_dict[package]['requested_match_version'] = self.match_version
                if versions_dict[package]['matched_versions']:
                    versions_dict[package]['matched_version_found'] = True
                    versions_dict[package]['matched_versions'].sort(key=LooseVersion)
                    versions_dict[package]['matched_version_latest'] = versions_dict[package]['matched_versions'][-1]
                else:
                    versions_dict[package]['matched_version_found'] = False
                    versions_dict[package]['matched_versions'] = []
                    versions_dict[package]['matched_version_latest'] = ""

        return versions_dict

    def repoquery(self):
        '''perform a repoquery '''

        repoquery_cmd = self.build_cmd()

        rval = self._repoquery_cmd(repoquery_cmd, True, 'raw')

        formatted_packages = Repoquery.format_packages(rval['results'].strip())
        formatted_versions = self.format_versions(formatted_packages)

        rval['versions'] = formatted_versions

        if self.verbose:
            rval['packages'] = formatted_packages
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
            query_type=dict(default='all', required=False, type='str',
                            choices=['installed', 'available', 'recent',
                                     'updates', 'extras', 'all']
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
