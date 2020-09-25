# -*- coding: utf-8 -*-
# Copyright 2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    bolcom_customer = fields.Boolean(string="Bol.com customer")

    def _bolcom_res_partner_mapping(self):
        return {
            "salutationCode": {"ignore": True},
            "firstName": {"method": "_bolcom_handle_name"},
            "surName": {"method": "_bolcom_handle_name"},
            "streetName": {"method": "_bolcom_handle_street"},
            "houseNumber": {"method": "_bolcom_handle_street"},
            "houseNumberExtended": {"method": "_bolcom_handle_street"},
            "extraAddressInformation": {"field": "street2"},
            "zipCode": {"field": "zip"},
            "city": {"field": "city"},
            "countryCode": {"method": "_bolcom_handle_country_id"},
            "email": {"field": "email"},
            "pickUpPointName": {"ignore": True},
        }

    @api.multi
    def bolcom_synchronize(self, vals_in):
        mapping_specs = self._bolcom_res_partner_mapping()
        partner = self
        if not self:
            action = "create"
        else:
            self.ensure_one()
            action = "update"
        handled = []
        vals = {"bolcom_customer": True}
        for key, value in vals_in.items():
            if key in handled:
                continue
            mapping = mapping_specs.get(key)
            if not mapping:
                raise UserError(_("Missing mapping table entry for parameter %s") % key)
            if mapping.get("ignore"):
                handled.append(key)
                continue
            if mapping.get("method"):
                method = "{}".format(mapping["method"])
                handled.extend(getattr(self, method)(key, vals_in, vals))
            else:
                vals[mapping["field"]] = value
                handled.append(key)
        self._bolcom_sync_update_vals(vals_in, vals)
        if action == "create":
            partner = self.create(vals)
        else:
            for f in vals.keys():
                val = getattr(partner, f)
                if isinstance(self._fields[f], fields.Many2one):
                    val = val.id
                if val == vals[f]:
                    del vals[f]
            if vals:
                partner.update(vals)
        return partner

    def _bolcom_sync_update_vals(self, vals_in, vals):
        if not self.property_account_position:
            fpos = self.env.user.company_id.bolcom_fiscal_position_id
            if fpos:
                vals["property_account_position"] = fpos.id

    def _bolcom_handle_name(self, key, vals_in, vals):
        name_fields = ["surName", "firstName"]
        is_company = vals_in.get("vatnumber", False) or self.is_company
        if is_company:
            vals["name"] = vals_in["surName"]
        else:
            vals["name"] = vals_in["surName"] + " " + vals_in["firstName"]
        vals["type"] = "delivery"
        return name_fields

    def _bolcom_handle_street(self, key, vals_in, vals):
        name_fields = ["streetName", "houseNumber", "houseNumberExtended"]
        street_parts = [vals_in[x].strip() for x in name_fields if vals_in.get(x)]
        vals["street"] = " ".join(street_parts)
        return name_fields

    def _bolcom_handle_country_id(self, key, vals_in, vals):
        name_fields = ["countryCode"]
        cc = vals_in.get("countryCode")
        if not cc:
            return name_fields
        country_ids = self.env["res.country"].search([("code", "=", cc)])
        if not country_ids:
            _logger.error("Missing Country definition for Country Code %s", cc)
        else:
            vals["country_id"] = country_ids[0].id
        return name_fields
