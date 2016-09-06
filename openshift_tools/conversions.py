# vim: expandtab:tabstop=4:shiftwidth=4

''' Purpose is to provide some useful functions for converting things
    like bytes in Ki/K/Mi/M units and milicore CPU units
'''

class ConversionException(Exception):
    ''' Module's exceptions '''
    pass

def to_milicores(num):
    ''' take an OpenShift CPU limit/request and convert to milicores '''

    if 'm' in num:
        cpu_num = int(num.rstrip('m'))
    else:
        cpu_num = int(num) * 1000

    return cpu_num

def to_bytes(num):
    ''' convert Ki, Mi... to bytes '''
    import string

    num_bytes = 0
    if num.endswith('Gi'):
        num_bytes = int(num.rstrip(string.ascii_letters)) * (1024 ** 3)
    elif num.endswith('G'):
        num_bytes = int(num.rstrip(string.ascii_letters)) * (1000 ** 3)
    elif num.endswith('Mi'):
        num_bytes = int(num.rstrip(string.ascii_letters)) * 1024 * 1024
    elif num.endswith('M') or num.endswith('m'):
        num_bytes = int(num.rstrip(string.ascii_letters)) * 1000 * 1000
    elif num.endswith('Ki'):
        num_bytes = int(num.rstrip(string.ascii_letters)) * 1024
    elif num.endswith('K') or num.endswith('k'):
        num_bytes = int(num.rstrip(string.ascii_letters)) * 1000
    else:
        num_bytes = int(num)

    return num_bytes
