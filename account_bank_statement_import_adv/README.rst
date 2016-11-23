.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

===========================
Bank Statement Files import
===========================

This module changes the OCA bank statement files import as follows:

Replacement of import method in order to disable the
automatic dispatch of the reconciliation interface.

Such a dispatch must take place after running
auto-reconcile/posting logic in order to filter out
the entries which do not require manual intervention.
