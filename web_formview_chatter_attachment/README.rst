============================
Form View Chatter Attachment
============================

This module allows to use the Odoo attachment widget code that is part of the chatter
in a regulat form view (pop up window as well as full screen form view).

It also adds a couple of options that enrich the attachment widget features when used
in the standard Odoo chatter zone.

|

Usage
=====

The attachment handling widget is rendered when adding the following div to your form view:

.. code:: xml

       <div class="oe_chatter"
            style="display:block;"
            options="{'render_attachments': True, 'open_attachments': True, 'hide_attachments_topbar': True, 'readonly': True}"
       />

|

Widget options
--------------

* render_attachments: set to True to show the attachment widget
* open_attachments: set to True to open the attachment widget
* hide_attachments_topbar: set to True to hide the attachment topbar
* readonly: set to True to hide the attachment add and delete buttons

|

Remarks
-------

The attachment topbar contains the button to open/close the attachment widget.
Setting this option to False in combination with 'open_attachments': False has
as a consequence the same effect as 'render_attachments': False

