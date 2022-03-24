from odoo.exceptions import UserError, ValidationError
from odoo import models, fields, api, _
import base64
import logging
import urllib.request
from contextlib import closing
import os
import ast
import json
import re
import tempfile
_logger = logging.getLogger(__name__)
import traceback


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
    app_license = fields.Char(string="App License")
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
            self._sync_manifest(f"{module_url}/__manifest__.py")

    def _sync_manifest(self, manifest_url):
        try:
            manifest_obj = urllib.request.urlopen(manifest_url).read().decode('utf-8')
            manifest = re.sub(r'(?m)^ *#.*\n?', '', manifest_obj)
            if manifest:
                manifest = ast.literal_eval(manifest)
                self.app_license = manifest.get('license')
                self.app_summary = manifest.get('summary')
        except Exception as e:
            _logger.warning("".join(traceback.format_exc()))
            return None, None

    def _wget_sync(self, url):
        _logger.warning(f"{url=}")
        try:
            file_obj = urllib.request.urlopen(url)
            _logger.warning(f"{file_obj=}")
            file_name = os.path.basename(url)
            _logger.warning(f"{file_name=}")
            return file_obj, file_name
        except Exception as e:
            _logger.warning("".join(traceback.format_exc()))
            return None, None

    def _create_attachment(self, datas, name):
        return base64.encodebytes(datas.read())

    def create_manifest(self):
        manifest_vals = {
            'name': self.name,
            'category': self.app_category.name,
            'website': 'https://www.vertlab.se',
            'summary': self.app_summary,
            'author': 'Vertel AB',
            'version': '1.0',
            'license': self.app_license,
            'description': self.app_description,
            'depends': [],
            'data': [],
            'installable': True,
            'application': True,
            'qweb': []
        }
        user_encode_data = json.dumps(manifest_vals, indent=2).encode('utf-8')
        temp = tempfile.NamedTemporaryFile(mode='w+b')
        temp.write(user_encode_data)
        temp.seek(0)
        attachment_id = self.env['ir.attachment'].create({
            'name': '__manifest__.py',
            'res_name': self.name,
            'res_model': self._name,
            'res_id': self.id,
            'datas': base64.encodebytes(temp.read()),
        })
        temp.close()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': self.env.ref('website_blog_app.download_manifest_wizard').id,
            'res_id': attachment_id.id,
            'target': 'new',
            'flags': {'mode': 'readonly'},
        }
