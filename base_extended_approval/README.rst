.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

======================
Base Extended Approval
======================

This module provides the base for extended approval flows. Through addon modules
extended flows can be made available for models.

If a model has an extended approval flow, when an object enters the approval
process the first matching flow (for which the domain applies) is used for the
approval process.

Each step of the flow for which the condition applies has to be completed. It
can be completed by a user which has any of the groups mentioned.

The applicable steps will be completed in sequence, and for each step a log
record will be created.

If a user belongs to the groups of multiple consecutive steps, all these steps
will be completed at once.

===
API
===

To integrate an existing model with extended approval, you have to create a
module extended_approval_<model_or_module>

In this module you should create a models/<model>.py which inherits the model
as shown:

.. code-block:: python

    from odoo import fields, models


    class ResPartner(models.Model):
        _name = "res.partner"
        _inherit = ["res.partner", "extended.approval.method.field.mixin"]

|

There are multiple mixins available depending on how you want to integrate
(see below).

You should also subclass extended approval history to add your model as
option for these records:

.. code-block:: python

    from odoo import fields, models


    class ExtendedApprovalHistory(models.Model):
        _inherit = "extended.approval.history"

        source = fields.Reference(selection_add=[("res.partner", "Partner")])

|

Lastly you will probably want to change the 'approve' and 'reset' buttons
visibility and add the approval history on the form. Example:

.. code-block:: xml

    <xpath expr="/form/sheet" position="before">
        <header>
            <button type="object" name="reset_to_draft"
                string="Reset to draft"
                attrs="{'invisible': ['|', ('state', 'not in', ['confirmed'])]}" />
            <button type="object" name="set_state_to_confirmed"
                string="Confirm partner"
                attrs="{'invisible': [('state', 'not in', ['draft']), '|', ('approval_allowed', '!=', True), ('state', 'not in', ['extended_approval'])]}" />
            <field name="state" widget="statusbar" />
        </header>
    </xpath>
    <xpath expr="//notebook" position="inside">
        <page string="Approvals" name="approval">
            <group name="g1" colspan="4" col="4"
                attrs="{'invisible': [('next_approver', '=', False)]}">
                <label for="next_approver" />
                <div>
                    <field name="next_approver" widget="many2many_tags"
                        options='{"no_open":True}' />
                    <button string="=> Users"
                        help="Show Approval Group Users" name="show_approval_group_users"
                        type="object" class="oe_link" />
                </div>
                <field name="approval_allowed" />
            </group>
            <group name="g2" colspan="4">
                <field colspan="4" name="approval_history_ids"
                    readonly="1">
                    <tree string="Approval History">
                        <field name="date" />
                        <field name="requested_group_ids" widget="many2many_tags" />
                        <field name="approver_id" />
                    </tree>
                </field>
            </group>
        </page>
    </xpath>

|

------------------------------------
extended.approval.method.field.mixin
------------------------------------

This mixin integrates by patching a method (intercepting the call to this
method), eg "button_approve". Furthermore this mixin supports a "state"
selection field.

The State selection field will automatically have an approval stated added
(after the start state).

--------------------------------
extended.approval.workflow.mixin
--------------------------------

This mixin triggers the approval workflow when setting the 'ea_state_field'
to the value defined into via the 'ea_signal' class attribute.
