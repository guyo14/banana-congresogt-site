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

CREATE TABLE IF NOT EXISTS votation_aggregated_stats (
    voting_id INTEGER NOT NULL REFERENCES voting(id) ON DELETE CASCADE,
    total_favor INTEGER NOT NULL,
    total_contra INTEGER NOT NULL,
    total_absent INTEGER NOT NULL,
    is_approved BOOLEAN NOT NULL,
    PRIMARY KEY (voting_id)
);

CREATE TABLE IF NOT EXISTS congressman_stats (
    id INTEGER NOT NULL REFERENCES congressmen(id) ON DELETE CASCADE,
    period TEXT NOT NULL,
    attendance_present INTEGER NOT NULL,
    attendance_absent INTEGER NOT NULL,
    attendance_excused INTEGER NOT NULL,
    votes_favor INTEGER NOT NULL,
    votes_contra INTEGER NOT NULL,
    votes_absent INTEGER NOT NULL,
    votes_with_majority INTEGER NOT NULL,
    PRIMARY KEY (id, period)
);

CREATE TABLE IF NOT EXISTS party_stats (
    id INTEGER NOT NULL REFERENCES parties(id) ON DELETE CASCADE,
    period TEXT NOT NULL,
    attendance_present INTEGER NOT NULL,
    attendance_absent INTEGER NOT NULL,
    attendance_excused INTEGER NOT NULL,
    votes_favor INTEGER NOT NULL,
    votes_contra INTEGER NOT NULL,
    votes_absent INTEGER NOT NULL,
    rice_index REAL NOT NULL,
    PRIMARY KEY (id, period)
);

CREATE TABLE IF NOT EXISTS district_stats (
    id INTEGER NOT NULL REFERENCES districts(id) ON DELETE CASCADE,
    period TEXT NOT NULL,
    attendance_present INTEGER NOT NULL,
    attendance_absent INTEGER NOT NULL,
    attendance_excused INTEGER NOT NULL,
    votes_favor INTEGER NOT NULL,
    votes_contra INTEGER NOT NULL,
    votes_absent INTEGER NOT NULL,
    rice_index REAL NOT NULL,
    PRIMARY KEY (id, period)
);

CREATE TABLE IF NOT EXISTS block_stats (
    id TEXT NOT NULL,
    period TEXT NOT NULL,
    attendance_present INTEGER NOT NULL,
    attendance_absent INTEGER NOT NULL,
    attendance_excused INTEGER NOT NULL,
    votes_favor INTEGER NOT NULL,
    votes_contra INTEGER NOT NULL,
    votes_absent INTEGER NOT NULL,
    rice_index REAL NOT NULL,
    PRIMARY KEY (id, period)
);

CREATE TABLE IF NOT EXISTS congressman_similarity (
    congressman_id INTEGER NOT NULL REFERENCES congressmen(id) ON DELETE CASCADE,
    congressman_2_id INTEGER NOT NULL REFERENCES congressmen(id) ON DELETE CASCADE,
    similarity_score REAL NOT NULL,
    PRIMARY KEY (congressman_id, congressman_2_id)
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
    
    // Derived pre-aggregated data
    const v_stats = loadCSV('votation_aggregated_stats.csv');
    const c_stats = loadCSV('congressman_stats.csv');
    const p_stats = loadCSV('party_stats.csv');
    const d_stats = loadCSV('district_stats.csv');
    const b_stats = loadCSV('block_stats.csv');
    const c_sim = loadCSV('congressman_similarity.csv');

    // Prepare insert statements
    const insertBlock = db.prepare('INSERT OR IGNORE INTO blocks (id, name, short_name) VALUES (@id, @name, @short_name)');
    const insertParty = db.prepare('INSERT OR IGNORE INTO parties (id, name, short_name, block_id) VALUES (@id, @name, @short_name, @block_id)');
    const insertDistrict = db.prepare('INSERT OR IGNORE INTO districts (id, name, key) VALUES (@id, @name, @key)');
    const insertCongressman = db.prepare('INSERT OR IGNORE INTO congressmen (id, first_name, last_name, key, party_id, district_id, birth_date, status, block_id) VALUES (@id, @first_name, @last_name, @key, @party_id, @district_id, @birth_date, @status, @block_id)');
    const insertSession = db.prepare('INSERT OR IGNORE INTO sessions (id, type, session_number, start_date) VALUES (@id, @type, @session_number, @start_date)');
    const insertVoting = db.prepare('INSERT OR IGNORE INTO voting (id, session_id, subject, start_date) VALUES (@id, @session_id, @subject, @start_date)');
    const insertVote = db.prepare('INSERT OR IGNORE INTO votes (voting_id, congressman_id, vote_type, attendance_status) VALUES (@voting_id, @congressman_id, @vote_type, @attendance_status)');
    const insertAttendance = db.prepare('INSERT OR IGNORE INTO attendance (session_id, congressman_id, status) VALUES (@session_id, @congressman_id, @status)');

    // Prep statements for aggregated data
    const insertVStats = db.prepare('INSERT OR IGNORE INTO votation_aggregated_stats (voting_id, total_favor, total_contra, total_absent, is_approved) VALUES (@voting_id, @total_favor, @total_contra, @total_absent, @is_approved)');
    const insertCStats = db.prepare('INSERT OR IGNORE INTO congressman_stats (id, period, attendance_present, attendance_absent, attendance_excused, votes_favor, votes_contra, votes_absent, votes_with_majority) VALUES (@id, @period, @attendance_present, @attendance_absent, @attendance_excused, @votes_favor, @votes_contra, @votes_absent, @votes_with_majority)');
    const insertPStats = db.prepare('INSERT OR IGNORE INTO party_stats (id, period, attendance_present, attendance_absent, attendance_excused, votes_favor, votes_contra, votes_absent, rice_index) VALUES (@id, @period, @attendance_present, @attendance_absent, @attendance_excused, @votes_favor, @votes_contra, @votes_absent, @rice_index)');
    const insertDStats = db.prepare('INSERT OR IGNORE INTO district_stats (id, period, attendance_present, attendance_absent, attendance_excused, votes_favor, votes_contra, votes_absent, rice_index) VALUES (@id, @period, @attendance_present, @attendance_absent, @attendance_excused, @votes_favor, @votes_contra, @votes_absent, @rice_index)');
    const insertBStats = db.prepare('INSERT OR IGNORE INTO block_stats (id, period, attendance_present, attendance_absent, attendance_excused, votes_favor, votes_contra, votes_absent, rice_index) VALUES (@id, @period, @attendance_present, @attendance_absent, @attendance_excused, @votes_favor, @votes_contra, @votes_absent, @rice_index)');
    const insertCSim = db.prepare('INSERT OR IGNORE INTO congressman_similarity (congressman_id, congressman_2_id, similarity_score) VALUES (@congressman_id, @congressman_2_id, @similarity_score)');

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

    insertMany(insertVStats, v_stats);
    insertMany(insertCStats, c_stats);
    insertMany(insertPStats, p_stats);
    insertMany(insertDStats, d_stats);
    insertMany(insertBStats, b_stats);
    insertMany(insertCSim, c_sim);

    console.log('Data ingestion complete!');
}

// Run ingestion when this module is required
ingestData();

export default db;
export const CONGRESSMEN_STATUS = { ACTIVE: 'active', INACTIVE: 'inactive' };
export const ATTENDANCE_STATUS = { PRESENT: 'present', ABSENT: 'absent', EXCUSED: 'license'};
export const VOTE_TYPE = { IN_FAVOR: 'in_favor', AGAINST: 'against', ABSENT: 'absent' };