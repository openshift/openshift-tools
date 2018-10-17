#!/usr/bin/python
# vim: expandtab:tabstop=2:shiftwidth=2

import unittest
from oo_vpc_subnets_calc import *

class TestSubnetCalc(unittest.TestCase):

    def test_large_cidr_3az_3subnet(self):
        cidr_block = "172.16.0.0/16"
        num_of_subnets = 3
        num_avail_zones_in_region = 3
        expected_result = ["172.16.0.0/21", "172.16.8.0/21", "172.16.16.0/21"]
        results = calc_subnets(None, cidr_block, num_of_subnets, num_avail_zones_in_region)
        self.assertItemsEqual(expected_result, results, "Enough AZs for 3 subnet and large enough CIDR block")

    def test_small_cidr_3az_3subnet(self):
        cidr_block = "172.16.0.0/24"
        num_of_subnets = 3
        num_avail_zones_in_region = 3
        expected_result = ["172.16.0.0/26", "172.16.0.64/26", "172.16.0.128/26"]
        results = calc_subnets(None, cidr_block, num_of_subnets, num_avail_zones_in_region)
        self.assertItemsEqual(expected_result, results, "Enough AZs for 3 subnet and large enough CIDR block")

    def test_large_cidr_2az_3subnet(self):
        cidr_block = "172.16.0.0/16"
        num_of_subnets = 3
        num_avail_zones_in_region = 2
        expected_result = ["172.16.0.0/21"]
        results = calc_subnets(None, cidr_block, num_of_subnets, num_avail_zones_in_region)
        self.assertItemsEqual(expected_result, results, "Not enough AZs for 3 subnet but large enough CIDR block")

    def test_small_cidr_2az_3subnet(self):
        cidr_block = "172.16.0.0/24"
        num_of_subnets = 3
        num_avail_zones_in_region = 2
        expected_result = ["172.16.0.0/26"]
        results = calc_subnets(None, cidr_block, num_of_subnets, num_avail_zones_in_region)
        self.assertItemsEqual(expected_result, results, "Not enough AZs for 3 subnet but large enough CIDR block")


if __name__ == '__main__':
    unittest.main()
