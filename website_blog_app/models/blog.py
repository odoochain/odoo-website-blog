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


class Blog(models.Model):
    _inherit = 'blog.blog'

    is_app = fields.Boolean(string="Is App")


class BlogPost(models.Model):
    _inherit = 'blog.post'

    is_app = fields.Boolean(string="Is App", related='blog_id.is_app')
    pod_id = fields.Integer(string="Pod Id")
    app_project = fields.Char(string="App Project")
    app_module = fields.Char(string="App Module")
    app_tree = fields.Char(string="Branch Tree")
    app_icon = fields.Binary(string="Icon")
    app_banner = fields.Binary(string="App Banner")
    app_summary = fields.Char(string="App Summary")
    app_category = fields.Many2one('ir.module.category', string="Category")
    app_description = fields.Text(string="App Description")
    app_manifest = fields.Char(string="App Manifest")
    app_index = fields.Html(string="App Index")

    def sync_module(self):
        git_url = self.env['ir.config_parameter'].sudo().get_param('GitHubBaseUrl')
        if not git_url:
            raise UserError(_("Git URL is not set"))
        if not self.app_project:
            raise UserError(_("No Git Project was specified"))
        if not self.app_module:
            raise UserError(_("No Module was specified"))
        if self.app_project and self.app_module:
            module_url = f"{git_url}/{self.app_project}/raw/{self.app_tree}/{self.app_module}"
            # get icon
            icon_data, icon_name = self._wget_sync(f"{module_url}/static/description/icon.png")
            if icon_data and icon_name:
                self.app_icon = self._create_attachment(icon_data, icon_name)
            # get banner
            banner_data, banner_name = self._wget_sync(f"{module_url}/static/images/main_screenshot.png")
            if banner_data and banner_name:
                self.app_banner = self._create_attachment(banner_data, banner_name)

            # manifest file
            # self._sync_manifest(f"{module_url}/__manifest__.py")

    def _sync_manifest(self, manifest_url):
        try:
            manifest_obj = urllib.request.urlopen(manifest_url)
            print(re.search(b'category', manifest_obj.read()).group())
        except Exception as e:
            _logger.warning(e)
            raise UserError(f'Something went wrong, exception: {e}')

    def _wget_sync(self, url):
        try:
            file_obj = urllib.request.urlopen(url)
            file_name = os.path.basename(url)
            return file_obj, file_name
        except Exception as e:
            _logger.warning(e)
            raise UserError(f'Something went wrong, exception: {e}')

    def _create_attachment(self, datas, name):
        return base64.encodebytes(datas.read())
