from odoo import http
import json
import shopify
from odoo.http import request


class WebhookController(http.Controller):
    @http.route('/webhook/orders_create/<int:id>',type='json', auth="public")
    def webhook_order_create(self,**kw):
        print(kw)
        return {}
    @http.route('/webhook/orders_update/<int:id>',type='json', auth="public")
    def webhook_order_update(self,**kw):
        print(kw)
        return {}
    @http.route('/webhook/products_create/<int:id>',type='json', auth="public")
    def webhook_product_create(self,**kw):
        print(request.jsonrequest)
        return {}

    #Todo: Viết webhook cập nhật tên sản phẩm. 👌
    @http.route('/webhook/products_update/<int:id>',type='json', auth="public")
    def webhook_product_update(self,**kw):
        product_update = request.jsonrequest
        hotspot = request.env['shopify.hotspot'].sudo().search([('shopify_id','=',product_update['admin_graphql_api_id'])],limit=1)
        if hotspot:
            hotspot.write({
                'title':product_update['title'],
                'image_url':product_update['image']['src']
            })

    @http.route('/webhook/uninstall/<int:id>',type='json', auth="public")
    def webhook_check(self,id,**kw):
        shop = request.env['shopify.shop'].browse(id)
        shop.init_shopify_session()
        shop.is_delete = True
        shop.destroy_scrip_tag()
        shop.destroy_webhook()
        return {}

