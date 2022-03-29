ALTER TABLE songs
    ADD telegram_name text;

UPDATE jukebox_version SET version = 2;