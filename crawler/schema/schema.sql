DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'congressman_status') THEN
        CREATE TYPE congressman_status AS ENUM ('active', 'inactive');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'session_type') THEN
        CREATE TYPE session_type AS ENUM ('ordinaria', 'extraordinaria', 'solemne');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'attendance_status') THEN
        CREATE TYPE attendance_status AS ENUM ('presente', 'ausente', 'licencia_excusa');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'vote_type') THEN
        CREATE TYPE vote_type AS ENUM ('a_favor', 'en_contra', 'ausente');
    END IF;
END$$;

CREATE TABLE IF NOT EXISTS districts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    type session_type NOT NULL,
    session_number INTEGER NOT NULL,
    start_date TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS blocks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    short_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS parties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    short_name VARCHAR(100) NOT NULL,
    block_id INTEGER REFERENCES blocks(id)
);

CREATE TABLE IF NOT EXISTS congressmen (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    key VARCHAR(512) NOT NULL,
    party_id INTEGER NOT NULL REFERENCES parties(id),
    district_id INTEGER NOT NULL REFERENCES districts(id),
    birth_date DATE,
    status congressman_status NOT NULL DEFAULT 'active',
    block_id INTEGER REFERENCES blocks(id)
);

CREATE TABLE IF NOT EXISTS voting (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    start_date TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS votes (
    voting_id INTEGER NOT NULL REFERENCES voting(id) ON DELETE CASCADE,
    congressman_id INTEGER NOT NULL REFERENCES congressmen(id) ON DELETE CASCADE,
    vote_type vote_type NOT NULL,
    attendance_status attendance_status NOT NULL,
    PRIMARY KEY (voting_id, congressman_id)
);

CREATE TABLE IF NOT EXISTS attendance (
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    congressman_id INTEGER NOT NULL REFERENCES congressmen(id) ON DELETE CASCADE,
    status attendance_status NOT NULL,
    PRIMARY KEY (session_id, congressman_id)
);

CREATE TABLE IF NOT EXISTS congressmen_aliases (
    id SERIAL PRIMARY KEY,
    congressman_id INTEGER NOT NULL REFERENCES congressmen(id) ON DELETE CASCADE,
    alias VARCHAR(255) NOT NULL UNIQUE
);
