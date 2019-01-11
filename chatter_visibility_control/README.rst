.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==========================
Chatter visibility control
==========================

This module allows to control the visibility of tracked fields in the chatter based on the Odoo security groups.

If security groups are added to the Model field definition of a tracked field, then the info in the chatter concerning
this field will only be visible to the users of those groups.


Configuration
=============

Define the system parameter ``chatter_visibility_control`` with the list of models
for which the visibility control will be applied, 
e.g. ``['sale.order', 'purchase.order', 'account.invoice']``

Specify the security groups in the Model fields definition via the ``track_visibility_groups`` parameter.

Install the ``chatter_visibility_control_purchase_demo`` module for a concrete example.
