# pylint: skip-file

# pylint: disable=too-many-instance-attributes
class GcloudComputeImage(GcloudCLI):
    ''' Class to wrap the gcloud compute images command'''

    # pylint allows 5
    # pylint: disable=too-many-arguments
    def __init__(self,
                 iname=None,
                 desc=None,
                 family=None,
                 licenses=None,
                 source_disk=None,
                 source_disk_zone=None,
                 source_uri=None,
                 verbose=False):
        ''' Constructor for gcloud resource '''
        super(GcloudComputeImage, self).__init__()
        self.image_name = iname
        self.desc = desc
        self.family = family
        self.licenses = licenses
        self.source_disk = source_disk
        self.source_disk_zone = source_disk_zone
        self.source_uri = source_uri
        self.verbose = verbose

    def list_images(self, image_name=None):
        '''return a list of images'''
        results = self._list_images(image_name)
        if results['returncode'] == 0:
            results['results'] = results['results'].strip().split('\n')[1:]

        return results

    def exists(self):
        ''' return whether an image exists '''
        images = self.list_images()
        if images['returncode'] != 0:
            if 'was not found' in images['stderr']:
                images['returncode'] = 0
                return images
            raise GcloudCLIError('Something went wrong.  Results: %s' % images['stderr'])

        return any([self.image_name in line for line in images['results']])

    def delete_image(self):
        '''delete an image'''
        return self._delete_image(self.image_name)

    def create_image(self):
        '''create an image'''
        image_info = {}
        image_info['description'] = self.desc
        image_info['family'] = self.family
        image_info['licenses'] = self.licenses
        image_info['source-disk'] = self.source_disk
        image_info['source-disk-zone'] = self.source_disk_zone
        image_info['source-uri'] = self.source_uri
        return self._create_image(self.image_name, image_info)

