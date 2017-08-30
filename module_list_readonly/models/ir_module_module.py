# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from openerp import api, models


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        res = super(IrModuleModule, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        if res.get('type') in ['tree', 'form']:
            if self._context.get('module_list_readonly'):
                if 'action' in res.get('toolbar'):
                    del res['toolbar']['action']
        if view_type == 'form' and self._context.get('module_list_readonly'):
            form = etree.XML(res['arch'])
            for div in form.xpath("//div[@class='oe_title']/div"):
                div.getparent().remove(div)
            res['arch'] = etree.tostring(form)
        return res
