CREATE TABLE IF NOT EXISTS telegram.users (
	user_id int8 NOT NULL,
	username text NULL,
	first_name text NULL,
	last_name text NULL,
	title text NULL,
	is_bot bool DEFAULT false NULL,
	json_data json NOT NULL,
	created_at timestamptz DEFAULT now() NULL,
	CONSTRAINT users_pkey PRIMARY KEY (user_id)
);



CREATE TABLE IF NOT EXISTS telegram.raw_messages (
	id bigserial NOT NULL,
	message_id int8 NOT NULL,
	chat_id int8 NOT NULL,
	sender_id int8 NULL,
	json_data json NOT NULL,
	received_at timestamptz DEFAULT now() NULL,
	CONSTRAINT raw_messages_pkey PRIMARY KEY (id),
	CONSTRAINT raw_messages_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES telegram.users(user_id) ON DELETE SET NULL
);
CREATE INDEX idx_raw_messages_chat_id ON telegram.raw_messages USING btree (chat_id);

ALTER TABLE telegram.raw_messages
    ADD COLUMN username text GENERATED ALWAYS AS (
        (SELECT u.username FROM telegram.users u WHERE u.user_id = sender_id)
    ) STORED;
    -- The original GENERATED ALWAYS AS expression for username cannot use a subquery.
    -- Instead, create a trigger to keep the username column updated.
    ALTER TABLE telegram.raw_messages
        ADD COLUMN username text;

    CREATE OR REPLACE FUNCTION telegram.update_raw_messages_username()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.sender_id IS NOT NULL THEN
            SELECT username INTO NEW.username FROM telegram.users WHERE user_id = NEW.sender_id;
        ELSE
            NEW.username := NULL;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS set_username_on_raw_messages_insert ON telegram.raw_messages;

    CREATE TRIGGER set_username_on_raw_messages_insert
    BEFORE INSERT OR UPDATE OF sender_id
    ON telegram.raw_messages
    FOR EACH ROW
    EXECUTE FUNCTION telegram.update_raw_messages_username();


    CREATE OR REPLACE VIEW telegram.raw_messages_simple AS
    SELECT
        -- Get chat username (if known, else NULL)
        (SELECT u.username FROM telegram.users u WHERE u.user_id = rm.chat_id) AS chat_username,
        -- Get sender username (if known, else NULL)
        (SELECT u.username FROM telegram.users u WHERE u.user_id = rm.sender_id) AS sender_username,
        rm.received_at AS time,
        -- Select 'message' field if present, else 'caption', else NULL
        COALESCE(
            rm.json_data->>'message',
            rm.json_data->>'caption'
        ) AS text
    FROM telegram.raw_messages rm;
    


