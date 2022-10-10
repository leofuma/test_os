select 
    row_number() over(order by u.id) as id,
    u.id as user_id,
    up.profile_id as profile_id,
	case g.is_role
	    when 't' then gu.gid
	    end
	as role_id,
	gu.gid as group_id
from
	res_users as u
	left join res_users_security_profile as up on up.user_id = u.id
	left join res_groups_users_rel as gu on gu.uid = u.id
	left join res_groups as g on g.id = gu.gid;
