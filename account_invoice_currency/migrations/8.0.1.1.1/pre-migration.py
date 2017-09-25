# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Onestein (http://www.onestein.eu).
#    Copyright (c) 2009-2017 Noviat nv/sa (www.noviat.com).
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

import logging

logger = logging.getLogger('OpenUpgrade')


def migrate(cr, version):
    if not version:
        sql = """
ALTER TABLE public.account_invoice ADD COLUMN cc_amount_tax numeric;
COMMENT ON COLUMN public.account_invoice.cc_amount_tax IS 'Company Cur. Tax';
ALTER TABLE public.account_invoice ADD COLUMN cc_amount_untaxed numeric;
COMMENT ON COLUMN public.account_invoice.cc_amount_untaxed IS 'Company Cur. Untaxed';
ALTER TABLE public.account_invoice ADD COLUMN cc_amount_total numeric;
COMMENT ON COLUMN public.account_invoice.cc_amount_total IS 'Company Cur. Total';


UPDATE account_invoice AS inv SET (cc_amount_untaxed, cc_amount_tax,
cc_amount_total) = (amount_untaxed, amount_tax,
amount_total)
-- 1. If invoice currency_id != company currency_id:
WHERE
(
    SELECT TRUE
    FROM res_company AS cmp
    WHERE inv.company_id = cmp.id
    AND inv.currency_id = cmp.currency_id
);

-- 1. company currency_id != invoice currency_id
UPDATE account_invoice AS inv SET (cc_amount_untaxed, cc_amount_tax,
cc_amount_total) = (0.0, 0.0, 0.0)
-- 1. If invoice currency_id != company currency_id:
WHERE
(
SELECT TRUE
FROM res_company AS cmp
WHERE inv.company_id = cmp.id
AND inv.currency_id != cmp.currency_id
);

-- 1. company currency_id != invoice currency_id
-- 2. Invoice has move_id.
-- 3. Sum of (debit - credit) of all related move lines.
-- 3.1 Where move lines only refer to an account_id which
-- is in the invoice_line of the invoice.
-- 3.
WITH aml_data AS (
SELECT i.id, aml.debit, aml.credit
FROM account_invoice AS i
INNER JOIN account_move AS mv
ON i.move_id = mv.id
INNER JOIN account_move_line AS aml
ON aml.move_id = mv.id
-- 3.1 if line.account_id.id in tax_accounts:
WHERE aml.account_id IN
(SELECT DISTINCT ail.account_id
FROM account_invoice_line AS ail
WHERE ail.invoice_id = i.id
)
)
UPDATE account_invoice AS inv
SET cc_amount_untaxed = (
SELECT inv.cc_amount_untaxed + sum(debit)-sum(credit)
FROM aml_data AS d WHERE d.id = inv.id)
WHERE
-- 1. If invoice currency_id != company currency_id:
(
SELECT TRUE
FROM res_company AS cmp
WHERE inv.company_id = cmp.id
AND inv.currency_id != cmp.currency_id
)
-- 2.
AND move_id IS NOT NULL;

-- 1. company currency_id != invoice currency_id
-- 2. Invoice has move_id.
-- 3. Sum of (debit - credit) of all related move lines.
-- 3.1 Where move lines only refer to an account_id which
-- is in the tax_line of the invoice and that tax_line
-- has an amount which is not 0.
-- 3.
WITH aml_data AS (
SELECT i.id, aml.debit, aml.credit
FROM account_invoice AS i
INNER JOIN account_move AS mv
ON i.move_id = mv.id
INNER JOIN account_move_line AS aml
ON aml.move_id = mv.id
-- 3.1 if line.account_id.id in tax_accounts:
WHERE aml.account_id IN
(SELECT DISTINCT ait.account_id
FROM account_invoice_tax AS ait
WHERE ait.invoice_id = i.id
)
)
UPDATE account_invoice AS inv
SET cc_amount_tax = (
SELECT inv.cc_amount_tax + sum(debit)-sum(credit)
FROM aml_data AS d WHERE d.id = inv.id)
WHERE
-- 1. If invoice currency_id != company currency_id:
(
SELECT TRUE
FROM res_company AS cmp
WHERE inv.company_id = cmp.id
AND inv.currency_id != cmp.currency_id
)
-- 2.
AND move_id IS NOT NULL;


-- 1. company currency_id != invoice currency_id
-- 2. Invoice has move_id.
-- 3. Invoice.type in ('out_invoice, 'in_refund').
UPDATE account_invoice AS i SET (cc_amount_untaxed,
cc_amount_tax) = (-cc_amount_untaxed, -cc_amount_tax)
-- 3.
WHERE type IN ('out_invoice', 'in_refund')
-- 2.
AND i.move_id IS NOT NULL
-- 1. If invoice currency_id != company currency_id:
AND (SELECT TRUE FROM (
SELECT inv.currency_id FROM account_invoice
AS inv INNER JOIN res_company AS cmp
ON inv.company_id = cmp.id
WHERE inv.currency_id != cmp.currency_id
AND inv.id = i.id) AS sub
);

-- 1. company currency_id != invoice currency_id
-- 2. Invoice has move_id.
UPDATE account_invoice AS i
SET cc_amount_total = cc_amount_tax + cc_amount_untaxed
-- 2.
WHERE i.move_id IS NOT NULL
-- 1. If invoice currency_id != company currency_id:
AND (SELECT true FROM (
SELECT inv.currency_id FROM account_invoice
AS inv INNER JOIN res_company AS cmp
ON inv.company_id = cmp.id
WHERE inv.currency_id != cmp.currency_id
AND inv.id = i.id) AS sub
);
        """
        logger.debug(
            "Running query to populate account_currency_invoice computed "
            "fields")
        cr.execute(sql)
