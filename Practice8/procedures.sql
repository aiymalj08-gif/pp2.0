CREATE OR REPLACE PROCEDURE upsert_contact(p_name VARCHAR, p_phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM contacts WHERE name = p_name) THEN
        UPDATE contacts SET phone = p_phone WHERE name = p_name;
        RAISE NOTICE 'Updated: % -> %', p_name, p_phone;
    ELSE
        INSERT INTO contacts(name, phone) VALUES (p_name, p_phone);
        RAISE NOTICE 'Inserted: % -> %', p_name, p_phone;
    END IF;
END;
$$;


CREATE OR REPLACE PROCEDURE bulk_insert_contacts(p_names TEXT[], p_phones TEXT[])
LANGUAGE plpgsql AS $$
DECLARE
    i            INT;
    invalid_data TEXT[] := ARRAY[]::TEXT[];
BEGIN
    IF array_length(p_names, 1) IS DISTINCT FROM array_length(p_phones, 1) THEN
        RAISE EXCEPTION 'Arrays must be the same length';
    END IF;

    FOR i IN 1..array_length(p_names, 1) LOOP
        IF p_phones[i] ~ '^[0-9]{11}$' THEN
            CALL upsert_contact(p_names[i], p_phones[i]);
        ELSE
            RAISE NOTICE 'Invalid phone - skipped: name=%, phone=%', p_names[i], p_phones[i];
            invalid_data := array_append(invalid_data, p_names[i] || ':' || p_phones[i]);
        END IF;
    END LOOP;

    IF array_length(invalid_data, 1) > 0 THEN
        RAISE NOTICE 'Invalid entries: %', array_to_string(invalid_data, ', ');
    END IF;
END;
$$;


CREATE OR REPLACE PROCEDURE delete_contact(p_name VARCHAR DEFAULT NULL, p_phone VARCHAR DEFAULT NULL)
LANGUAGE plpgsql AS $$
DECLARE
    rows_deleted INT;
BEGIN
    IF p_name IS NULL AND p_phone IS NULL THEN
        RAISE EXCEPTION 'Provide at least a name or a phone to delete';
    END IF;

    DELETE FROM contacts
    WHERE (p_name  IS NOT NULL AND name  = p_name)
       OR (p_phone IS NOT NULL AND phone = p_phone);

    GET DIAGNOSTICS rows_deleted = ROW_COUNT;

    IF rows_deleted = 0 THEN
        RAISE NOTICE 'No contact found for name=% phone=%', p_name, p_phone;
    ELSE
        RAISE NOTICE 'Deleted % contact(s).', rows_deleted;
    END IF;
END;
$$;