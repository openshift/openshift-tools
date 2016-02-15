#!/usr/bin/env python
"""
 This is a simple script to copy an EC2 AMI to all regions.
 It will then print out the region and the ami id in that region.

 NOTE: Because there is no good way to ensure that the AMI's are the same in each region,
  this script relies on the AMI name to macth.  So, there is a possibility that the ami
  is not the same, but the names are.

 NOTE: If a copy is done, it may take a few (10) minutes for the ami to appear in the remote
  region.  If this script is run again, too quickly, it will create another copy in the same
  remote region.  Trust the output, the AMI's will appear

 This assumes that your AWS credentials are loaded in the ENV variables:
  AWS_ACCESS_KEY_ID=xxxx
  AWS_SECRET_ACCESS_KEY=xxxx

 Be default it will assume the ami is in the us-east-1 region. This can be overidden with
  a 2nd conditional variable

 Usage:

 # copy ami-id to all regions (ami-12345678 is in us-east-1)
 ec2_copy_ami_to_regions.py ami-12345678

 # copy ami-id to all regions (ami-12345678 is in us-west-1)
 ec2_copy_ami_to_regions.py ami-12345678 us-west-1
"""
# Ignoring module name
# pylint: disable=invalid-name

import boto.ec2
import sys

def check_arguments():
    """ ensure that the ami was pass in on the command line """

    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print "Usage:"
        print "   %s <ami-id>" % sys.argv[0]
        print "   %s <ami-id> <ec2-source-region> (Region is optional, default: us-east-1)" % sys.argv[0]
        print
        print "example: %s ami-1245678" % sys.argv[0]
        print "example: %s ami-1245678 us-west-1" % sys.argv[0]
        sys.exit(10)
    else:
        if sys.argv[1].startswith("ami-"):
            return True

def main():
    """ main function """

    check_arguments()

    if len(sys.argv) == 3:
        source_region = sys.argv[2]
    else:
        source_region = 'us-east-1'

    source_ami = sys.argv[1]

    regions_to_copy = ['us-east-1',
                       'us-west-1',
                       'us-west-2',
                       'eu-west-1',
                       'ap-southeast-1',
                       'ap-southeast-2',
                       'eu-central-1',
                       'eu-central-1',
                      ]

    conn = boto.ec2.connect_to_region(source_region)
    original_ami_id = conn.get_all_images(image_ids=source_ami)
    original_ami_name = original_ami_id[0].name


    ami_dict = {}
    for region in regions_to_copy:
        conn = boto.ec2.connect_to_region(region)
        ami = conn.get_all_images(filters={'name': original_ami_name})
        if not ami:
            ami = conn.copy_image(source_region, source_ami)
            ami_dict[region] = ami.image_id
        else:
            ami_dict[region] = ami[0].id
        print "%s: %s" %(region, ami)

    print
    print "Yaml output:"
    print
    print "g_ec2_image:"
    for region, ami_id in ami_dict.iteritems():
        print "  %s: %s" %(region, ami_id)

if __name__ == "__main__":
    main()
