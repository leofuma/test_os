select 
	row_number() over(order by g.id) as ide,
	g.id, 
	g.name, 
	i.gid, 
	i.hid, 
	f.name, 
	count(i.gid)
from 
	res_groups as g
	left join res_groups_implied_rel as i on g.id = i.gid
	left join res_groups as f on i.hid = f.id 
group by 
	g.id, 
	g.name, 
	i.gid, 
	i.hid, 
	f.name;
