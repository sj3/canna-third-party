.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

========================
Netherlands - ICP Report
========================

This module activates the following functionality:
- Periodical Intracom Declaration (ICP)

The report is available in PDF and Excel (xlsx) format.

Configuration
=============

Tax objects
-----------

Please ensure that the Odoo Tax objects for intracommunity services and products
are configured with Tax Code '3b'.
This is the case when using tax objects based upon the tax templates supplied with l10n_nl.

Use Tax Code '3b-T' for ABC transactions.

Known issues / Roadmap
======================

 * No cross control with periodical VAT declaration (must be done manually)
 * The report is based upon a query on the accounting entries and takes into account the
   accounting entry date (not the fiscal period) and the tax codes (3b).
   A manual correction is required when delivery of services takes place
   in a different period than the corresponding invoice.
   A manual correction is also required for intracom deliveries without corresponding
   invoice (e.g. delivery to EU offices of your own company).
