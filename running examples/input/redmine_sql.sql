q1
SELECT  roles.* FROM roles WHERE roles.builtin = $1

q2
SELECT  attachments.* FROM attachments WHERE attachments.digest = $1 AND attachments.filesize = $2

q3
SELECT  auth_sources.* FROM auth_sources WHERE auth_sources.id = $1

q4
SELECT 
	custom_fields.* 
FROM 
	custom_fields 
INNER JOIN 
	custom_fields_trackers 
ON 
	custom_fields.id = custom_fields_trackers.custom_field_id 
WHERE 
	custom_fields.type IN ('IssueCustomField') 
	AND custom_fields_trackers.tracker_id = $1

q5 
SELECT 
	DISTINCT users.* 
FROM 
	users 
INNER JOIN 
	email_addresses 
ON 
	email_addresses.user_id = users.id 
WHERE 
	users.type IN ('User', 'AnonymousUser') 
	AND (LOWER(email_addresses.address) IN ('jsmith@somenet.foo'))
ORDER BY 
	users.id ASC;

// Here we do not have any parameters to fill in

q6
SELECT 
	users.* 
FROM 
	users 
INNER JOIN
	watchers 
ON 
	users.id = watchers.user_id 
WHERE 
	watchers.watchable_id = $1 
	AND watchers.watchable_type = $2 
	AND users.status = $3


q7
SELECT 
	custom_values.* 
FROM 
	custom_values 
WHERE 
	custom_values.customized_id = $1 
	AND custom_values.customized_type = $2


q8
SELECT 
	MAX(custom_field_enumerations.position) 
FROM 
	custom_field_enumerations 
WHERE 
	custom_field_enumerations.custom_field_id = $1

