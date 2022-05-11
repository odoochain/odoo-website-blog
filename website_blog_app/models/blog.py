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
from odoo.tools.translate import html_translate
_logger = logging.getLogger(__name__)
import traceback


class Blog(models.Model):
    _inherit = 'blog.blog'

    is_app = fields.Boolean(string="Is App")
    app_project = fields.Char(string="App Project")


class BlogPost(models.Model):
    _inherit = 'blog.post'

    def _default_description(self):
        return self.env['ir.ui.view']._render_template('website.s_text_image')

    is_app = fields.Boolean(string="Is App", related="blog_id.is_app")
    pod_id = fields.Integer(string="Pod Id")
    app_project = fields.Char(string="App Project", related="blog_id.app_project")
    app_module = fields.Char(string="App Module", default="technical name")
    app_tree = fields.Char(string="Branch Tree", default="14.0")
    app_icon = fields.Binary(string="Icon")
    
    app_url = fields.Char(string="Website", compute="_get_app_url", default="vertel")
    app_banner = fields.Binary(string="App Banner")
    app_summary = fields.Char(string="App Summary")
    app_category = fields.Many2one('ir.module.category', string="Category", default=1)
    app_description = fields.Text(string="App Description", default="The module description goes here.")
    app_manifest = fields.Char(string="App Manifest")
    app_license = fields.Char(string="App License", default="LGPL-3")
    app_index = fields.Html(string="App Index", translate=html_translate, sanitize_attributes=False,
                            sanitize_form=False, default=_default_description)
                            
    @api.depends('app_module', 'blog_id.app_project')
    def _get_app_url(self):	 
        for b in self:
           if b.blog_id.app_project and b.app_module:
               b.app_url = "https://vertel.se/apps/"+b.blog_id.app_project+"/"+b.app_module
 
 
    def sync_module(self):
        git_url = self.env['ir.config_parameter'].sudo().get_param('GitHubBaseUrl')
        			
        if not git_url:
            raise UserError(_("Git URL is not set"))
        if not self.app_project:
            raise UserError(_("No Git Project was specified"))
        if not self.app_module:
            raise UserError(_("No Module was specified"))
        if self.app_project and self.app_module:
            module_url = f"{git_url}/{blog_post.app_project}/{blog_post.app_module}/{self.app_module}"
            
            # get icon

            icon_data, icon_name = self._wget_sync(f"{module_url}/static/description/icon.png")
            if icon_data and icon_name:
                self.app_icon = self._create_attachment(icon_data, icon_name)
            # get banner
            manifest_obj = urllib.request.urlopen(f"{module_url}/__manifest__.py").read().decode('utf-8')
            manifest = re.sub(r'(?m)^ *#.*\n?', '', manifest_obj)
            if manifest:
                manifest = ast.literal_eval(manifest)
                manifest_images = manifest.get('images')
                if manifest_images:
                    main_screenshot = [image for image in manifest_images if image.endswith('_screenshot.png')]
                    banner_data, banner_name = self._wget_sync(
                        f"{module_url}{main_screenshot[0] if main_screenshot else manifest_images[0]}"
                    )
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

