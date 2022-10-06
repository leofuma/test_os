# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools


class Groups(models.Model):
    _inherit = 'res.groups'
    _rec_name = 'id'

    description = fields.Text(u'Descripción', required=True)
    user_roles = fields.One2many('res.users.role', 'group_id', string=u"Rol asociado")
    is_role = fields.Boolean('Grupo de Rol', compute="_compute_is_role", store=True)
    role_ids = fields.Many2many('res.users.role', string=u"Roles", compute='_compute_role_ids', search="_search_role_ids",
                                help=u"Roles en los que está incluido este grupo")

    @api.depends('user_roles')
    def _compute_is_role(self):
        for group in self:
            group.is_role = len(group.user_roles) > 0

    @api.multi
    def _compute_role_ids(self):
        all_groups_by_role = self._get_all_groups_by_role()
        for group in self:
            roles = self.env['res.users.role']
            for role, groups in all_groups_by_role.items():
                if group.id in groups.ids:
                    roles |= role
            group.role_ids = roles

    def _search_role_ids(self, operator, value):
        ids = []
        for role in self.env['res.users.role'].sudo().search([('name', operator, value)]):
            ids += role.trans_implied_ids.ids
        return [('id', 'in', ids)]

    @tools.ormcache()
    def _get_all_groups_by_role(self):
        result = {}
        for role in self.env['res.users.role'].sudo().search([]):
            result[role] = role.trans_implied_ids
        return result

    def get_application_groups(self, cr, uid, domain=None, context=None):
        domain = [('is_role','=',False)] + (domain or [])
        return super(Groups, self).get_application_groups(cr, uid, domain=domain, context=context)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('exclude_group_role', True):
            args = [('is_role','=',False)] + (args or [])
        return super(Groups, self)._search(args, offset=offset, limit=limit, order=order, count=count, access_rights_uid=access_rights_uid)

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if self._context.get('exclude_group_role', True):
            domain = [('is_role', '=', False)] + (domain or [])
        return super(Groups, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
