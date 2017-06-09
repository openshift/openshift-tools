#!/usr/bin/python
# vim: expandtab:tabstop=4:shiftwidth=4
'''
    Tool to provide developers with ability to remotely run a limited
    set of commands.
'''
# Disabling invalid-name because pylint doesn't like the naming conention we have.
# pylint: disable=invalid-name

import logging
import os
import re
import subprocess
import sys
import yaml

class OCCmd(object):
    ''' Class to hold and standardize building of /usr/bin/oc commands
        out of raw string command line text '''
    def __init__(self, raw_cmd):
        # original command line text
        self._raw_cmd = raw_cmd

        self._params = {}
        # always define a namespace
        self._params['namespace'] = 'default'
        # whether special output formatting is requested
        self._params['output_format'] = None
        # --follow or -f
        self._params['follow'] = None
        # -c for 'oc get logs -c <container>
        self._params['container'] = None

        # the actual command to run without the params
        # (ie oc get pods or oc get secrets my-secret)
        self._params['verb'] = None
        self._params['type'] = None
        self._params['subject'] = None
        self.parse_cmd()

    def get_namespace(self, cmd):
        ''' find a namespace (if passed in) and return cmd
            without the namespace-related parameters '''

        cmd_split = cmd.split()
        delete_tokens = []

        for x in range(0, len(cmd_split)):
            if cmd_split[x] == '-n':
                # token was exactly '-n' so next token is the namespace
                self._params['namespace'] = cmd_split[x+1]

                # make sure to mark these items for removal from list
                # before returning the command
                delete_tokens.append(cmd_split[x])
                delete_tokens.append(cmd_split[x+1])

                # skip next token since we already processed it
                x = x + 1
            elif cmd_split[x].startswith('-n'):
                # we have a namespace in the format of -n<namespace>
                self._params['namespace'] = re.sub('-n', '', cmd_split[x])

                delete_tokens.append(cmd_split[x])
            # elif match --namespace and --namespace=<namespace> params

        # now clean up namespace-related tokens before returning
        # cmd without the namespace-related parameters
        for token in delete_tokens:
            cmd_split.remove(token)

        new_cmd = " ".join(cmd_split)
        return new_cmd

    def get_follow(self, cmd):
        ''' find -f --follow (if passed in) and return cmd without
            the param '''

        cmd_split = cmd.split()
        delete_tokens = []

        for x in range(0, len(cmd_split)):
            if cmd_split[x] == '-f' or cmd_split[x] == '--follow':
                self._params['follow'] = '--follow'
                delete_tokens.append(cmd_split[x])

        for token in delete_tokens:
            cmd_split.remove(token)

        new_cmd = " ".join(cmd_split)
        return new_cmd

    def get_output_format(self, cmd):
        ''' find output format parameters (if passed in) and return cmd
            without the format parameters '''

        cmd_split = cmd.split()
        delete_tokens = []

        for x in range(0, len(cmd_split)):
            if cmd_split[x] == '-o':
            # token was exactly '-o' so next token is output format
                self._params['output_format'] = cmd_split[x+1]

                # mark tokens for removal
                delete_tokens.append(cmd_split[x])
                delete_tokens.append(cmd_split[x+1])

                # skip next token since we already processed it
                x = x + 1
            elif cmd_split[x].startswith('-o'):
                # we have an output in format -o<output_format>
                self._params['output_format'] = re.sub('-o', '', cmd_split[x])

                delete_tokens.append(cmd_split[x])

        # clean up output-related tokens and return resulting string
        for token in delete_tokens:
            cmd_split.remove(token)

        new_cmd = " ".join(cmd_split)
        return new_cmd

    def get_container(self, cmd):
        ''' Take '-c' command line param (for oc logs)
            Return remaining string '''
        cmd_split = cmd.split()
        delete_tokens = []

        for x in range(0, len(cmd_split)):
            if cmd_split[x] == '-c':
                self._params['container'] = cmd_split[x+1]

                # mark tokens for removal
                delete_tokens.append(cmd_split[x])
                delete_tokens.append(cmd_split[x+1])

                # skip next token since we already processed it
                x = x + 1
            elif cmd_split[x].startswith('-c'):
                self._params['container'] = re.sub('-c', '', cmd_split[x])

                delete_tokens.append(cmd_split[x])

        for token in delete_tokens:
            cmd_split.remove(token)

        new_cmd = " ".join(cmd_split)
        return new_cmd


    def get_verb_type_subject(self, cmd):
        ''' Take command without parameters and parse it into its
            various components.
            Return remaining string (should be "")
        '''
        cmd_split = cmd.split()

        # handle 'oc <verb> <type> <optional-subject>' type of cmd
        # ...or even 'oc logs <subject>'
        cmd_split.remove("oc")

        # make sure none of the remaining tokens are parameters
        for param in cmd_split:
            if param.startswith('-'):
                raise Exception('Should not have any more parameters left for processing')

        self._params['verb'] = cmd_split[0]
        self._params['type'] = cmd_split[1]
        if len(cmd_split) > 2:
            self._params['subject'] = cmd_split[2]

        if self._params['verb'] == 'logs':
            # logs commands aren't in the form of verb type subject
            # just verb subject, so wipe out _type and store it in
            # _subject instead
            self._params['subject'] = self._params['type']
            self._params['type'] = None

        cmd_split.remove(self._params['verb'])
        if self._params['type'] is not None:
            cmd_split.remove(self._params['type'])
        if self._params['subject'] is not None:
            cmd_split.remove(self._params['subject'])

        return " ".join(cmd_split)

    def parse_cmd(self):
        ''' take a raw oc command and tokenize it '''

        #
        # Get all params first
        #
        cmd_no_namespace = self.get_namespace(self._raw_cmd)

        cmd_no_output_formatting = self.get_output_format(cmd_no_namespace)

        cmd_no_follow = self.get_follow(cmd_no_output_formatting)

        cmd_no_container = self.get_container(cmd_no_follow)

        #
        # all that is left should be: 'oc <verb> <type> <optional-subject>'
        #
        cmd = self.get_verb_type_subject(cmd_no_container)


        # should be nothing left after we parsed all the tokens
        if cmd != "":
            raise Exception("Unprocessed command tokens left.")

    def normalized_cmd(self, generic=False):
        ''' return 'normalized' string in the format:
            oc <action> <type> <opt-subject> -n<namespace> -o<output_format> --follow
            Use generic=True to substitue out thing with subject-specific parameters
            (ie. router-3-abx3j changed to SUBJECT) for easier command matching
        '''
        normalized_cmd = "oc"

        for item in [self._params['verb'], self._params['type']]:
            if item is not None:
                normalized_cmd = "{orig} {token}".format(orig=normalized_cmd,
                                                         token=item)

        if self._params['subject'] is not None:
            if generic:
                normalized_cmd = "{orig} SUBJECT".format(orig=normalized_cmd)
            else:
                normalized_cmd = "{orig} {subject}".format(orig=normalized_cmd,
                                                           subject=self._params['subject'])

        if self._params['container'] is not None:
            # add container
            if generic:
                normalized_cmd = "{orig} -cSUBJECT".format(orig=normalized_cmd)
            else:
                normalized_cmd = "{orig} -c{container}".format(orig=normalized_cmd,
                                                               container=self._params['container'])
        # add namespace
        normalized_cmd = "{orig} -n{namespace}".format(orig=normalized_cmd,
                                                       namespace=self._params['namespace'])
        # add output formatting
        if self._params['output_format'] is not None:
            normalized_cmd = "{cmd} -o{oformat}".format(cmd=normalized_cmd,
                                                        oformat=self._params['output_format'])

        # add --follow
        if self._params['follow'] is not None:
            normalized_cmd = "{cmd} {follow}".format(cmd=normalized_cmd,
                                                     follow=self._params['follow'])

        return normalized_cmd


class WhitelistedCommands(object):
    ''' Class to hold functions implementing allowed functionality '''
    KUBECONFIG = '/etc/origin/master/admin.kubeconfig'

    def __init__(self, kubeconfig_path=None):
        if kubeconfig_path is not None:
            WhitelistedCommands.KUBECONFIG = kubeconfig_path

    @staticmethod
    def oc_cmd_builder(cmd):
        ''' Add default command-line args for 'oc' commands '''
        cmd_to_run = cmd.split()
        cmd_to_run.extend(['--config', WhitelistedCommands.KUBECONFIG])
        return cmd_to_run

    @staticmethod
    def rpm_qa(cmd):
        ''' return 'rpm -qa' output '''

        results = subprocess.check_output(cmd.split())
        return results

    @staticmethod
    def oc_get_nodes(occmd):
        ''' provide 'oc get nodes' '''

        n_cmd = occmd.normalized_cmd()
        run_cmd = WhitelistedCommands.oc_cmd_builder(n_cmd)
        results = subprocess.check_output(run_cmd)

        return results

class DevGet(object):
    ''' Class to wrap approved developer access commands '''
    CONFIG_FILE = '/etc/openshift_tools/devaccess.yaml'
    ACL_FILE = '/etc/openshift_tools/devaccess_users.yaml'
    LOG_FILE = '/var/log/devaccess.log'

    def __init__(self, kubeconfig=None):
        self._debug = False
        self._args = None
        self._user = None
        self._oc_cmd = None
        self._config = None

        self.parse_args()
        self.parse_config()
        self.setup_logging()
        logging.debug("Got args: " + str(self._args))

        self._allowed_commands = self.setup_permissions()
        self._command_dict = self.whitelisted_command_list()
        if kubeconfig is not None:
            WhitelistedCommands(kubeconfig_path=kubeconfig)

    def parse_config(self):
        ''' Load in config settings '''
        self._config = yaml.load(open(DevGet.CONFIG_FILE, 'r'))

        if not self._config.has_key('aclfile_path'):
            self._config['aclfile_path'] = DevGet.ACL_FILE

        if not self._config.has_key('logfile_path'):
            self._config['logfile_path'] = DevGet.LOG_FILE

        if not self._config.has_key('debug'):
            self._config['debug'] = False

    def setup_permissions(self):
        ''' Read in users and roles.
            Return list of allowed commands for user. '''

        perm_dict = yaml.load(open(self._config['aclfile_path'], 'r'))
        # create list of allowed commands for the user
        for user in perm_dict['users']:
            if user['username'] == self._user:
                allowed_roles = user['roles']
                # the 'ALL' group applies to everyone
                allowed_roles.append('ALL')
        logging.debug("user: %s roles: %s", self._user, str(allowed_roles))

        commands = []
        # get list of allowed commands for each role
        for role in perm_dict['roles']:
            if role['name'] in allowed_roles:
                commands.extend(role['commands'])

        logging.debug("user: %s commands: %s", self._user, str(commands))
        return commands

    @staticmethod
    def whitelisted_command_list():
        ''' Dict with key of whitelisted commmands mapped to their
            actual implementation.
            The commands should be in 'normalized' output style from OCCmd.
        '''
        command_dict = {}

        ### commands for everyone (the 'ALL' group)
        command_dict['oc get nodes -ndefault'] = WhitelistedCommands.oc_get_nodes
        command_dict['oc get nodes -ndefault -ojson'] = WhitelistedCommands.oc_get_nodes
        command_dict['rpm -qa'] = WhitelistedCommands.rpm_qa

        return command_dict

    def parse_args(self):
        ''' Parse command line arguments passed in through the
            SSH_ORIGINAL_COMMAND environment variable when READ_SSH is a
            param.
            Also handle when run manually. '''
        args = None
        user = None
        read_ssh_env = False

        # authorized_keys will force direct our command/argv to be
        # 'devaccess_wrap READ_SSH <username>' with the original params stored
        # in SSH_ORIGINAL_COMMAND
        if "READ_SSH" in sys.argv:
            read_ssh_env = True

        if read_ssh_env:
            cmd = os.environ.get("SSH_ORIGINAL_COMMAND", "")

            # SSH_ORIGINAL_COMMAND will include the whole command
            # as a continuous string
            args = cmd

            # The user's authorized_keys will force the command run to be:
            # <path to devaccess_wrap> READ_SSH <username>
            # Save the username for permission lookups later.
            user = sys.argv[2]
        else:
            # not being launched from ssh authorized_keys, so
            # drop the devaccess_wrap from the command
            args = " ".join(sys.argv[1:])
            user = os.getlogin()

        self._args = args
        self._user = user

        if self._args.startswith('oc'):
            self._oc_cmd = OCCmd(self._args)

    def setup_logging(self):
        ''' Configure logging '''

        if os.environ.has_key("DEVACC_DEBUG") or self._debug is True:
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO

        logging.basicConfig(filename=self._config['logfile_path'],
                            format="%(asctime)s %(message)s",
                            level=log_level)

    def can_run_cmd(self, cmd):
        ''' Return True/False for whether user is allowed to run the command
        '''

        return cmd in self._allowed_commands

    def cmd_not_allowed(self, user_cmd):
        ''' Print generic info when user isnt' able to
            run a command.
        '''

        print "Command not supported/allowed: {}".format(user_cmd)
        print "Allowed commands:"
        for cmd in self._allowed_commands:
            print cmd

    def main(self):
        ''' Entry point for class '''
        cmd = self._args
        logging.info("user: %s command: %s", self._user, self._args)

        # Check whether user has permissions to run command.
        # oc commands are handled in a special way, since those
        # whitelisted function handlers expect an OCCmd object to be passed
        if self._oc_cmd is not None:
            generic_cmd = self._oc_cmd.normalized_cmd(generic=True)
            full_cmd = self._oc_cmd.normalized_cmd()
            logging.debug("user: %s Normalized cmd: %s", self._user, full_cmd)

            if self.can_run_cmd(generic_cmd):
                results = self._command_dict[generic_cmd](self._oc_cmd)
                print results
            else:
                self.cmd_not_allowed(full_cmd)
        # non-oc command run handling
        elif self.can_run_cmd(cmd):
            results = self._command_dict[cmd](cmd)
            print results
        else:
            self.cmd_not_allowed(cmd)


if __name__ == '__main__':
    devget = DevGet()
    devget.main()
