# -*- coding: utf-8 -*-
# Copyright 2014 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, SUPERUSER_ID


class ResUsers(models.Model):
    _inherit = 'res.users'

    role_line_ids = fields.One2many(
        'res.users.role.line', 'user_id', string=u"Role lines",
        default=lambda self: self._default_role_lines())
    role_ids = fields.One2many(
        'res.users.role', string=u"Roles",
        compute='_compute_role_ids')

    @api.model
    def _default_role_lines(self):
        if self.env.user.id == SUPERUSER_ID:
            return []
        default_user = self.env.ref(
            'base.default_user', raise_if_not_found=False)
        default_values = []
        if default_user:
            for role_line in default_user.role_line_ids:
                default_values.append({
                    'role_id': role_line.role_id.id,
                    'date_from': role_line.date_from,
                    'date_to': role_line.date_to,
                    'is_enabled': role_line.is_enabled,
                })
        return default_values

    @api.multi
    @api.depends('role_line_ids.role_id')
    def _compute_role_ids(self):
        for user in self:
            if user.id != SUPERUSER_ID:
                user.role_ids = user.role_line_ids.mapped('role_id')

    @api.model
    def create(self, vals):
        new_record = super(ResUsers, self).create(vals)
        new_record.set_groups_from_roles()
        return new_record

    @api.multi
    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        self.sudo().set_groups_from_roles()
        return res

    @api.multi
    def set_groups_from_roles(self):
        """Set (replace) the groups following the roles defined on users.
        If no role is defined on the user, its groups are let untouched.
        """
        for user in self:
            if not user.role_line_ids or user.id == SUPERUSER_ID:
                continue
            group_ids = []
            role_lines = user.role_line_ids.filtered(
                lambda rec: rec.is_enabled)
            for role_line in role_lines:
                role = role_line.role_id
                if role:
                    group_ids.append(role.group_id.id)
                    group_ids.extend(role.implied_ids.ids)
            group_ids = list(set(group_ids))    # Remove duplicates IDs
            vals = {
                'groups_id': [(6, 0, group_ids)],
            }
            super(ResUsers, user).write(vals)
        return True
