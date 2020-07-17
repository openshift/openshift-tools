#!/usr/bin/env python2
"""
Perform checks on RH SSO
"""

import sys
import subprocess
import traceback
import yaml

# pylint: disable=broad-except
# pylint: disable=no-self-use

class DictQuery(dict):
    """class DictQuery"""
    def get(self, path, default=None):
        keys = path.split("/")
        val = None

        for key in keys:
            if val:
                if isinstance(val, list):
                    val = [v.get(key, default) if v else None for v in list(val)]
                else:
                    val = val.get(key, default)
            else:
                val = dict.get(self, key, default)

            if not val:
                break

        return val

class RHMICheckRHSSO:
    """class RHMICheckRHSSO"""
    def __init__(self):
        self._results = []

    def oc_run(self, *args):
        """helper cmd for oc"""
        cmd = ("oc",) + args

        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)

        return out

    def get_rhsso_client_secret(self):
        """get_rhsso_client_secret"""
        val = ""
        try:
            val = self.oc_run("get", "secret", "openshift-client-client",
                              "-n", "openshift-sso", "--template", "{{.data.secret | base64decode }}")
        except subprocess.CalledProcessError as exception:
            sys.stderr.write("Unable to retrieve client secret for rhsso instance."\
                             " oc returned: %s" % (exception.output))
            sys.exit(-1)

        return val

    def get_masters(self):
        """get_masters"""
        pods = []

        try:
            res = self.oc_run("get", "pod", "-l", "openshift.io/component=api",
                              "--no-headers", "-n", "kube-system", "-o",
                              "custom-columns=:.metadata.name,:.status.hostIP")

            for line in res.splitlines():
                pod, node = line.split()
                pods.append((pod, node))
        except subprocess.CalledProcessError as exception:
            sys.stderr.write("Failed to retrieve list of master api pods."\
                             " oc returned: %s" % (exception.output))
            sys.exit(-1)

        return pods

    def check_config(self):
        """check_config"""
        expected_secret = self.get_rhsso_client_secret()

        master_pods = self.get_masters()

        for pod, node in master_pods:
            try:
                master_config = self.oc_run("-n", "kube-system", "exec", pod, "cat",
                                            "/etc/origin/master/master-config.yaml")

                yaml_data = yaml.safe_load(master_config)

                rhsso = None

                for idp in yaml_data["oauthConfig"]["identityProviders"]:
                    if idp["name"] == "rh_sso":
                        rhsso = idp
                        break

                if rhsso:
                    provider = "found"
                    provider_secret = DictQuery(rhsso).get("provider/clientSecret", None)

                    secret = "ok" if provider_secret == expected_secret else "mismatch"
                else:
                    provider = "missing"
                    secret = "n/a"
            except Exception:
                provider = secret = "fail"

            self._results.append((node, provider, secret))

    def report(self):
        """report"""
        line_format = "%-20s %-10s %-30s"

        # print headers
        print(line_format % ("MASTER_NODE", "RHSSO", "SECRET"))

        return_code = 0
        for node, provider, secret in self._results:
            print(line_format % (node, provider, secret))
            if secret != "ok":
                return_code = 1

        return return_code

    def main(self):
        """main"""
        self.check_config()

        real_code = self.report()

        # swallow and report the actual return code; otherwise, the devaccess wrapper
        # would hide any useful error info we printed to STDERR
        print("overall result: %s" % (("ok" if real_code == 0 else "fail")))

if __name__ == "__main__":
    RETURN_CODE = 0

    try:
        CHECK_SSO = RHMICheckRHSSO()
        CHECK_SSO.main()
    except Exception:
        traceback.print_exc()
    finally:
        sys.exit(RETURN_CODE)
