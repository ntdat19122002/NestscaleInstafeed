import requests
import werkzeug

from odoo import http
from odoo.http import request
from ..instance.InstagramAPI import InstagramAPI

SCOPE = 'pages_show_list,instagram_basic,pages_manage_engagement,business_management,pages_messaging'

class FacebookController(http.Controller):
    @http.route('/facebook/instafeed/auth', auth='public')
    def meta_auth(self):
        facebook_client_id = request.env['ir.config_parameter'].sudo().get_param('instafeed.facebook_client_id')
        facebook_redirect_uri = request.env['ir.config_parameter'].sudo().get_param('instafeed.facebook_redirect_uri')

        return werkzeug.utils.redirect(f'https://www.facebook.com/v17.0/dialog/oauth?client_id={facebook_client_id}&redirect_uri={facebook_redirect_uri}&scope={SCOPE}')


    @http.route('/facebook/instafeed/oauth', auth='public')
    def meta_callback(self,**kw):
        instagram = InstagramAPI(request)

        facebook_token_data = instagram.get_user_token_facebook(kw['code'])
        facebook_token = facebook_token_data.json()['access_token']

        app_access_token_data = instagram.get_app_token_facebook()
        app_access_token = app_access_token_data.json()['access_token']

        facebook_user_data = instagram.get_facebook_user_data(facebook_token,app_access_token)
        facebook_user = facebook_user_data.json()['data']

        current_facebook_user = request.env['facebook.user'].sudo().search([('user_id','=',facebook_user['user_id'])])
        if not current_facebook_user:
            facebook_new = request.env['facebook.user'].sudo().create({
                'admin':request.env.user.id,
                'user_token':facebook_token,
                'app_token': app_access_token,
                'user_id': facebook_user['user_id'],
                'code': kw['code'],
            })
            facebook_new_id = facebook_new.id
        else:
            current_facebook_user.sudo().write({
                'admin': request.env.user.id,
                'user_token': facebook_token,
                'app_token': app_access_token,
                'code': kw['code'],
            })
            facebook_new_id = current_facebook_user.id

        page_data = instagram.get_page_data_facebook(facebook_token)
        page_data_id = page_data.json()['data'][0]['id']

        insta_data = instagram.get_insta_data(page_data_id,facebook_token)
        insta_id = insta_data.json()["instagram_business_account"]['id']

        user_insta_data =  instagram.get_user_insta_data(insta_id,facebook_token).json()

        insta_user = request.env['instagram.user'].sudo().search([('instagram_id','=',insta_id)],limit=1)
        if not insta_user:
            insta_user = request.env['instagram.user'].sudo().create({
                'instagram_id':insta_id,
                'facebook_id':facebook_new_id,
                'profile_img':user_insta_data['profile_picture_url'],
                'username':user_insta_data['name']
            })

            current_facebook_user.sudo().write({
                'instagram_user_id':insta_user.id
            })
        else:
            insta_user.sudo().write({
                'facebook_id': facebook_new_id,
                'profile_img': user_insta_data['profile_picture_url'],
                'username': user_insta_data['name']
            })

            current_facebook_user.sudo().write({
                'instagram_user_id': insta_user.id
            })

        insta_media_fields = 'media_url,permalink,media_type,thumbnail_url'
        insta_media_data = instagram.get_insta_media_data(insta_id,insta_media_fields,facebook_token).json()
        for post in insta_media_data['data']:
            post_search = request.env['instagram.post'].sudo().search([('post_id','=',post['id'])],limit=1)
            if not post_search:
                post_search = request.env['instagram.post'].sudo().create({
                    'post_id':post['id'],
                    'instagram_user_id':insta_user.id,
                    'media_url':post['media_url'],
                    'link_to_post': post['permalink'],
                    'media_type':post['media_type']
                })
            else:
                post_search.sudo().write({
                    'instagram_user_id': insta_user.id,
                    'media_url': post['media_url'],
                    'link_to_post': post['permalink'],
                    'media_type':post['media_type'],
                })

            if post['media_type'] == 'VIDEO':
                post_search.write({
                    'thumbnail_url': post['thumbnail_url']
                })

        return werkzeug.utils.redirect('https://odoo.website/apps/instafeed')