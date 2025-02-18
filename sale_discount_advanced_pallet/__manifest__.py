# Copyright 2019 Onestein (https://www.onestein.nl/).
# Copyright 2009-2025 Noviat (www.noviat.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Discount Advanced Pallet",
    "author": "Onestein, Noviat",
    "summary": """Extends Discounts with the pallet matching type""",
    "category": "Sales",
    "version": "13.0.1.1.0",
    "license": "AGPL-3",
    "depends": ["sale_discount_advanced", "product_packaging_type_pallet"],
    "data": ["views/sale_discount_views.xml"],
    "demo": [
        "demo/product_packaging_type_demo.xml",
        "demo/product_packaging_demo.xml",
        "demo/sale_discount_demo.xml",
        "demo/sale_discount_rule_demo.xml",
    ],
}
