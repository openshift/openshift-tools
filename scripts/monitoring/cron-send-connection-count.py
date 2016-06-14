#!/bin/env python2
'''
  Command to send process connection count to Zagg
'''
# vim: expandtab:tabstop=4:shiftwidth=4

from openshift_tools.monitoring.zagg_sender import ZaggSender
import argparse
import psutil

def parse_args():
    """ parse the args from the cli """
    
    TCP_STATUSES = [
        'ESTABLISHED',
        'SYN_SENT',
        'SYN_RECV',
        'FIN_WAIT1',
        'FIN_WAIT2',
        'TIME_WAIT',
        'CLOSE',
        'CLOSE_WAIT',
        'LAST_ACK',
        'LISTEN',
        'CLOSING'
    ]

    parser = argparse.ArgumentParser(description='Process connection counter')
    parser.add_argument('--debug', action='store_true', default=None, help='Debug?')
    parser.add_argument('proc_to_check', help='The process name to be checked for connections')
    parser.add_argument('port', type=int, help='The port to be checked ')
    parser.add_argument('zabbix_key', help='Zabbix key to send with the connection count')
    parser.add_argument('-s', '--conn_status', choices=TCP_STATUSES, default='ESTABLISHED')

    
    return parser.parse_args()

def main():
    """  Main function to run the check """
    argz = parse_args()
    conn_count = 0

    for proc in psutil.process_iter():
        try:
            if proc.name() == argz.proc_to_check:
                if argz.debug: print proc.connections() 
                for conn in proc.connections():
                    if conn.status == argz.conn_status and conn.laddr[1] == argz.port:
                        conn_count += 1
        except psutil.NoSuchProcess:
            pass

    if argz.debug:
        print 'Process ({0}) on port {1} has {2} connections in {3} status'.format(argz.proc_to_check, 
                                                                                   argz.port,
                                                                                   conn_count,
                                                                                   argz.conn_status
        )



    zgs = ZaggSender(debug=argz.debug)
    zgs.add_zabbix_keys({'{0}'.format(argz.zabbix_key) : conn_count})
    zgs.send_metrics()

if __name__ == '__main__':
    main()
