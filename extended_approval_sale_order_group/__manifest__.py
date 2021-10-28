# Copyright (C) Startx 2021
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Extended Approval Sale Order Group",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Startx",
    "category": "base",
    "depends": [
        "sale_order_group",
        "base_extended_approval",
        # Not strictly necessary, but allows to test interaction.
        "extended_approval_sale_order",
    ],
    "data": ["views/sale_order_group_views.xml"],
    "installable": True,
}
