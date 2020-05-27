#!/usr/bin/env python
import yaml, sys

def find_all_env_lists( obj, fn ):
    if isinstance( obj, dict ):
        for k, v in obj.iteritems():
            if (k=="env" and isinstance(v, list)):
                for item in v:
                    if "value" in item:
                        item["value"] = fn( item["name"], item["value"] )
            elif isinstance( v, ( dict, list, tuple ) ):
                find_all_env_lists( v, fn )
    elif isinstance(obj, (list,tuple)):
        for item in obj:
            find_all_env_lists(item, fn)

    return obj

def redact_secure_env_vars( key, value ):
    if ("PASSWORD" in key or "PASSWD" in key):
        value = "***REDACTED***"
    return value

y=yaml.safe_load(sys.stdin);

print( yaml.dump(find_all_env_lists(y, redact_secure_env_vars)) )
