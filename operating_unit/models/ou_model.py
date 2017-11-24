# # -*- coding: utf-8 -*-
# # Copyright 2009-2017 Noviat.
# # Copyright 2009-2017 Onestein BV.
# # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models, SUPERUSER_ID
from lxml import etree
import logging
_logger = logging.getLogger(__name__)


class OUModel(models.BaseModel):
    """Manages a dynamic domain on all fields of all models,
    so that only records related to the currently selected Operating Unit are
    shown. Let classes that require this functionality inherit this class."""
    # TODO merge into operating_unit.py
    _name = None
    _auto = True  # create database backend
    # Not visible in ORM registry, meant to be python-inherited only:
    _register = False
    _transient = False  # True in a TransientModel

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """
        Override to apply the Operating Unit domain to all relevant fields.
        """
        def modify_domain():
            """
            Change the domain so only records on the fetched fields
            belonging to the currently selected operating unit are visible.
            for relevant_relation in relevant_relations.
            """
            if res.get('fields') and res['fields'].get(
                    relation[0]):
                doc = etree.XML(res['arch'])
                nodes = doc.xpath("//field[@name='%s']" % relation[0])
                # Get the related model's allowed records.
                foreign_obj = self.env[relation[1]]
                # Filter records based on currently set Operating Unit.
                allowed_recs = foreign_obj.search([
                    (foreign_column, 'in', user_ous.ids)])
                for node in nodes:
                    # Prepend to original domain.
                    if node.attrib.get('domain'):
                        new_domain = node.attrib['domain'][:1] + \
                                 "('id', 'in', %s)," % allowed_recs.ids + \
                                 node.attrib['domain'][1:]
                        node.set('domain', new_domain)
                    # Add domain attribute.
                    else:
                        _logger.debug(
                            "Domain added to field for OperatingUnit. "
                            "Node: %s" % node.attrib['name']
                        )
                        node.set('domain', "[('id', 'in', %s),"
                                           "]" % allowed_recs.ids)
                res['arch'] = etree.tostring(doc)

        res = super(OUModel, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        # TODO is only checking this on form view enough?
        if not res['type'] == 'form':
            return res
        user_obj = self.env['res.users']
        user_ous = user_obj.browse(self._uid).default_operating_unit_id or \
                   user_obj.browse(self._uid).operating_unit_ids
        # Don't modify domains if admin has not selected a specific Operating
        # Unit.
        if self._uid == SUPERUSER_ID and len(user_ous) != 1:
            return res

        # Get all related fields to models which have a field that points to
        #  model "operating.unit".
        # relations = [(str(field), str(model)),...]
        relations = [(f, res['fields'][f]['relation']) for f in res[
            'fields'] if res['fields'][f].get('relation')]
        relevant_relations = []
        for relation in relations:
            foreign_column = 'operating_unit_id'
            # Skip chatter fields to show all followers and messages:
            if relation[0] in ['message_follower_ids', 'message_ids']:
                continue
            foreign_obj = self.env[relation[1]]
            # Modify domain without checking again if relation is already
            # confirmed to have a relation to operating.unit:
            if relation[1] in relevant_relations:
                modify_domain(relation)
                relevant_relations.append(relation)
            # Special case res.users because it uses "operating_unit_ids":
            elif relation[1] == 'res.users':
                foreign_column = 'operating_unit_ids'
                modify_domain()
                relevant_relations.append(relation)
            # Check if the default name "operating_unit_id is" used:
            elif foreign_obj._all_columns.get(
                    'operating_unit_id'):
                modify_domain()
                relevant_relations.append(relation)
            # Check all foreign fields if "operating_unit_id" isn't found:
            else:
                for foreign_column in foreign_obj._all_columns.iteritems():
                    if foreign_column[1].column._obj == 'operating.unit':
                        modify_domain()
                        relevant_relations.append(relation)
                        # Continue with next local field.
                        break
        return res
