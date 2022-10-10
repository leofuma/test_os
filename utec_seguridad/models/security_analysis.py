# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

######   Pivot View   #######

from openerp import api, fields, models, tools

# security analysis view class for the pivot view
class SecurityAnalysis(models.Model):
    _name = "security.analysis"
    _description = "Security Analysis"
    _auto = False # Order that execute this code
    _rec_name = 'user_id'
    _order = 'user_id desc'

    # records to be displayed in the view (dimensions)
    # login = fields.Char(u'login', readonly=True)
    profile_id = fields.Many2one('security.profile','Profile', readonly=True)
    group_id = fields.Many2one('res.groups', 'Group', readonly=True)
    user_id = fields.Many2one('res.users','User', readonly=True)
    role_id = fields.Many2one('res.users.role','Role', readonly=True)


   # view selection
    def _select(self):
        select_str = """
        select 
            row_number() over(order by u.id) as id,
            u.id as user_id,
            up.profile_id as profile_id,
            case g.is_role
                when 't' then gu.gid
                end
            as role_id,
            gu.gid as group_id
            """
        return select_str

    # view relations
    def _from(self):
        from_str = """
            res_users as u
            left join res_users_security_profile as up on up.user_id = u.id
            left join res_groups_users_rel as gu on gu.uid = u.id
            left join res_groups as g on g.id = gu.gid;
        """
        return from_str

    # view group by
    def _group_by(self):
        group_by_str = """  """
        return group_by_str

    # view creation
    def init(self, cr):
        # check exist
        tools.drop_view_if_exists(cr, self._table)
        # building view
        cr.execute("""CREATE or REPLACE VIEW %s as
            %s
            FROM %s
            %s
            ;
            """ % (self._table, self._select(), self._from(), self._group_by()))

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """
            Inherit read_group to calculate the sum of the non-stored fields, as it is not automatically done anymore through the XML.
        """
        res = super(SecurityAnalysis, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if "user_id" in fields:
            for re in res:
                if re.get('__domain'):
                    sa = self.search(re['__domain'])
                    users = sa.mapped("user_id")
                    print('DDDDD', users)
                    re["user_id"] = (str(len(users)), str(len(users)))
        return res