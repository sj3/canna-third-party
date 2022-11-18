# Copyright (c) 2016 Onestein BV (www.onestein.eu).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
        openupgrade.logged_query(
            env.cr, """
            delete from mail_template mt
            using ir_model_data imd
            where imd.model='mail.template' and
            imd.name='email_template_po_to_apprv'
            and imd.module='extended_approval_purchase_order' and
            imd.res_id=mt.id;"""
        )
        openupgrade.logged_query(
            env.cr, """
            delete from ir_model_data
            where model='mail.template' and name='email_template_po_to_apprv'
            and module='extended_approval_purchase_order';"""
        )
