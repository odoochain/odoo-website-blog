# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Website Blog App',
    'category': 'Website/Website',
    'sequence': 200,
    'website': 'https://www.vertlab.se',
    'summary': 'Website Blog App',
    'author': 'Vertel AB',
    'version': '1.0',
    'description': "",
    'depends': ['website_blog'],
    'data': [
        'views/snippets/snippets.xml',
        'views/website_blog_view.xml',
        'views/website_blog_templates.xml',
        'views/app_templates.xml',
        'views/assets.xml',
        'data/ir_config_parameter.xml',
        'data/server_action.xml',
        'data/data.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
