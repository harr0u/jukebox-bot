ALTER TABLE songs
    ADD created_at DATE DEFAULT (datetime('now','localtime'));

UPDATE jukebox_version SET version = 3;