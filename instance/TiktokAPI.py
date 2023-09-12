import requests

class TiktokAPI(object):
    tiktok_client_key = None
    tiktok_secret_key = None

    def __init__(self,request):
        self.tiktok_client_key = request.env['ir.config_parameter'].sudo().get_param('instafeed.tiktok_client_key')
        self.tiktok_secret_key = request.env['ir.config_parameter'].sudo().get_param('instafeed.tiktok_secret_key')

    def get_tiktok_access_token(self,code):
        get_token_uri = 'https://open-api.tiktok.com/oauth/access_token/'
        get_token_param = {
            'client_key': self.tiktok_client_key,
            'client_secret': self.tiktok_secret_key,
            'code': code,
            'grant_type': 'authorization_code'
        }
        return requests.post(get_token_uri, get_token_param)