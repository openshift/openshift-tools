lib_ops_utils
=============

A role containing various general utility modules maintained by the OpenShift Ops team

For the most current module documention, see the module's doctext.

Module `iptables_chain`:

Set the rules of a chain to match the specified rules.

Module `yum_repo_exclude`:

Add package names or patterns to a YUM repository configuration's exclude line


Requirements
------------

None

Example Playbook
----------------

To make sure that we can reference these modules, include a role as such:

    - hosts: servers
      roles:
         - lib_ops_utils


For the `iptables_chain` module:

      tasks:
      - name: Create the example chain
        iptables_chain:
          name: example
          rules:
              - "-A example -p udp -m udp --dport 1025:65535 -m conntrack --ctstate NEW -j ACCEPT"
              - "-A example -p tcp -m tcp --dport 1025:65535 -m conntrack --ctstate NEW -j ACCEPT"
              - "-A example -p tcp -m tcp --dport 22 -m conntrack --ctstate NEW -j ACCEPT"
              - "-A example -p udp -m udp --dport 137 -m conntrack --ctstate NEW -j ACCEPT"
              - "-A example -p udp -m udp --dport 138 -m conntrack --ctstate NEW -j ACCEPT"

For the `yum_repo_exclude` module:

      tasks:
      - name: Don't install foo from repo bar
        yum_repo_exclude:
          name: /etc/yum.repos.d/bar.repo
          repo: bar
          patterns: [ foo ]
      - name: Stop excluding baz and qux-* from repo bar
        yum_repo_exclude:
          name: /etc/yum.repos.d/bar.repo
          repo: bar
          patterns: [ baz, qux-* ]
          state: absent

License
-------

Apache

