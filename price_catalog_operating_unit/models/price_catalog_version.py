# Copyright 2020 Onestein B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PriceCatalogVersion(models.Model):
    """Adds Operating Unit functionality to Price Catalog Versions."""

    _inherit = "price.catalog.version"

    operating_unit_id = fields.Many2one(
        comodel_name="operating.unit",
        default=lambda self: self.env["res.users"].operating_unit_default_get(),
    )
