.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

====================
Import Price Catalog
====================

Module to import Price Catalogs.

The file to be imported must have the following structure:
- Column 1: Product Code
- Column 2: Product Description (for information only, only the Product Code is used to load the data)
- Column 3: price

The labels of the header line are not important, after the header line the Code is retrieved from Column 1 and the Price from Column 3.


productdescription is not used but kept for legacy compatibility.

The file must be a csv file with the following settings:
- character set: utf-8
- field delimiter: ;
- string delimiter: "
