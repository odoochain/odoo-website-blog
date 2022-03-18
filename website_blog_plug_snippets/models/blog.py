from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
import base64
import logging
import urllib.request
import os
import ast
import json
import re
_logger = logging.getLogger(__name__)
import traceback


class BlogPost(models.Model):
    _inherit = 'blog.post'

    is_plug = fields.Boolean(string='Is Plug Blogpost', default=False)
    
