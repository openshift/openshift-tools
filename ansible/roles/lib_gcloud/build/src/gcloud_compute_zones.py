# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class GcloudComputeZones(GcloudCLI):
    ''' Class to wrap the gcloud compute zones command'''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self, region=None, verbose=False):
        ''' Constructor for gcloud resource '''
        super(GcloudComputeZones, self).__init__()
        self._region = region
        self.verbose = verbose

    @property
    def region(self):
        '''property for region'''
        return self._region

    def list_zones(self):
        '''return a list of zones'''
        results = self._list_zones()

        if results['returncode'] == 0 and self.region:
            zones = []
            for zone in results['results']:
                if self.region == zone['region']:
                    zones.append(zone)
            results['results'] = zones

        return results

