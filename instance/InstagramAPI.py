import requests

SCOPE = 'pages_show_list,instagram_basic,pages_manage_engagement,business_management,pages_messaging'
class InstagramAPI(object):
    facebook_client_id = None
    facebook_redirect_uri = None
    facebook_secret = None

    def __init__(self,request):
        self.facebook_client_id = request.env['ir.config_parameter'].sudo().get_param('instafeed.facebook_client_id')
        self.facebook_redirect_uri = request.env['ir.config_parameter'].sudo().get_param('instafeed.facebook_redirect_uri')
        self.facebook_secret = request.env['ir.config_parameter'].sudo().get_param('instafeed.facebook_secret')

    def get_user_token_facebook(self,code):
        get_token_uri = ('https://graph.facebook.com/v17.0/oauth/access_token')
        get_token_param = {
            'redirect_uri': self.facebook_redirect_uri,
            'client_id': self.facebook_client_id,
            'client_secret': self.facebook_secret,
            'code': code
        }

        return requests.post(get_token_uri, get_token_param)

    def get_app_token_facebook(self):
        uri = 'https://graph.facebook.com/oauth/access_token'
        param = {
            'client_id' : self.facebook_client_id,
            'client_secret':self.facebook_secret,
            'grant_type' : 'client_credentials'
        }
        return requests.get(uri,param)

    def get_facebook_user_data(self,access_token,app_access_token):
        return requests.get(f'https://graph.facebook.com/debug_token?input_token={access_token}&access_token={app_access_token}')