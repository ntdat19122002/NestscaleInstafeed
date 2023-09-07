import json

import requests

from odoo import fields, api, models


class TiktokUser(models.Model):
    _name = "tiktok.user"

    admin = fields.Many2one('res.users')
    access_token = fields.Char()
    open_id = fields.Char()
    union_id = fields.Char()
    profile_img = fields.Char()
    username = fields.Char()
    post_id = fields.One2many('tiktok.post','user_id')

class TiktokPost(models.Model):
    _name = "tiktok.post"

    user_id = fields.Many2one('tiktok.user')
    post_id = fields.Char()
    embed_link = fields.Char()
    share_url = fields.Char()
    cover_img = fields.Char()
    title = fields.Char()
    like_count = fields.Integer()
    comment_count = fields.Integer()
    share_count = fields.Integer()

    hotspot_ids = fields.Many2many('shopify.hotspot', 'tiktok_hotspot_rel')

    def reset_cover_img(self):
        posts = self.env['tiktok.post'].sudo().search([])
        for post in posts:
            video_uri = 'https://open-api.tiktok.com/video/query/'
            video_param = {
                "access_token": post.user_id.access_token,
                "filters": {
                    "video_ids": [post['post_id']]
                },
                "fields": ["id", "title","cover_image_url"]
            }
            video = requests.post(video_uri, data=json.dumps(video_param),
                                       headers={'Content-Type': 'application/json'})
            video_cover_img = video.json()['data']['videos'][0]['cover_image_url']
            post.write({
                'cover_img':video_cover_img
            })