# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

######   Pivot View   #######

from openerp import tools
from openerp import api, fields, models

# security analysis view class for the pivot view
class SecurityAnalysis(models.Model):
    _name = "security.analysis"
    _description = "Security Analysis"
    _auto = False # Order that execute this code
    _rec_name = 'login'
    _order = 'login desc'

    # records to be displayed in the view (dimensions)
    login = fields.Char(u'login', readonly=True)
    profile = fields.Char(u'Profile', readonly=True)
    group = fields.Char(u'Group', readonly=True)
    role = fields.Char(u'Role', readonly=True)

    # records to be displayed in the view (measures)
    qty_user = fields.Integer('Qty user')

    # view selection
    def _select(self):
        select_str = """
              select row_number() over(order by r.id) as id,
                     login as login,
                     sp.name as profile,
                     rur.group_id as group,
                     rur.description as role
        """
        return select_str

    # view relations
    def _from(self):
        from_str = """
                res_users r 
                   join res_users_security_profile rup on rup.user_id = r.id 
                   left join security_profile sp on rup.profile_id = sp.id 
                   left join security_profile_user_role_rel spu on sp.id = spu.profile_id 
                   left join res_users_role rur on spu.role_id = rur.id 
        """
        return from_str

    # view group by
    def _group_by(self):
        group_by_str = """  """
        return group_by_str

    # view creation
    def init(self, cr):
        # asigned name from view
        self._table = "security_analysis_view"
        # check exist
        tools.drop_view_if_exists(cr, self._table)
        # building view
        cr.execute("""CREATE or REPLACE VIEW %s as
            %s
            FROM %s
            %s
            """ % (self._table, self._select(), self._from(), self._group_by()))
