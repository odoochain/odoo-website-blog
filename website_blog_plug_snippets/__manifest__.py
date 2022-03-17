# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Blog App Snippets',
    'category': 'Website/Website',
    'sequence': 200,
    'website': 'https://www.vertlab.se',
    'summary': 'Website Blog App',
    'author': 'Vertel AB',
    'version': '1.0',
    'description': "",
    'depends': ['website_blog'],
    'data': [
        'views/website_blog_view.xml',
        'views/website_blog_templates.xml',
        'views/app_templates.xml',
        'views/snippets/snippets.xml',
        'views/snippets/snip_plug_posts.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
