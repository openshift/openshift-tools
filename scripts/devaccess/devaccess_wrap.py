#!/usr/bin/python
# vim: expandtab:tabstop=4:shiftwidth=4
'''
    Tool to provide developers with ability to remotely run a limited
    set of commands.
'''
# Disabling invalid-name because pylint doesn't like the naming conention we have.
# pylint: disable=invalid-name

import logging
import logging.config
import os
import re
import subprocess
import sys
import yaml

with open('/etc/openshift_tools/devaccesslogging.conf') as f:
    logging.config.dictConfig(yaml.load(f))

log = logging.getLogger('devget')

class DevGetError(Exception):
    ''' DevGet-specific exceptions '''
    pass

class OCCmd(object):
    ''' Class to hold and standardize building of /usr/bin/oc commands
        out of raw string command line text '''

    def __init__(self, raw_cmd, allowed_commands):
        # original command line text
        self._raw_cmd = raw_cmd
        self._allowed_commands = allowed_commands
        self._current_command = None
        self._current_type = None
        self.runner = None

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

    @staticmethod
    def valid_param_check(string):
        ''' Check for valid string parameter '''
        matched = re.match("^[A-Za-z](?:-?[A-Za-z0-9])*$", string)
        if matched is None:
            raise DevGetError("Invalid characters in parameter value")

    @staticmethod
    def get_param_value(params, short_p):
        ''' Get value of parameter short_p or long_p out of param_list.
            Return value and params with the param and value removed. '''
        params_split = params.split()
        delete_tokens = []
        value = None

        x = 0
        while x < len(params_split):
            # check for token/param exact match (ie '-n' but not
            # -nSOMETHING)
            if params_split[x] == short_p:
                # Fail if we're at the end of the param/token list
                if x == len(params_split) - 1:
                    raise DevGetError("Dangling param without value")

                # A param value starting with '-' is invalid
                OCCmd.valid_param_check(params_split[x+1])

                value = params_split[x+1]

                delete_tokens.append(x)
                delete_tokens.append(x+1)

                # skip next token since we already processed it
                x = x + 1
            # handle single token with param+value (ie -nVALUE)
            elif params_split[x].startswith(short_p):
                value = re.sub(short_p, '', params_split[x])
                OCCmd.valid_param_check(value)

                delete_tokens.append(x)
            # TODO: elif match double-dash params (ie --namespace and
            # --namespace=VALUE type params

            x = x + 1

        # clean up processed tokens before sending back remaining string
        delete_tokens.sort(reverse=True)
        for token in delete_tokens:
            params_split.pop(token)

        params_post_proccessed = ' '.join(params_split)

        return (value, params_post_proccessed)


    def get_namespace(self, cmd):
        ''' find a namespace (if passed in) and return cmd
            without the namespace-related parameters '''

        (value, new_cmd) = OCCmd.get_param_value(cmd, '-n')

        cmd_split = new_cmd.split()
        for param in cmd_split:
            if param == '--all-namespaces':
                value = 'all'
                new_cmd = new_cmd.replace('--all-namespaces', '')

        if value is not None:
            self._params['namespace'] = value
        return new_cmd

    def get_follow(self, cmd):
        ''' find -f --follow (if passed in) and return cmd without
            the param '''

        cmd_split = cmd.split()
        delete_tokens = []

        for x in range(0, len(cmd_split)):
            if cmd_split[x] == '-f' or cmd_split[x] == '--follow':
                self._params['follow'] = '--follow'
                delete_tokens.append(x)

        delete_tokens.sort(reverse=True)
        for token in delete_tokens:
            cmd_split.pop(token)

        new_cmd = " ".join(cmd_split)
        return new_cmd

    def get_output_format(self, cmd):
        ''' find output format parameters (if passed in) and return cmd
            without the format parameters '''

        (value, new_cmd) = OCCmd.get_param_value(cmd, '-o')

        self._params['output_format'] = value
        return new_cmd

    def get_container(self, cmd):
        ''' Take '-c' command line param (for oc logs)
            Return remaining string '''

        (value, new_cmd) = OCCmd.get_param_value(cmd, '-c')

        self._params['container'] = value
        return new_cmd

    def get_verb_type_subject(self, cmd):
        ''' Take command without parameters and parse it into its
            various components.
            Return remaining string (should be "")
        '''
        cmd_split = cmd.split()

        # handle 'oc <verb> <type> <optional-subject>' type of cmd
        # ...or even 'oc logs <subject>'
        cmd_split.pop(0)

        # make sure none of the remaining tokens are parameters
        for param in cmd_split:
            if param.startswith('-'):
                raise Exception('Should not have any more parameters left for processing')

        self._params['verb'] = cmd_split[0]
        self._params['type'] = cmd_split[1]
        for command_type in self._current_command['types']:
            if self._params['type'] in command_type['names']:
                self._current_type = command_type
                self.runner = command_type['runner']

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

        for command in self._allowed_commands:
            if self._raw_cmd.startswith(command['base']):
                self._current_command = command

                cmd_no_namespace = self.get_namespace(self._raw_cmd)
                log.debug('no ns: %s', cmd_no_namespace)

                cmd_no_output_formatting = self.get_output_format(cmd_no_namespace)
                log.debug('no format: %s', cmd_no_output_formatting)

                cmd_no_follow = self.get_follow(cmd_no_output_formatting)
                log.debug('no follow: %s', cmd_no_follow)

                cmd_no_container = self.get_container(cmd_no_follow)
                log.debug('no container: %s', cmd_no_container)

                #
                # all that is left should be: 'oc <verb> <type> <optional-subject>'
                #
                cmd = self.get_verb_type_subject(cmd_no_container)

                # should be nothing left after we parsed all the tokens
                if cmd != "":
                    raise Exception("Unprocessed command tokens left.")

    #pylint: disable=too-many-branches
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
        if self._current_command.has_key('namespaces'):
            if self._params['namespace'] == 'all':
                normalized_cmd = '{orig} --all-namespaces'.format(orig=normalized_cmd)
            else:
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
    def cmd_with_tail(cmd):
        ''' replace process with called one to keep getting updates '''
        args = cmd.split()
        os.execvp(args[0], args)

    @staticmethod
    def safe_command(cmd):
        ''' return any safe command output
            this is for all commands that should not have any type of sensitive data in them
        '''
        results = ''
        our_env = os.environ
        our_env['PATH'] = '/usr/sbin:' + our_env['PATH']
        try:
            results = subprocess.check_output(cmd.split(), env=our_env)
        except subprocess.CalledProcessError:
            log.exception("Call to process (%s) failed", cmd)

        return results

    @staticmethod
    def sudo_command(cmd):
        ''' return the output running it through sudo
        TODO: try to make it work with one external script that has elevated privileges
        '''
        results = ''
        our_env = os.environ
        our_env['PATH'] = '/usr/sbin:' + our_env['PATH']
        try:
            results = subprocess.check_output(['/usr/bin/sudo'] + cmd.split(), env=our_env)
        except subprocess.CalledProcessError:
            log.exception("Call to process (%s) failed", cmd)

        return results

    @staticmethod
    def oc_get_generic(occmd):
        ''' provide a generic 'oc get ' artifact '''
        run_cmd = WhitelistedCommands.oc_cmd_builder(occmd)
        results = subprocess.check_output(run_cmd)

        return results

    @staticmethod
    def oc_get_clusterwide(occmd):
        ''' provide non namespaced objects '''
        n_cmd = occmd.normalized_cmd()
        run_cmd = WhitelistedCommands.oc_cmd_builder(n_cmd)
        results = subprocess.check_output(run_cmd)

        return results

    @staticmethod
    def oc_get_routes(occmd):
        ''' provide 'oc get routes' '''

        n_cmd = occmd.normalized_cmd()
        run_cmd = WhitelistedCommands.oc_cmd_builder(n_cmd)
        # -o yaml and -o json output of routes can expose
        # certificate details. will need to redact those
        # bits if more detailed output is requested
        results = subprocess.check_output(run_cmd)

        return results

class DevGet(object):
    ''' Class to wrap approved developer access commands '''
    CONFIG_FILE = '/etc/openshift_tools/devaccess.yaml'
    ACL_FILE = '/etc/openshift_tools/devaccess_users.yaml'

    def __init__(self):
        self._args = None
        self._user = None
        self._oc_cmd = None
        self._config = None
        self._runner = None

        self.parse_args()
        log.debug("Got args: " + str(self._args))
        self.parse_config()

        self._allowed_commands = self.setup_permissions()
        self._default_params = None

        if self._args.startswith('oc'):
            self._oc_cmd = OCCmd(self._args, self._allowed_commands)

    def parse_config(self):
        ''' Load in config settings '''
        custom_config = os.environ.get('DEVACCESS_CONFIG')
        if custom_config is not None:
            self._config = yaml.load(open(custom_config, 'r'))
        else:
            self._config = yaml.load(open(DevGet.CONFIG_FILE, 'r'))

        if self._config.has_key('kubeconfig_path'):
            WhitelistedCommands(kubeconfig_path=self._config['kubeconfig_path'])
        if not self._config.has_key('aclfile_path'):
            self._config['aclfile_path'] = DevGet.ACL_FILE

        if not self._config.has_key('debug'):
            self._config['debug'] = False

    def setup_permissions(self):
        ''' Read in users and roles.
            Return list of allowed commands for user. '''

        perm_dict = yaml.load(open(self._config['aclfile_path'], 'r'))
        # create list of allowed commands for the user
        allowed_roles = []
        for user in perm_dict['users']:
            if user['username'] == self._user:
                if user.has_key('roles'):
                    allowed_roles = user['roles']
                # the 'ALL' group applies to everyone
                allowed_roles.append('ALL')
        log.debug("user: %s roles: %s", self._user, str(allowed_roles))

        commands = []
        # get list of allowed commands for each role
        for role in perm_dict['roles']:
            if role['name'] in allowed_roles:
                commands.extend(role['commands'])

        log.debug("user: %s commands: %s", self._user, str(commands))
        return commands

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
            if re.match("^[A-Za-z][A-Za-z0-9]*$", sys.argv[2]) is None:
                raise DevGetError("Invalid username found")
            user = sys.argv[2]
        else:
            # not being launched from ssh authorized_keys, so
            # drop the devaccess_wrap from the command
            args = " ".join(sys.argv[1:])
            user = os.getlogin()

        self._args = args
        self._user = user


    #pylint: disable=too-many-nested-blocks
    def can_run_cmd(self, cmd):
        ''' Return True/False for whether user is allowed to run the command
        '''
        can_run = False

        for command in self._allowed_commands:
            # incoming command starts with one of the known command bases
            if cmd.startswith(command['base']):
                # found our matched command, set the function that should run it
                self._runner = command['runner']
                # remove the matched part, strip whitespace
                # TODO: check if doing this with regex is faster to process
                cmd = cmd.replace(command['base'], '').strip()
                # if command has no switches or other params but matched, then we just run it
                if len(cmd) == 0:
                    can_run = True
                    break

                # tokenizing the param list
                all_tokens = cmd.split()
                delete_tokens = []
                # switches need to be present, partial matches are ok
                if command.has_key('switches'):
                    log.debug('all switches for command: %s', all_tokens)
                    for token in all_tokens:
                        for switch in command['switches']:
                            if token == switch:
                                delete_tokens.append(token)
                        log.debug('accepted tokens: %s', delete_tokens)

                # removing tokens found by switches before moving on
                leftover_tokens = [token for token in all_tokens if token not in delete_tokens]
                leftover_command = ' '.join(leftover_tokens)
                # whatever was left over of the command should match one in the list
                if command.has_key('leftover'):
                    for leftover in command['leftover']:
                        patt = re.compile(leftover, flags=re.DOTALL)
                        if patt.match(leftover_command):
                            leftover_tokens = []

                if command.has_key('defaultparams'):
                    self._default_params = command['defaultparams']

                # we processed every part of the command, might as well run it
                if len(leftover_tokens) == 0:
                    can_run = True

        return can_run

    def cmd_not_allowed(self):
        ''' Print generic info when user isn't able to
            run a command.
        '''

        print "\nCommand not supported/allowed"
        print "#############################"
        print "Allowed commands:"

        for command in self._allowed_commands:
            outputline = '{}'.format(command['base'])
            if command.has_key('types'):
                for cmdtype in command['types']:
                    tmpstr = '{} [{}]'.format(outputline, '/'.join(cmdtype['names']))
                    if cmdtype.has_key('namespaces'):
                        if 'all' in cmdtype['namespaces']:
                            tmpstr += ' --all-namespaces'
                            tmpns = [x for x in cmdtype['namespaces'] if x not in ['all']]
                        else:
                            tmpns = cmdtype['namespaces']
                        if len(tmpns) > 0:
                            tmpstr += ' -n <{}>'.format('/'.join(tmpns))
                    if cmdtype.has_key('output'):
                        tmpstr += ' -o {}'.format('|'.join(cmdtype['output']))
                    print tmpstr
            else:
                tmpstr = '{}'.format(outputline)
                if command.has_key('switches'):
                    tmpstr += ' {}'.format(' '.join(command['switches']))
                if command.has_key('leftover'):
                    tmpstr += ' ({})'.format(' | '.join(command['leftover']))
                print tmpstr
        sys.exit(1)

    def main(self):
        ''' Entry point for class '''
        cmd = self._args
        log.debug("user: %s command: %s", self._user, self._args)

        # Check whether user has permissions to run command.
        # oc commands are handled in a special way, since those
        # whitelisted function handlers expect an OCCmd object to be passed
        if self._oc_cmd is not None:
            try:
                full_cmd = self._oc_cmd.normalized_cmd()
                log.debug("user: %s Normalized cmd: %s", self._user, full_cmd)

                results = getattr(WhitelistedCommands, self._oc_cmd.runner)(full_cmd)
                print results
            #pylint: disable=broad-except
            except Exception:
                log.exception('Command failed to run. %s', cmd)
                self.cmd_not_allowed()
        # non-oc command run handling
        elif self.can_run_cmd(cmd):
            if self._default_params is not None:
                cmd_split = cmd.split()
                cmd = '{} {} {}'.format(cmd_split[0], ' '.join(self._default_params), ' '.join(cmd_split[1:]))
            results = getattr(WhitelistedCommands, self._runner)(cmd)
            print results
        else:
            self.cmd_not_allowed()

if __name__ == '__main__':
    devget = DevGet()
    devget.main()
