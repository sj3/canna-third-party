# Copyright 2009-2022 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    cr.execute(
        "SELECT id FROM ir_model_fields WHERE model='res.partner' "
        "AND name='out_inv_comm_algorithm'"
    )
    [fields_id] = cr.fetchone()
    cr.execute(
        """
        INSERT INTO ir_property(name, type, fields_id, company_id, res_id, value_text)
        SELECT 'out_inv_comm_algorithm', 'selection', %s,
        company_id, CONCAT('res.partner,', id),
               out_inv_comm_algorithm
          FROM res_partner
        WHERE out_inv_comm_algorithm IS NOT NULL OR out_inv_comm_type = 'bba'
    """,
        (fields_id,),
    )
    cr.execute(
        "SELECT id FROM ir_model_fields WHERE "
        "model='res.partner' AND name='out_inv_comm_type'"
    )
    [fields_id] = cr.fetchone()
    cr.execute(
        """
        INSERT INTO ir_property(name, type, fields_id, company_id, res_id, value_text)
        SELECT 'out_inv_comm_type', 'selection', %s,
        company_id, CONCAT('res.partner,', id),
               out_inv_comm_type
          FROM res_partner
        WHERE out_inv_comm_algorithm IS NOT NULL OR out_inv_comm_type = 'bba'
    """,
        (fields_id,),
    )
