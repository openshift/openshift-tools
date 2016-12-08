openshift_aws_group
=========

Ansible role for GPG encrypting data found at a path

Requirements
------------

Ansible Modules:


Role Variables
--------------

gpges_dir: Directory where the unencrypted data exists.  The data should be named with the username.
gpges_users: User dict that has the users gpg key included
gpges_file_name: Part of the file name to add to the user names to create the encrypted file.
gpges_email_domain: domain to send the email to. This will send an email to username@domain
gpges_mail_subject: Subject of the email to send users.

user dict should look like this:

+sample-gpges_users:
- user1:
    username: user1
    gpgkey: XXXXXXXXXX
- user2:
    username: user2
    gpgkey: YYYYYYYYYYYY


Dependencies
------------


Example Playbook
----------------
  - role: tools_roles/gpg_encrypt_send
    gpges_dir: /tmp/some_dir
    gpges_users: "{{ user_dict }}"
    gpges_email_domain: example.com
    gpges_file_name: add_this_to_the_encrypted_file_name
    gpges_mail_subject: Something ecrypted is being sent to you


License
-------

Apache 2.0

Author Information
------------------

Openshift Operations
