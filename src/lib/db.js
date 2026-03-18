import Database from 'better-sqlite3';
import { parse } from 'csv-parse/sync';
import fs from 'fs';
import path from 'path';

// Create an in-memory database
const db = new Database(':memory:');

// Define the schema based on schema.sql but adapted for SQLite
db.exec(`
CREATE TABLE IF NOT EXISTS blocks (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    short_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS parties (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    short_name TEXT NOT NULL,
    block_id INTEGER REFERENCES blocks(id)
);

CREATE TABLE IF NOT EXISTS districts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    key TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS congressmen (
    id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    key TEXT NOT NULL,
    party_id INTEGER REFERENCES parties(id),
    district_id INTEGER REFERENCES districts(id),
    birth_date TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    block_id INTEGER REFERENCES blocks(id)
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL,
    session_number INTEGER NOT NULL,
    start_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS voting (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    start_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS votes (
    voting_id INTEGER NOT NULL REFERENCES voting(id) ON DELETE CASCADE,
    congressman_id INTEGER NOT NULL REFERENCES congressmen(id) ON DELETE CASCADE,
    vote_type TEXT NOT NULL,
    attendance_status TEXT NOT NULL,
    PRIMARY KEY (voting_id, congressman_id)
);

CREATE TABLE IF NOT EXISTS attendance (
    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    congressman_id INTEGER NOT NULL REFERENCES congressmen(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    PRIMARY KEY (session_id, congressman_id)
);
`);

/**
 * Helper to load and parse a CSV file synchronously.
 * @param {string} filename 
 * @returns {Array<Object>}
 */
function loadCSV(filename) {
    const filePath = path.resolve('./data', filename);
    if (!fs.existsSync(filePath)) {
        console.warn(`Warning: ${filePath} does not exist. Skipping.`);
        return [];
    }
    const fileContent = fs.readFileSync(filePath, 'utf8');
    return parse(fileContent, {
        columns: true,
        skip_empty_lines: true
    });
}

/**
 * Main ingestion function
 */
function ingestData() {
    console.log('Ingesting data into in-memory SQLite database...');

    // Load data
    const blocks = loadCSV('blocks.csv');
    const parties = loadCSV('parties.csv');
    const districts = loadCSV('districts.csv');
    const congressmen = loadCSV('congressmen.csv');
    const sessions = loadCSV('sessions.csv');
    const voting = loadCSV('voting.csv');
    const votes = loadCSV('votes.csv');
    const attendance = loadCSV('attendance.csv');

    // Prepare insert statements
    const insertBlock = db.prepare('INSERT OR IGNORE INTO blocks (id, name, short_name) VALUES (@id, @name, @short_name)');
    const insertParty = db.prepare('INSERT OR IGNORE INTO parties (id, name, short_name, block_id) VALUES (@id, @name, @short_name, @block_id)');
    const insertDistrict = db.prepare('INSERT OR IGNORE INTO districts (id, name, key) VALUES (@id, @name, @key)');
    const insertCongressman = db.prepare('INSERT OR IGNORE INTO congressmen (id, first_name, last_name, key, party_id, district_id, birth_date, status, block_id) VALUES (@id, @first_name, @last_name, @key, @party_id, @district_id, @birth_date, @status, @block_id)');
    const insertSession = db.prepare('INSERT OR IGNORE INTO sessions (id, type, session_number, start_date) VALUES (@id, @type, @session_number, @start_date)');
    const insertVoting = db.prepare('INSERT OR IGNORE INTO voting (id, session_id, subject, start_date) VALUES (@id, @session_id, @subject, @start_date)');
    const insertVote = db.prepare('INSERT OR IGNORE INTO votes (voting_id, congressman_id, vote_type, attendance_status) VALUES (@voting_id, @congressman_id, @vote_type, @attendance_status)');
    const insertAttendance = db.prepare('INSERT OR IGNORE INTO attendance (session_id, congressman_id, status) VALUES (@session_id, @congressman_id, @status)');

    // Execute in transactions for speed
    const insertMany = (stmt, items) => {
        const insert = db.transaction((items) => {
            for (const item of items) {
                Object.keys(item).forEach(key => {
                    if (item[key] === '') item[key] = null
                });
                stmt.run(item);
            }
        });
        insert(items);
    };

    insertMany(insertBlock, blocks);
    insertMany(insertParty, parties);
    insertMany(insertDistrict, districts);
    insertMany(insertCongressman, congressmen);
    insertMany(insertSession, sessions);
    insertMany(insertVoting, voting);
    insertMany(insertVote, votes);
    insertMany(insertAttendance, attendance);

    console.log('Data ingestion complete!');
}

// Run ingestion when this module is required
ingestData();

export default db;
