from odoo import models, fields, api, _


class BlogPost(models.Model):
    _inherit = 'blog.post'

    libsyn_episode = fields.Char(string="Episode")
