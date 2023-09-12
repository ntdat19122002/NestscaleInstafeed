import json
import traceback
from urllib.parse import urlencode

import requests
import werkzeug

from odoo import http
from odoo.http import request, _logger
from ..instance.TiktokAPI import TiktokAPI

class TiktokController(http.Controller):
    @http.route('/tiktok/instafeed/auth', auth='public')
    def tiktok_auth(self):
        tiktok_client_key = request.env['ir.config_parameter'].sudo().get_param('instafeed.tiktok_client_key')
        tiktok_redirect_uri = 'https://odoo.website/tiktok/instafeed/finalize/'

        url = 'https://www.tiktok.com/auth/authorize?'

        params = {
            'client_key':tiktok_client_key,
            'scope':'user.info.basic,video.list',
            'response_type':'code',
            'redirect_uri':tiktok_redirect_uri
        }

        return werkzeug.utils.redirect(url+urlencode(params))

    @http.route('/tiktok/instafeed/finalize', auth='public')
    #Todo: Thêm try catch
    def tiktok_finalize(self,**kw):
        try:
            tiktok_client_key = request.env['ir.config_parameter'].sudo().get_param('instafeed.tiktok_client_key')
            tiktok_secret_key = request.env['ir.config_parameter'].sudo().get_param('instafeed.tiktok_secret_key')
            tiktok = TiktokAPI(request)
            if 'code' in kw:

                token = tiktok.get_tiktok_access_token(kw['code']).json()['data']['access_token']

                user_info_uri = 'https://open-api.tiktok.com/user/info/'
                user_info_param = {
                    "fields": ["open_id", "union_id", "avatar_url","display_name"],
                    'access_token':token
                }
                user_info = requests.post(user_info_uri,data = json.dumps(user_info_param), headers={'Content-Type': 'application/json'})
                user_info_decode = user_info.json()['data']['user']
                tikok_user = request.env['tiktok.user'].sudo().search([('open_id','=',user_info_decode['open_id']),('union_id','=',user_info_decode['union_id'])],limit=1)
                if not tikok_user:
                    tikok_user = request.env['tiktok.user'].sudo().create({
                        'open_id':user_info_decode['open_id'],
                        'access_token': token,
                        'union_id':user_info_decode['union_id'],
                        'profile_img':user_info_decode['avatar_url'],
                        'username':user_info_decode['display_name'],
                        'admin':request.env.user.id
                    })
                else:
                    tikok_user.write({
                        'access_token': token,
                        'profile_img': user_info_decode['avatar_url'],
                        'username': user_info_decode['display_name'],
                        'admin': request.env.user.id
                    })

                video_list_uri = 'https://open-api.tiktok.com/video/list/'
                video_list_param = {
                    "access_token": token,
                    "fields": ["id", "embed_link", "title","like_count","comment_count","share_count","cover_image_url","share_url"]
                }
                video_list = requests.post(video_list_uri, data=json.dumps(video_list_param),headers={'Content-Type': 'application/json'})
                video_list_decode = video_list.json()['data']['videos']
                for video in video_list_decode:
                    video_search = request.env['tiktok.post'].sudo().search([('post_id','=',video['id'])])
                    if 'embed_link' in video:
                        if not video_search:
                            request.env['tiktok.post'].sudo().create({
                                'user_id':tikok_user.id,
                                'post_id':video['id'],
                                'cover_img': video['cover_image_url'],
                                'embed_link':video['embed_link'],
                                'share_url':video['share_url'],
                                'title':video['title'],
                                'like_count':video['like_count'],
                                'comment_count':video['comment_count'],
                                'share_count':video['share_count'],
                            })
                        else:
                            video_search.write({
                                'user_id': tikok_user.id,
                                'cover_img': video['cover_image_url'],
                                'embed_link': video['embed_link'],
                                'share_url': video['share_url'],
                                'title': video['title'],
                                'like_count': video['like_count'],
                                'comment_count': video['comment_count'],
                                'share_count': video['share_count'],
                            })
            return werkzeug.utils.redirect('https://odoo.website/')
        except Exception as e:
            _logger.error(traceback.format_exc())
            return werkzeug.utils.redirect('https://nestscale.com/contact-us')

    #Todo: Bỏ. Code thừa 👌

    # @http.route('/tiktok/like', type="json", auth='public', cors='*', method=['POST'])
    # def get_number_of_like_tiktok(self, **kw):
    #     post = request.env['tiktok.post'].sudo().search([('id', '=', kw['post_id'])])
    #     return json.dumps(post.like_count)
    #
    # @http.route('/tiktok/comments', type="json", auth='public', cors='*', method=['POST'])
    # def get_number_of_comments_tiktok(self, **kw):
    #     post = request.env['tiktok.post'].sudo().search([('id', '=', kw['post_id'])])
    #     return json.dumps(post.comment_count)
