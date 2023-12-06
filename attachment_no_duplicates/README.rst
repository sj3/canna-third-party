.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

=============================
Prevent duplicate attachments
=============================

When sending an invoice to a customer via mail an attachment containing the invoice PDF is
added to the message board as well as to the invoice.
In case this PDF was already generated the PDF file is attached a second time.
When resending the invoice the attachment is created over and over again.

The same problem may occur on other objects using the mail.compose.message wizard.

This module correct this behaviour and ensures that identical attachments are added only once.
