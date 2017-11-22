# # -*- coding: utf-8 -*-
# # Copyright 2009-2017 Noviat.
# # Copyright 2009-2017 Onestein BV.
# # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models, SUPERUSER_ID
from lxml import etree


class OUModel(models.BaseModel):
    """For managing a dynamic view filter on all fields of all models,
    so that only records related to the currently selected operating unit are
    shown. Let classes that require this functionality inherit this class."""
    # TODO check if these are required:
    _name = None
    _auto = True
    _register = False
    _transient = False  # True in a TransientModel

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        """ fields_view_get([view_id | view_type='form'])

        Get the detailed composition of the requested view like fields, model,
        view architecture

        :param view_id: id of the view or None
        :param view_type: type of the view to return if view_id is None
        ('form', 'tree', ...)
        :param toolbar: true to include contextual actions
        :param submenu: deprecated
        :return: dictionary describing the composition of the requested view
        (including inherited views and extensions)
        :raise AttributeError:
                            * if the inherited view has unknown position to
                            work with other than 'before', 'after', 'inside',
                            'replace'
                            * if some tag other than 'position' is found in
                            parent view
        :raise Invalid ArchitectureError: if there is view type other than
        form, tree, calendar, search etc defined on the structure
        """

        res = super(OUModel, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        # Get all related fields to models which have a field that points to
        #  the model operating.unit.

        # Browse all x2x fields
        # relations = [(str field, str model)]
        relations = [(x, res['fields'][x]['relation']) for x in res[
            'fields'] if res['fields'][x].get('relation')]
        relevant_relations = []
        for relation in relations:
            # TODO don't run it on the same foreign model twice (but do add
            # the other relevant_relation(s) to the list.
            # SKIP message_follower_ids
            if relation[0] == 'message_follower_ids':
                continue
            for foreign_column in self.env[relation[
                1]]._all_columns.iteritems():
                if foreign_column[1].column._obj == 'operating.unit':
                    relevant_relations.append(relation)
                    # Continue with next local field.
                    break

        # Change the domain so only records on the fetched fields (above)
        # belonging to the currently selected operating unit are visible.
        for relevant_relation in relevant_relations:
            # TODO is only checking this on form view enough?
            if res.get('fields') and res['fields'].get(relevant_relation[0])\
                    and res['type'] == 'form':
                doc = etree.XML(res['arch'])
                nodes = doc.xpath("//field[@name='%s']" % relevant_relation[0])
                # Get the related model's allowed records.
                foreign_obj = self.env[relevant_relation[1]]
                user_obj = self.env['res.users']
                # Get the user's current Operating Unit (TODO move up)
                user_ou = user_obj.browse(self._uid).default_operating_unit_id
                # Filter records based on currently set Operating Unit.
                if user_ou:
                    allowed_recs = foreign_obj.search([
                        ('operating_unit_id', '=', user_ou.ids)])
                    for node in nodes:
                        print "NODE: ", node.attrib['name']
                        # Prepend to original domain.
                        try:
                            new_domain = node.attrib['domain'][:1] + \
                                "('id', 'in', %s)," % allowed_recs.ids + \
                                node.attrib['domain'][1:]
                            node.set('domain', new_domain)
                        except KeyError:
                            # TODO see new_domain (instead of hardcode 1)
                            # TODO add logger call, use:
                             # print "NODE: ", node.attrib['name']
                            node.set('domain', "[('id', 'in', %s),"
                                               "]" % allowed_recs.ids)
                    res['arch'] = etree.tostring(doc)
                # Allow admin to see everything
                elif self._uid == SUPERUSER_ID:
                    pass  # TODO
                # In case none set, allow all in operating_unit_ids ("Allowed
                # Operating Units").
                else:
                    pass  # TODO
        return res
