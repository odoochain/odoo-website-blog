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
        'views/website_blog_view.xml',
        'data/ir_config_parameter.xml',
        'data/server_action.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
