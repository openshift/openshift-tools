# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class GcloudComputeAddresses(GcloudCLI):
    ''' Class to wrap the gcloud compute addresses command'''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 aname=None,
                 desc=None,
                 region=None,
                 address=None,
                 isglobal=False,
                 verbose=False):
        ''' Constructor for gcloud resource '''
        super(GcloudComputeAddresses, self).__init__()
        self.name = aname
        self.desc = desc
        self.region = region
        self.isglobal = isglobal
        self.address = address
        self.verbose = verbose

    def list_addresses(self, address_name=None):
        '''return a list of addresses'''
        results = self._list_addresses(address_name)
        if results['returncode'] == 0:
            if not address_name:
                rval = []
                for addr in results['results'].strip().split('\n')[1:]:
                    aname, region, aip, status = addr.split()
                    rval.append({'name': aname, 'region': region, 'address': aip, 'status': status})
                results['results'] = rval

            else:
                results['results'] = yaml.load(results['results'])

        return results

    def exists(self):
        ''' return whether an address exists '''
        addresses = self.list_addresses()
        if addresses['returncode'] != 0:
            if 'was not found' in addresses['stderr']:
                addresses['returncode'] = 0
                return addresses
            raise GcloudCLIError('Something went wrong.  Results: %s' % addresses['stderr'])

        return any([self.name == addr['name'] for addr in addresses['results']])

    def delete_address(self):
        '''delete an address'''
        return self._delete_address(self.name)

    def create_address(self):
        '''create an address'''
        address_info = {}
        address_info['description'] = self.desc
        address_info['region'] = self.region
        return self._create_address(self.name, address_info, self.address, self.isglobal)

