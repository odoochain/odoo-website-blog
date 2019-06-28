# -*- coding: utf-8 -*-


from datetime import datetime
import random
import json

import itertools

from odoo import api, models, fields, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.tools.translate import html_translate
from odoo.tools import html2plaintext


class Blog(models.Model):
    _inherit = 'blog.blog'

    banner = fields.Binary('Banner')
    icon = fields.Binary('Icon')



class BlogTagCategory(models.Model):
    _inherit = 'blog.tag.category'

    banner = fields.Binary('Banner')
    icon = fields.Binary('Icon')




class BlogPost(models.Model):
    _inherit = "blog.post"

    teaser_publish = fields.Boolean('Teaser Publish')   
    teaser_image = fields.Binary('Teaser Image')
    icon = fields.Binary('Icon')


    @api.model
    def teaser_get(self):
	return self.env['blog.post'].search([]) # Return a list of teasers for website sorted 

import werkzeug

from odoo import http
from odoo.http import request


class WebsiteUrl(http.Controller):
    @http.route('/website_blog_teaser/get', type='json', auth='user', methods=['POST'])
    def website_blog_teaser_get(self, **post):
        return [(t.name,t.teaser_image,t.icon) for t in request.env['blog.post'].teaser_get()] # return what we need may be add Blog/BlogTagCategory

