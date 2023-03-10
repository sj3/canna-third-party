# Copyright (C) 2019-2022 Noviat nv/sa (www.noviat.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _belongs_to_category(self, category):
        """
        Returns True if the product category or one of its children
        is equal to 'category'.
        """
        self.ensure_one()

        def check_category_recursive(product, category):
            # In case we are in an onchange, category is a NewId.
            # By using .ids we get a value that we can use to compare.
            if product.categ_id.ids == category.ids:
                return True
            else:
                for categ in category.child_id:
                    check = check_category_recursive(product, categ)
                    if check:
                        return True
                return False

        return check_category_recursive(self, category)
