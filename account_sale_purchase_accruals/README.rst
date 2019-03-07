.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==============================
Account Sale Purchase Accruals
==============================

This module generates traceable Journal Entries for the complete
Sale/Purchase/Stock process with automatic reconciliation of
entries on accrued expense accounts.

Installation
============

This module is NOT compatible with the 'account_anglo_saxon' module from the standard addons.

This module requires that your Odoo instance runs a version that includes the
following Pull Request:

  https://github.com/odoo/odoo/pull/10551

You should install the patch distributed with this module if this is not the case,
cf. doc/account_invoice.diff

This module requires version 8.0.2.1.0 of the 'account_refund_original' module,
cf. https://github.com/OCA/l10n-spain/tree/8.0


Configuration
=============

Product parameters
------------------

Procurement Action = Buy
''''''''''''''''''''''''

Define the Accrued Expense In/Out accounts on Product or Product Category.

Procurement Action = Move
'''''''''''''''''''''''''

Set 'Inventory Valuation' to Real Time on the Product record.
Define the Stock Input/Output accounts on Product or Product Category.

Financial Journals
------------------

Set the 'Group Invoice Lines' flag on your Sales and Purchase Journals.

Company parameters
------------------

- Accrual Journal

Define the Financial Journal used for the product related Accrual Entries generated when
validating the Sales Invoice. Also the product related accrual entries generated when purchasing
those goods are created in this Journal.

These Sales and Purchase accruals will be automatically reconciled with each other.
As a consequence, the non-reconciled accruals give the list of sold products with
pending procurements.

Known issues / Roadmap
======================

At this point in time the module does not support accruals for

- bougth-in services (unless if you configure such a service as a 'dropship consumable')
- manufacturing
