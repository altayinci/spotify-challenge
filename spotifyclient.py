import requests
import base64
import json


class SpotifyClient(object):
    basic_auth_url = 'https://accounts.spotify.com/api/token'

    def __init__(self, client_id, client_secret, base_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url

    def get_basic_auth(self):

        raw_str = '{}:{}'.format(self.client_id, self.client_secret)
        encoded_str = base64.b64encode(raw_str)

        auth_key = '{} {}'.format('Basic', encoded_str)
        headers = {
            'Authorization': auth_key,
        }
        data = {
            'grant_type': 'client_credentials',
        }
        method = 'POST'

        return self.call(url=self.basic_auth_url, headers=headers, data=data, method=method)

    def get_bearer_auth(self):

        basic_auth_resp = self.get_basic_auth()
        json_resp = json.loads(basic_auth_resp.text)
        token = json_resp['access_token']

        auth = '{} {}'.format('Bearer', token)
        bearer_header = {
            'Authorization': auth,
        }

        return bearer_header

    # For tracks, we need to have singer id.
    # For getting singer id, firstly make a search with name.
    # After search, we obtains more than one singer but first result probably is our singer.
    # We can get singer id only with this method.

    def get_singer(self, data):

        search_singers_fragment = "search?"
        search_url = self.base_url + search_singers_fragment + "&".join(["%s=%s" % (k, v) for k, v in data.iteritems()])

        headers = self.get_bearer_auth()

        search_response = self.call(url=search_url, method='GET', headers=headers)

        search_data = json.loads(search_response.text)

        singer_id = search_data['artists']['items'][0]['uri'].split(':')[-1]

        return singer_id, headers

    def get_top_tracks(self, data):

        singer_id, headers = self.get_singer(data)
        get_artist_fragment = "artists"
        get_top_tracks_fragment = "top-tracks"
        market = 'US'
        top_tracks_url = '{}{}/{}/{}?country={}'.format(self.base_url, get_artist_fragment, singer_id,
                                                        get_top_tracks_fragment, market)

        top_tracks_response = self.call(method='GET', headers=headers, url=top_tracks_url)

        return json.loads(top_tracks_response.text)

    def call(self, url, headers, data=None, method=None):

        try:
            response = requests.request(
                method=method, url=url, data=data, headers=headers
            )
            response.raise_for_status()
        except Exception as e:
            if response:
                error_message = json.loads(response.text)['error']['message']
                raise Exception(error_message)
            else:
                raise Exception(e.message)

        return response
