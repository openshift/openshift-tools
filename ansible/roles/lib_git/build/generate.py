#!/usr/bin/env python
'''
  Generate the openshift-tools/ansible/roles/lib_git/library/ modules.
'''

import os

# pylint: disable=anomalous-backslash-in-string
GEN_STR = "#!/usr/bin/env python\n" + \
          "#     ___ ___ _  _ ___ ___    _ _____ ___ ___\n"          + \
          "#    / __| __| \| | __| _ \  /_\_   _| __|   \\\n"        + \
          "#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |\n"        + \
          "#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____\n"  + \
          "#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|\n" + \
          "#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |\n"   + \
          "#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|\n"

OPENSHIFT_ANSIBLE_PATH = os.path.dirname(os.path.realpath(__file__))


FILES = {'git_commit.py': ['lib/base.py',
                           'src/git_commit.py',
                           'ansible/git_commit.py',
                          ],
         'git_merge.py': ['lib/base.py',
                          'src/git_merge.py',
                          'ansible/git_merge.py',
                         ],
         'git_push.py': ['lib/base.py',
                         'src/git_push.py',
                         'ansible/git_push.py',
                        ],
         'git_checkout.py': ['lib/base.py',
                             'src/git_checkout.py',
                             'ansible/git_checkout.py',
                            ],
        }

def main():
    ''' combine the necessary files to create the ansible module '''
    library = os.path.join(OPENSHIFT_ANSIBLE_PATH, '..', 'library/')
    for fname, parts in FILES.items():
        with open(os.path.join(library, fname), 'w') as afd:
            afd.seek(0)
            afd.write(GEN_STR)
            for fpart in parts:
                with open(os.path.join(OPENSHIFT_ANSIBLE_PATH, fpart)) as pfd:
                    # first line is pylint disable so skip it
                    for idx, line in enumerate(pfd):
                        if idx == 0 and 'skip-file' in line:
                            continue

                        afd.write(line)


if __name__ == '__main__':
    main()
