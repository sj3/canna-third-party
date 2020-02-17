# -*- coding: utf-8 -*-
# Copyright 2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
_logger = logging.getLogger(__name__)

try:
    import vatnumber
except ImportError:
    _logger.warning("VAT validation partially unavailable because the `vatnumber` Python library cannot be found. "
                                          "Install it to support more countries, for example with `easy_install vatnumber`.")
    vatnumber = None

from openerp.osv import fields, osv


class res_partner(osv.osv):
    _inherit = 'res.partner'

    def check_vat_sk(self, vat):
        '''
        Check Slovakia VAT number.
        VAT format: [C1 C2 C3 C4 C5 C6 C7 C8 C9 C10]
          Where:
            C1 to C10 are digits.
            C1: In the range 1...9
            C2, C4...C10: In the range 0...9
            C3: One of 2, 3, 4, 7, 8, 9
          Rules:
            [C1 C2 C3 C4 C5 C6 C7 C8 C9 C10] modulo 11 = 0
        '''
        def check_vat_ch_match(vat):
            if len(vat) != 10:
                return False
            if not vat.isdigit():
                return False
            if int(vat[0:1]) == 0:
                return False
            if int(vat[2:3]) in [0, 1, 5, 6]:
                return False
            return True

        _logger.info("Check Slovakia VAT number: " + vat)
        if not check_vat_ch_match(vat):
            _logger.info("Slovakia VAT number: regex not OK")
            if vatnumber:
                check_func = getattr(vatnumber, 'check_vat_sk', None)
                return check_func(vat)
            return False
        #digits = filter(lambda s: s.isdigit(), vat)
        return int(vat) % 11 == 0.0
