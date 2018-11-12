.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
Web Hidden Element
==================

This module allows to hide fields and other view elements to all users or groups, or to a specific user or
group, without changing the view XML files.

Inspired by web_hidden_field from Ignacio Ibeas <ignacio@acysos.com>

Installation
============

Copy this module to your addons path and go to Applications and Install.

Configuration
=============

Don't need any special configuration.

Usage
=====

Go to Settings -> Security -> Hidden Elements -> Hidden Elements.
Create a new template and select the model and the fields and elements that you want to 
hide. 
If you don't select any user or group, the field/element is hidden for all users. If
you select any user the field is hidden for this user. If you select any 
group the field is hidden for this group. The user is more restrictive than 
the group.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/162/10.0


Known issues / Roadmap
======================

*

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/web/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.


Credits
=======

Images
------

* Odoo Community Association: `Icon <https://odoo-community.org/logo.png>`_.


Contributors
------------

* Ignacio Ibeas - Acysos S.L. <ignacio@acysos.com>


Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
