-- ============================================================
--  PhoneBook  –  New Stored Procedures & Functions (TSIS 1)
--  Do NOT re-define anything already in Practice 8's files.
-- ============================================================


-- 1. add_phone ---------------------------------------------
--    Adds a phone number to an existing contact by name.
CREATE OR REPLACE PROCEDURE add_phone(
    p_contact_name VARCHAR,
    p_phone        VARCHAR,
    p_type         VARCHAR   -- 'home' | 'work' | 'mobile'
)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INT;
BEGIN
    SELECT id INTO v_contact_id
    FROM contacts
    WHERE name = p_contact_name;

    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;

    IF p_type NOT IN ('home', 'work', 'mobile') THEN
        RAISE EXCEPTION 'Invalid phone type "%". Use home | work | mobile', p_type;
    END IF;

    INSERT INTO phones (contact_id, phone, type)
    VALUES (v_contact_id, p_phone, p_type);

    RAISE NOTICE 'Phone % (%) added to %', p_phone, p_type, p_contact_name;
END;
$$;


-- 2. move_to_group -----------------------------------------
--    Moves a contact to a group; creates the group if needed.
CREATE OR REPLACE PROCEDURE move_to_group(
    p_contact_name VARCHAR,
    p_group_name   VARCHAR
)
LANGUAGE plpgsql AS $$
DECLARE
    v_group_id   INT;
    v_contact_id INT;
BEGIN
    -- Resolve (or create) the group
    SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;
    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO v_group_id;
        RAISE NOTICE 'Created new group: %', p_group_name;
    END IF;

    -- Verify the contact exists
    SELECT id INTO v_contact_id FROM contacts WHERE name = p_contact_name;
    IF v_contact_id IS NULL THEN
        RAISE EXCEPTION 'Contact "%" not found', p_contact_name;
    END IF;

    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
    RAISE NOTICE 'Moved "%" to group "%"', p_contact_name, p_group_name;
END;
$$;


-- 3. search_contacts ----------------------------------------
--    Extends the Practice-8 pattern search to also cover:
--      • email
--      • all phone numbers in the phones table
--    Returns one row per contact (deduped via DISTINCT ON).
CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE (
    id       INT,
    name     VARCHAR,
    email    VARCHAR,
    birthday DATE,
    grp      VARCHAR,
    phones   TEXT          -- comma-separated list of phone numbers
)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
        SELECT DISTINCT ON (c.id)
            c.id,
            c.name,
            c.email,
            c.birthday,
            g.name  AS grp,
            STRING_AGG(ph.phone || ' (' || COALESCE(ph.type, '?') || ')', ', ')
                OVER (PARTITION BY c.id) AS phones
        FROM contacts c
        LEFT JOIN groups g  ON g.id  = c.group_id
        LEFT JOIN phones ph ON ph.contact_id = c.id
        WHERE
            c.name  ILIKE '%' || p_query || '%'
            OR c.email ILIKE '%' || p_query || '%'
            OR ph.phone ILIKE '%' || p_query || '%'
        ORDER BY c.id;
END;
$$;