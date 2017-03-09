#!/usr/bin/env python
'''
  Generate the openshift-tools/ansible/roles/lib_gcloud/library/ modules.
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


FILES = {'gcloud_dm_deployments.py': ['lib/base.py',
                                      #'../../lib_yaml_editor/build/src/yedit.py',
                                      'src/gcloud_dm_deployments.py',
                                      'ansible/gcloud_dm_deployments.py',
                                     ],
         'gcloud_dm_resource_builder.py': ['lib/base.py',
                                           'lib/gcpresource.py',
                                           'lib/address.py',
                                           'lib/bucket.py',
                                           'lib/disk.py',
                                           'lib/firewall_rule.py',
                                           'lib/forwarding_rule.py',
                                           'lib/health_check.py',
                                           'lib/network.py',
                                           'lib/network_interface.py',
                                           'lib/subnetwork.py',
                                           'lib/target_pool.py',
                                           'lib/vminstance.py',
                                           'src/gcloud_dm_resource_builder.py',
                                           'ansible/gcloud_dm_resource_builder.py',
                                          ],
         'gcloud_compute_image.py': ['lib/base.py',
                                     'src/gcloud_compute_image.py',
                                     'ansible/gcloud_compute_image.py',
                                    ],
         'gcloud_dm_manifest.py': ['lib/base.py',
                                   'src/gcloud_dm_manifest.py',
                                   'ansible/gcloud_dm_manifest.py',
                                  ],
         'gcloud_compute_addresses.py': ['lib/base.py',
                                         'src/gcloud_compute_addresses.py',
                                         'ansible/gcloud_compute_addresses.py',
                                        ],
         'gcloud_compute_disk_labels.py': ['lib/base.py',
                                           'src/gcloud_compute_disk_labels.py',
                                           'ansible/gcloud_compute_disk_labels.py',
                                          ],
         'gcloud_compute_label.py': ['lib/base.py',
                                     'src/gcloud_compute_label.py',
                                     'ansible/gcloud_compute_label.py',
                                    ],
         'gcloud_compute_projectinfo.py': ['lib/base.py',
                                           'src/gcloud_compute_projectinfo.py',
                                           'ansible/gcloud_compute_projectinfo.py',
                                          ],
         'gcloud_iam_sa.py': ['lib/base.py',
                              'src/gcloud_iam_sa.py',
                              'ansible/gcloud_iam_sa.py',
                             ],
         'gcloud_iam_sa_keys.py': ['lib/base.py',
                                   'src/gcloud_iam_sa_keys.py',
                                   'ansible/gcloud_iam_sa_keys.py',
                                  ],
         'gcloud_dm_resource_reconciler.py': ['lib/base.py',
                                              'src/gcloud_dm_resource_reconciler.py',
                                              'ansible/gcloud_dm_resource_reconciler.py',
                                             ],
         'gcloud_project_policy.py': ['lib/base.py',
                                      'src/gcloud_project_policy.py',
                                      'ansible/gcloud_project_policy.py',
                                     ],
         'gcloud_compute_zones.py': ['lib/base.py',
                                     'src/gcloud_compute_zones.py',
                                     'ansible/gcloud_compute_zones.py',
                                    ],
         'gcloud_config.py': ['lib/base.py',
                              'src/gcloud_config.py',
                              'ansible/gcloud_config.py',
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


