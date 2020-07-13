# Copyright 2009-2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Module List readonly",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Noviat",
    "category": "Tools",
    "depends": ["base"],
    "external_dependencies": {"python": ["lxml"]},
    "data": [
        "security/module_security.xml",
        "views/remove_sidebar_action.xml",
        "views/ir_module_module.xml",
    ],
    "installable": True,
}
