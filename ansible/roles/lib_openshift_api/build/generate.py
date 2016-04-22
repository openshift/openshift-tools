#!/usr/bin/env python
'''
  Generate the openshift-tools/ansible/roles/lib_openshift_cli/library/ modules.
'''

import os

# pylint: disable=anomalous-backslash-in-string
GEN_STR = "#!/usr/bin/env python # pylint: disable=too-many-lines\n" + \
          "#     ___ ___ _  _ ___ ___    _ _____ ___ ___\n"          + \
          "#    / __| __| \| | __| _ \  /_\_   _| __|   \\\n"        + \
          "#   | (_ | _|| .` | _||   / / _ \| | | _|| |) |\n"        + \
          "#    \___|___|_|\_|___|_|_\/_/_\_\_|_|___|___/_ _____\n"  + \
          "#   |   \ / _ \  | \| |/ _ \_   _| | __|   \_ _|_   _|\n" + \
          "#   | |) | (_) | | .` | (_) || |   | _|| |) | |  | |\n"   + \
          "#   |___/ \___/  |_|\_|\___/ |_|   |___|___/___| |_|\n"

OPENSHIFT_ANSIBLE_PATH = os.path.dirname(os.path.realpath(__file__))


FILES = {'oc_obj.py': ['lib/base.py',
                       '../../lib_yaml_editor/build/src/yedit.py',
                       'src/oc_obj.py',
                       'ansible/oc_obj.py',
                      ],
         'oc_secret_add.py': ['lib/base.py',
                              '../../lib_yaml_editor/build/src/yedit.py',
                              'src/oc_secret_add.py',
                              'ansible/oc_secret_add.py',
                             ],
         'oc_secret.py': ['lib/base.py',
                          '../../lib_yaml_editor/build/src/yedit.py',
                          'src/oc_secret.py',
                          'ansible/oc_secret.py',
                         ],
         'oc_service.py': ['lib/base.py',
                           '../../lib_yaml_editor/build/src/yedit.py',
                           'lib/service.py',
                           'src/oc_service.py',
                           'ansible/oc_service.py',
                          ],
         'oc_volume.py': ['lib/base.py',
                          '../../lib_yaml_editor/build/src/yedit.py',
                          'lib/volume.py',
                          'lib/deploymentconfig.py',
                          'src/oc_volume.py',
                          'ansible/oc_volume.py',
                         ],
         'oc_edit.py': ['lib/base.py',
                        '../../lib_yaml_editor/build/src/yedit.py',
                        'src/oc_edit.py',
                        'ansible/oc_edit.py',
                       ],
         'oc_env.py': ['lib/base.py',
                       '../../lib_yaml_editor/build/src/yedit.py',
                       'lib/deploymentconfig.py',
                       'src/oc_env.py',
                       'ansible/oc_env.py',
                      ],
         'oadm_router.py': ['lib/base.py',
                            '../../lib_yaml_editor/build/src/yedit.py',
                            'lib/service.py',
                            'lib/deploymentconfig.py',
                            'src/oadm_router.py',
                            'ansible/oadm_router.py',
                           ],
         'oadm_registry.py': ['lib/base.py',
                              '../../lib_yaml_editor/build/src/yedit.py',
                              'lib/volume.py',
                              'lib/service.py',
                              'lib/deploymentconfig.py',
                              'src/oadm_registry.py',
                              'ansible/oadm_registry.py',
                             ],
         'oadm_ca.py': ['lib/base.py',
                        '../../lib_yaml_editor/build/src/yedit.py',
                        'src/oadm_certificate_authority.py',
                        'ansible/oadm_certificate_authority.py',
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


