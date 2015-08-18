import requests
import os
import json
import time
import logging

from JumpScale import j


ActionsBase = j.atyourservice.getActionsBaseClass()


class Actions(ActionsBase):
    ENDPOINT_CONFIG = '/rest/system/config'
    ENDPOINT_RESTART = '/rest/system/restart'
    ENDPOINT_STATUS = '/rest/system/status'

    def get_url(self, service_obj, endpoint):
        port = service_obj.hrd.get('instance.param.port')
        return 'http://localhost:{port}{endpoint}'.format(
            port=port,
            endpoint=endpoint
        )

    def add_folder(self, service_obj, folder_id, path):
        sessions = requests.Session()

        headers = {
            'content-type': 'application/json'
        }

        config_url = self.get_url(service_obj, self.ENDPOINT_CONFIG)

        _errors = 0
        while True:
            try:
                response = sessions.get(config_url)
                if not response.ok:
                    raise Exception('Invalid response from syncthing: %s' % response.reason)
                else:
                    break
            except:
                _errors += 1
                if _errors >= 3:
                    raise
                seconds = 3 * _errors
                logging.info('Error retreiving syncthing config, retrying in %s seconds', seconds)
                time.sleep(seconds)

        config = response.json()

        local_device_id = response.headers['x-syncthing-id']
        # Get API key for future use
        api_key = config['gui']['apiKey']
        headers['X-API-Key'] = api_key

        # add device to shared folder.
        folders = filter(lambda f: f['id'] == folder_id, config['folders'])

        dirty = False

        if not folders:
            # add folder.
            folder = {
                'autoNormalize': False,
                'copiers': 1,
                'devices': [{'deviceID': local_device_id}],
                'hashers': 0,
                'id': folder_id,
                'ignorePerms': False,
                'invalid': '',
                'order': 'random',
                'path': path,
                'pullers': 16,
                'readOnly': False,
                'rescanIntervalS': 60,
                'versioning': {'params': {}, 'type': ''}
            }

            if not os.path.isdir(path):
                os.makedirs(path, 0755)

            config['folders'].append(folder)
            dirty = True
        else:
            folder = folders[0]

        if not dirty:
            return

        response = sessions.post(config_url, data=json.dumps(config), headers=headers)
        if not response.ok:
            raise Exception('Failed to set syncthing configuration', response.reason)

        response = sessions.post(self.get_url(service_obj, self.ENDPOINT_RESTART), headers=headers)
        if not response.ok:
            raise Exception('Failed to restart syncthing', self.get_url(service_obj, self.ENDPOINT_RESTART),
                            response.reason)
