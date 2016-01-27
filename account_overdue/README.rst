Account Reinvoice
=================

Module for automatic inter-company reinvoicing.

Usage
=====

Reinvoice Keys and Distributions
--------------------------------

Go to **Accounting > Configuration > Miscellaneous > Reinvoice Configuration**

Reinvoice Distributions
-----------------------
| Use this menu entry to configure the Reinvoicing rate per target Customer.
|

Reinvoice Keys
--------------
| The Distribution Key is the field on an accounting entry that triggers the Reinvoicing process.
| Such a key contains key instances which are valid within a configured date range and refer to a Distribution.
| No reinvoicing will take place for instances in 'Draft' state.
|

Accounting Entries
------------------

It is recommended to enter the 'Product' field when encoding distribution keys in accounting entries. 
The products on the incoming entries will be copied to the corresponding outgoing Customer Invoice.

In case of a multi-company setup (cf. module account_reinvoice_multi_company), these products
will also be copied to the corresponding incoming invoice (if allowed by security settings).
In this case, the product record accounting properties will be used to determine general accounts and
taxes on those incoming invoices and hence allows fully automated end-to-end intercompany invoicing.

