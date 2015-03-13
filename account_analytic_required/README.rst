Account Analytic Required
=========================

This module adds an option *analytic policy* on account types.
You have the choice between 3 policies : *always*, *never* and *optional*.

For example, if you want to have an analytic account on all your expenses,
set the policy to *always* for the account type *expense* ; then, if you
try to save an account move line with an account of type *expense*
without analytic account, you will get an error message.

Contributors
------------

- Module developped by Alexis de Lattre <alexis.delattre@akretion.com>
  during the Akretion-Camptocamp code sprint of June 2011.
- Luc De Meyer <luc.demeyer@noviat.com>