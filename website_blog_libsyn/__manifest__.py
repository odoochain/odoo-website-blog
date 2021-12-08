# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Libsyn Blogs',
    'category': 'Website/Website',
    'sequence': 200,
    'website': 'https://www.vertlab.se',
    'summary': 'Add Libsyn podcast to blog',
    'version': '1.0',
    'description': "",
    'depends': ['website_blog'],
    'data': [
        'views/website_blog_views.xml',
        'views/website_blog_templates.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
