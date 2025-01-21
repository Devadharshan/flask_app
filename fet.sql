CREATE OR REPLACE VIEW User_Tasks_View AS
SELECT
    task.sys_id AS task_id,
    task.number AS task_number,
    task.short_description,
    task.description,
    task.state,
    task.priority,
    task.assigned_to,
    task.assignment_group,
    task.sys_created_on AS created_on,
    task.sys_updated_on AS updated_on,
    task.opened_at,
    task.closed_at,
    task.close_notes, -- Close notes field
    task.requester,
    task.catalog_type,
    task.due_date,
    assignment_group.name AS assignment_group_name,
    user.name AS assigned_to_name,
    user.email AS assigned_to_email,
    
    -- Calculated Fields
    TIMESTAMPDIFF(SECOND, task.opened_at, task.closed_at) AS time_to_close_seconds, -- Total time to close (in seconds)
    TIMESTAMPDIFF(DAY, task.opened_at, task.closed_at) AS time_to_close_days, -- Total time to close (in days)
    CASE
        WHEN task.state = 'Resolved' THEN TIMESTAMPDIFF(SECOND, task.opened_at, task.closed_at)
        ELSE NULL
    END AS time_to_resolve_seconds, -- Time to resolve only for resolved tasks
    CASE
        WHEN task.state = 'Closed' THEN TIMESTAMPDIFF(SECOND, task.opened_at, task.closed_at)
        ELSE NULL
    END AS time_to_close_seconds_closed, -- Time to close only for closed tasks
    CASE
        WHEN task.closed_at IS NULL THEN TIMESTAMPDIFF(SECOND, task.opened_at, NOW())
        ELSE NULL
    END AS time_open_seconds -- Time the task has been open (for active tasks)
FROM
    task
LEFT JOIN
    sys_user AS user ON task.assigned_to = user.sys_id
LEFT JOIN
    sys_user_group AS assignment_group ON task.assignment_group = assignment_group.sys_id
WHERE
    task.assignment_group IN ('GroupA', 'GroupB', 'GroupC') -- Replace with target groups
    AND task.sys_class_name = 'task' -- Ensure you're fetching tasks/requests
    AND (task.state IN ('Open', 'In Progress', 'Resolved', 'Closed') OR task.active = true); -- Active or specific states