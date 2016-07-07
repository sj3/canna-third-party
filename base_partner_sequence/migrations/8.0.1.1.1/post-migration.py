# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Onestein (http://www.onestein.eu).
#    Copyright (c) 2009-2016 Noviat nv/sa (www.noviat.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, SUPERUSER_ID
from openupgradelib import openupgrade
import logging

logger = logging.getLogger('OpenUpgrade')


def fill_partner_ref(env):
    """Fills partner refs according to base_partner_sequence.
    Note that base_partner_sequence treats the reference field as a
    commercial field, thus contacts do not get reference codes.
    This method tries to find an already existing partner sequence and
    starts counting from there.
    """
    seq_obj = env['ir.sequence']
    # Try to find an existing res.partner sequence
    old_sequence = seq_obj.search(
        [('code', '=', 'res.partner'), ('number_next', '>', 1)])
    # Use the highest sequence
    # if there is no match: just use 1 (default)
    # if there are multiple, find the highest:
    if len(old_sequence) != 1:
        highest_seq = seq_obj.browse()
        for sequence in old_sequence:
            if sequence.number_next > highest_seq.number_next:
                highest_seq = sequence
        if highest_seq:
            old_sequence = highest_seq
    assert len(old_sequence) == 1
    # Update the new sequence:
    new_sequence = env.ref('base_partner_sequence.seq_res_partner')
    new_sequence.number_next = old_sequence.number_next
    # Write the updated sequence to partners which do not have a ref yet:
    vals = {}
    partner_obj = env['res.partner']
    # Note: not taking inactive partners into account.
    all_partners = partner_obj.search([])
    for partner in all_partners:
        if not partner.ref and partner._needsRef(partner.id):
            vals['ref'] = partner._get_next_ref(partner, vals)
            partner.write(vals)
    return True


@openupgrade.migrate(no_version=True)
def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        fill_partner_ref(env)
