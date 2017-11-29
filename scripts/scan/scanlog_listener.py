#!/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

""" A small server to listen for image-inspector scan results and log them to a local file. """

import argparse
import json
import os
import socket
import sys


class ClamLogSrv(object):
    """ Class to receive and report scan results. """


    @staticmethod
    def check_arguments():
        """ Ensure that an argument was passed in from the command line.
        Returns:
            Parsed argument(s), if provided
        """

        parser = argparse.ArgumentParser(description='Get parameters from the user.')
        parser.add_argument('-p', '--port',
                            help='Specify the port on which to listen for clam scan results.')
        parser.add_argument('-s', '--servername',
                            help='Specify name of the host of the socket, e.g. localhost.')
        parser.add_argument('-l', '--logfile',
                            help='Provide the path to the logfile on the host.')
        args = parser.parse_args()

        if not args.servername and not args.port and not args.logfile:
            print('Specify the hostname, port, and logfile location.\n'
                  'Usage:\n'
                  'example: {0} -s localhost -p 8080 -l /var/log/clam/scanlog'.format(parser.prog))
            sys.exit(10)

        return args


    @staticmethod
    def start_serve(hostname, hostport, logfile):
        """ Listen on specified port for incoming clam logs. """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = (hostname, int(hostport))
        sock.bind(server_address)

        sock.listen(1)

        while True:
            connection, _ = sock.accept()

            try:
                while True:
                    data = connection.recv(1024)
                    newdata = data.split('\n')[6]
                    rec_js = json.loads(newdata)

                    filemode = ''

                    if os.path.isfile(logfile):
                        filemode = 'a'
                    else:
                        filemode = 'w'

                    with open(logfile, filemode) as open_file:
                        open_file.write(json.dumps(rec_js, indent=4, sort_keys=True))

                    break

            finally:
                connection.close()


    def main(self):
        """ Main function. """

        args = self.check_arguments()

        if args.servername and args.port and args.logfile:
            self.start_serve(args.servername, args.port, args.logfile)

        else:
            raise ValueError('Please specify server name, port, and logfile.')


if __name__ == '__main__':
    CLAMLOG = ClamLogSrv()
    CLAMLOG.main()
