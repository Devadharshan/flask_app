sp_tables_count
sql
Copy code
CREATE PROCEDURE sp_tables_count AS
BEGIN
    SELECT COUNT(*) AS table_count
    FROM sysobjects
    WHERE type = 'U'
END
sp_views_count
sql
Copy code
CREATE PROCEDURE sp_views_count AS
BEGIN
    SELECT COUNT(*) AS view_count
    FROM sysobjects
    WHERE type = 'V'
END
sp_procedures_count
sql
Copy code
CREATE PROCEDURE sp_procedures_count AS
BEGIN
    SELECT COUNT(*) AS procedure_count
    FROM sysobjects
    WHERE type = 'P'
END
