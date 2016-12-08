# vim: expandtab:tabstop=4:shiftwidth=4

'''
    Wrapper for interfacing with cgroups.

    This is especially useful for getting container statistics.
'''

# Adding the ignore because it does not like the naming of the script
# to be different than the class name
# pylint: disable=invalid-name

import os
import sys
import multiprocessing
import time
from collections import namedtuple

DEFAULT_CGROUP_PATH = ['sys', 'fs', 'cgroup']

SYSTEM_SLICE_TYPE = 'system.slice'
USER_SLICE_TYPE = 'user.slice'

MemoryStats = namedtuple('MemoryStats', ['used', 'limit', 'limit_used_pct', 'failcnt'])
CpuStats = namedtuple('CpuStats', ['used_pct'])

CONV_RATE = 10**7


class CgroupUtil(object):
    ''' Class to store docker storage information
    '''

    def __init__(self, cgroup_entity, slice_type=SYSTEM_SLICE_TYPE, cgroup_basedir=None):
        self.cgroup_entity = cgroup_entity

        if not cgroup_basedir:
            self.cgroup_basedir = os.path.join(os.path.sep, *DEFAULT_CGROUP_PATH)
        else:
            self.cgroup_basedir = cgroup_basedir

        self.slice_type = slice_type

    @staticmethod
    def _read_cgroup_file_as_int(path):
        ''' Reads the cgroup file and coverts the contents to an integer '''

        # Check if the cgroup is gone, if it is, return 0.
        # Returning 0 in this case is so that we're compatible with docker.stat's behavior
        if not os.path.isfile(path):
            return 0

        with open(path, 'r') as memfile:
            return int(memfile.read())

    def get_raw_memory_stats(self):
        ''' Reads the raw memory stats from cgroups '''
        path = os.path.join(self.cgroup_basedir, 'memory', self.slice_type, self.cgroup_entity)

        mem_used = CgroupUtil._read_cgroup_file_as_int(os.path.join(path, 'memory.usage_in_bytes'))
        mem_limit = CgroupUtil._read_cgroup_file_as_int(os.path.join(path, 'memory.limit_in_bytes'))
        mem_failcnt = CgroupUtil._read_cgroup_file_as_int(os.path.join(path, 'memory.failcnt'))

        if mem_limit == 0:
            mem_limit = sys.maxsize

        return {
            'usage': mem_used,
            'limit': mem_limit,
            'failcnt': mem_failcnt,
            }

    @staticmethod
    def cpu_stats_to_cpu_pct(stats):
        ''' Takes in raw cgroup cpu stats and calculates the percent cpu used.
        '''
        previous_cpu_stats = stats['precpu_stats']
        cpu_stats = stats['cpu_stats']

        cpu_used_pct = 0.0
        cpu_delta = cpu_stats['cpu_usage']['total_usage'] - previous_cpu_stats['cpu_usage']['total_usage']

        system_delta = cpu_stats['system_cpu_usage'] - previous_cpu_stats['system_cpu_usage']


        if system_delta > 0.0 and cpu_delta > 0.0:
            cpu_used_pct = ((float(cpu_delta) / float(system_delta)) * \
                           len(cpu_stats['cpu_usage']['percpu_usage'])) * 100

        return cpu_used_pct


    def get_raw_cpuacct_stat(self):
        ''' Reads the raw cpuacct stats from cgroups '''
        path = os.path.join(self.cgroup_basedir, 'cpuacct', self.slice_type, self.cgroup_entity)

        # The cgroup is gone, return 0. This is to be compatible with docker.
        if not os.path.isdir(path):
            return (0, 0, 0, [0] * multiprocessing.cpu_count())

        cpu_stat_str = None
        with open(os.path.join(path, 'cpuacct.stat'), 'r') as memfile:
            cpu_stat_str = memfile.read()

        user_usage = None
        system_usage = None

        for line in cpu_stat_str.split(os.linesep):
            if line:
                parts = line.split(' ')

                if parts[0] == 'user':
                    user_usage = int(parts[1]) * CONV_RATE

                if parts[0] == 'system':
                    system_usage = int(parts[1]) * CONV_RATE

        total_usage = user_usage + system_usage

        percpu_usage = None

        with open(os.path.join(path, 'cpuacct.usage_percpu'), 'r') as memfile:
            line = memfile.read()
            percpu_usage = [int(col) for col in line.strip().split(' ')]

        return (user_usage, system_usage, total_usage, percpu_usage)


    @staticmethod
    def get_raw_system_cpu_usage():
        ''' Reads the raw system cpu usage from proc '''
        with open('/proc/stat', 'r') as procfile:
            cputimes = procfile.readline()
            cputotal = 0
            # count from /proc/stat: user, nice, system, idle, iowait, irc, softirq, steal, guest
            for value in cputimes.split(' ')[2:]:
                value = int(value)
                cputotal = (cputotal + value)

            return int(cputotal) * CONV_RATE

    def get_raw_cpu_stats(self):
        ''' Reads the raw system cpu usage from proc '''
        (user_usage, _, total_usage, percpu_usage) = self.get_raw_cpuacct_stat()
        system_cpu_usage = CgroupUtil.get_raw_system_cpu_usage()

        return {
            'cpu_usage': {
                'usage_in_usermode': user_usage,
                'total_usage': total_usage,
                'percpu_usage': percpu_usage,
            },

            'system_cpu_usage': system_cpu_usage
        }

    def raw_stats(self):
        ''' Combines all of the raw stats into a dictionary.
            This intentionally has the same format as docker-py's .stats() call.
        '''
        retval = {}

        retval['memory_stats'] = self.get_raw_memory_stats()

        retval['precpu_stats'] = self.get_raw_cpu_stats()

        time.sleep(1)

        retval['cpu_stats'] = self.get_raw_cpu_stats()

        return retval



    @staticmethod
    def raw_stats_to_dtos(raw_stats):
        ''' Takes raw stats dictionand and returns the cpu and memory stats as DTOs '''
        raw_mem_stats = raw_stats['memory_stats']

        mem_used = raw_mem_stats['usage']
        mem_limit = raw_mem_stats['limit']
        mem_failcnt = raw_mem_stats['failcnt']

        mem_limit_used_pct = (float(mem_used) / float(mem_limit)) * 100

        mem_stats = MemoryStats(used=mem_used,
                                limit=mem_limit,
                                limit_used_pct=mem_limit_used_pct,
                                failcnt=mem_failcnt
                               )


        cpu_used_pct = CgroupUtil.cpu_stats_to_cpu_pct(raw_stats)
        cpu_stats = CpuStats(used_pct=cpu_used_pct)

        return (cpu_stats, mem_stats)
