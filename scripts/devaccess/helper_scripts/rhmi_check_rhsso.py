#!/usr/bin/python2
import json
import sys
import yaml
import subprocess
import os
import traceback

class DictQuery(dict):
  def get(self, path, default = None):
    keys = path.split("/")
    val = None

    for key in keys:
      if val:
        if isinstance(val, list):
          val = [ v.get(key, default) if v else None for v in val]
        else:
          val = val.get(key, default)
      else:
        val = dict.get(self, key, default)

      if not val:
        break;

    return val

class RHMICheckRHSSO(object):
  def __init__(self):
    self._results = []

  def oc_run(self, *args):
    cmd = ("oc",) + args;

    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)

    return out

  def get_rhsso_client_secret(self):
    val = ""
    try:
      val = self.oc_run("get", "secret", "openshift-client-client","-n","openshift-sso","--template","{{.data.secret | base64decode }}")
    except subprocess.CalledProcessError as e:
      print >> sys.stderr, "Unable to retrieve client secret for rhsso instance.  oc returned: %s" % (e.output)
      sys.exit(-1)

    return val

  def get_masters(self):
    pods = []

    try:
      res = self.oc_run("get", "pod", "-l", "openshift.io/component=api", "--no-headers", "-n", "kube-system", "-o", "custom-columns=:.metadata.name,:.status.hostIP")

      for line in res.splitlines():
        pod, node = line.split()
        pods.append((pod, node))
    except subprocess.CalledProcessError as e:
      print >> sys.stderr, "Failed to retrieve list of master api pods.  oc returned: %s" % (e.output)
      sys.exit(-1)

    return pods

  def check_config(self):
    expectedSecret = self.get_rhsso_client_secret()

    masterPods = self.get_masters()

    for pod, node in masterPods:
      try:
        masterConfig = self.oc_run("-n","kube-system","exec",pod,"cat","/etc/origin/master/master-config.yaml")

        y = yaml.safe_load(masterConfig)

        rhsso = None

        for idp in y["oauthConfig"]["identityProviders"]:
          if idp["name"] == "rh_sso":
            rhsso = idp
            break

        if rhsso:
          provider = "found"
          providerSecret = DictQuery(rhsso).get("provider/clientSecret", None)

          secret = "ok" if providerSecret == expectedSecret else "mismatch"
        else:
          provider = "missing"
          secret = "n/a"
      except:
        provider = secret = "fail"

      self._results.append((node, provider, secret))

  def report(self):
    lineFormat = "%-20s %-10s %-30s"

    # print headers
    print(lineFormat % ("MASTER_NODE","RHSSO","SECRET"))

    rc = 0
    for node, provider, secret in self._results:
      print (lineFormat % (node, provider, secret))
      if secret != "ok":
        rc = 1

    return rc

  def main(self):
    self.check_config()

    realCode = self.report()

    # swallow and report the actual return code; otherwise, the devaccess wrapper
    # would hide any useful error info we printed to STDERR
    print("overall result: %s" % (("ok" if realCode == 0 else "fail")))

if __name__ == "__main__":
  code = 0

  try:
    check = RHMICheckRHSSO()
    check.main()
  except:
    traceback.print_exc()
  finally:
    sys.exit(code)
