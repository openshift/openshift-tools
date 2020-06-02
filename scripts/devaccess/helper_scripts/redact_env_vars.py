#!/usr/bin/env python
"""
This script performs inline filtering of the yaml output of an openshift resource
and redacts the values of env vars likely to contain unfiltered passwords
"""
import sys
import yaml
#pylint: disable=invalid-name
#pylint: disable=superfluous-parens
def find_all_env_lists(obj, modify_fn):
    """Recursive search obj for env lists and call a function for each of the members"""
    if isinstance(obj, dict):
        for k, val in obj.iteritems():
            if (k == "env" and isinstance(val, list)):
                for item in val:
                    if "value" in item:
                        item["value"] = modify_fn(item["name"], item["value"])
            elif isinstance(val, (dict, list, tuple)):
                find_all_env_lists(val, modify_fn)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            find_all_env_lists(item, modify_fn)

    return obj

def redact_secure_env_vars(key, value):
    """Redacts values of probable password env var."""
    if ("PASSWORD" in key or "PASSWD" in key):
        value = "***REDACTED***"
    return value

y = yaml.safe_load(sys.stdin)

print(yaml.dump(find_all_env_lists(y, redact_secure_env_vars)))
