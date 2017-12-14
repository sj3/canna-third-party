from openerp import models


class BaseModelExtend(models.AbstractModel):
    _name = 'basemodel.extend'

    def _register_hook(self, cr):

        def _ou_search(
                self, cr, user, args, offset=0, limit=None,
                order=None, context=None, count=False, access_rights_uid=None):

            if context is None:
                context = {}
            if not args:
                args = []

            if 'operating_unit_id' in self._fields:
                if context.get('record', {}).get('_field', False) \
                   and self.pool.get(context['record']['_name']) \
                   and context['record']['_field'] in self.pool.get(
                       context['record']['_name'])._fields \
                   and getattr(
                       self.pool.get(context['record']['_name'])._fields[
                           context['record']['_field']],
                       'operating_unit_isolation',
                       False):
                    isolation = getattr(
                        self.pool.get(context['record']['_name'])._fields[
                            context['record']['_field']],
                        'operating_unit_isolation').split('.')
                    filter_ou = False
                    if len(isolation) == 2:
                        if isolation[0] == context[
                                'parent_record']['_o2m']:
                            filter_ou = context[
                                'parent_record'][isolation[1]]
                    elif len(isolation) == 1:
                        filter_ou = context['record'][isolation[0]]

                    if filter_ou:
                        args.append((
                            'operating_unit_id', 'in', [False, filter_ou]
                        ))

            return _ou_search.origin(
                self, cr, user, args, offset=offset, limit=limit,
                order=order, context=context, count=count,
                access_rights_uid=access_rights_uid)

        ou_patched = getattr(models.BaseModel, 'ou_patch', None)
        if not ou_patched:
            models.BaseModel._patch_method('_search', _ou_search)
            models.BaseModel.ou_patched = True

        return super(BaseModelExtend, self)._register_hook(cr)
