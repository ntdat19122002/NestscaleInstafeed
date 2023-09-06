import json

import requests

from odoo import http
from odoo.http import request


class InstagramController(http.Controller):
    @http.route('/instagram/like', type="json", auth='user', cors='*', method=['POST'])
    def get_number_of_like(self,**kw):
        post = request.env['instagram.post'].sudo().search([('id','=',kw['post_id'])])
        facebook_token = post.instagram_user_id.facebook_id.user_token
        like_count = requests.get(f"https://graph.facebook.com/v17.0/{post['post_id']}?fields=like_count&access_token={facebook_token}").json()['like_count']
        return json.dumps(like_count)

    @http.route('/instagram/comments', type="json", auth='user', cors='*', method=['POST'])
    def get_number_of_comments(self,**kw):
        post = request.env['instagram.post'].sudo().search([('id', '=', kw['post_id'])])
        facebook_token = post.instagram_user_id.facebook_id.user_token
        comments_count = requests.get(f"https://graph.facebook.com/v17.0/{post['post_id']}?fields=comments_count&access_token={facebook_token}").json()['comments_count']
        return json.dumps(comments_count)

            

