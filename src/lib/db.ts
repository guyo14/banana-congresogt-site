import Database, { type Statement } from 'better-sqlite3';
import { parse } from 'csv-parse/sync';
import fs from 'fs';
import path from 'path';

interface Block {
    id: number;
    name: string;
    short_name: string;
}

interface Party {
    id: number;
    name: string;
    short_name: string;
    block_id: number | null;
}

interface District {
    id: number;
    name: string;
    key: string;
}

interface Congressman {
    id: number;
    first_name: string;
    last_name: string;
    party_id: number;
    district_id: number;
    birth_date: string;
    status: number;
    block_id: number | null;
}

interface Session {
    id: number;
    type: string;
    session_number: number;
    start_date: string;
    period: string;
}

interface Voting {
    id: number;
    session_id: number;
    subject: string;
    votes_in_favor_x: number;
    votes_against_x: number;
    votes_absent_x: number;
    attendance_present_x: number;
    attendance_absent_x: number;
    attendance_license_x: number;
    majority_x: number;
    votes_in_favor_y: number;
    votes_against_y: number;
    votes_absent_y: number;
    attendance_present_y: number;
    attendance_absent_y: number;
    attendance_license_y: number;
    majority_y: number;
}

interface Vote {
    voting_id: number;
    congressman_id: number;
    vote_type: number;
    attendance_status: string;
    session_id: number;
    period: string;
    with_majority: boolean;
}

interface Attendance {
    session_id: number;
    congressman_id: number;
    status: number;
}


interface CongressmanStats {
    id: number;
    period: string;
    attendance_present: number;
    attendance_absent: number;
    attendance_license: number;
    votes_in_favor: number;
    votes_against: number;
    votes_absent: number;
    votes_with_majority: number;
    votes_against_majority: number;
}

interface PartyStats {
    id: number;
    period: string;
    attendance_present: number;
    attendance_absent: number;
    attendance_license: number;
    votes_in_favor: number;
    votes_against: number;
    votes_absent: number;
    rice_index: number;
}

interface DistrictStats {
    id: number;
    period: string;
    attendance_present: number;
    attendance_absent: number;
    attendance_license: number;
    votes_in_favor: number;
    votes_against: number;
    votes_absent: number;
    rice_index: number;
}

interface BlockStats {
    id: number;
    period: string;
    attendance_present: number;
    attendance_absent: number;
    attendance_license: number;
    votes_in_favor: number;
    votes_against: number;
    votes_absent: number;
    rice_index: number;
}

interface CongressmanSimilarity {
    congressman_id: number;
    congressman_2_id: number;
    similarity_score: number;
    common_votes: number;
    same_votes: number;
    agreement_percentage: number;
}

// Create an in-memory database
const db = new Database(':memory:');

// Define the schema to load csv files
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
    block_id INTEGER NOT NULL
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
    party_id INTEGER NOT NULL,
    district_id INTEGER NOT NULL,
    birth_date TEXT,
    status INTEGER NOT NULL,
    block_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY,
    type INTEGER NOT NULL,
    session_number INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    period TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS voting (
    id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    votes_in_favor INTEGER NOT NULL,
    votes_against INTEGER NOT NULL,
    votes_absent INTEGER NOT NULL,
    attendance_present INTEGER NOT NULL,
    attendance_absent INTEGER NOT NULL,
    attendance_license INTEGER NOT NULL,
    majority INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS votes (
    voting_id INTEGER NOT NULL,
    congressman_id INTEGER NOT NULL,
    vote_type INTEGER NOT NULL,
    attendance_status TEXT NOT NULL,
    session_id INTEGER NOT NULL,
    period TEXT NOT NULL,
    with_majority INTEGER NOT NULL,
    PRIMARY KEY (voting_id, congressman_id)
);

CREATE TABLE IF NOT EXISTS attendance (
    session_id INTEGER NOT NULL,
    congressman_id INTEGER NOT NULL,
    status INTEGER NOT NULL,
    PRIMARY KEY (session_id, congressman_id)
);

CREATE TABLE IF NOT EXISTS congressman_stats (
    id INTEGER NOT NULL,
    period TEXT NOT NULL,
    attendance_present INTEGER NOT NULL,
    attendance_absent INTEGER NOT NULL,
    attendance_license INTEGER NOT NULL,
    votes_in_favor INTEGER NOT NULL,
    votes_against INTEGER NOT NULL,
    votes_absent INTEGER NOT NULL,
    votes_with_majority INTEGER NOT NULL,
    votes_against_majority INTEGER NOT NULL,
    PRIMARY KEY (id, period)
);

CREATE TABLE IF NOT EXISTS party_stats (
    id INTEGER NOT NULL,
    period TEXT NOT NULL,
    attendance_present INTEGER NOT NULL,
    attendance_absent INTEGER NOT NULL,
    attendance_license INTEGER NOT NULL,
    votes_in_favor INTEGER NOT NULL,
    votes_against INTEGER NOT NULL,
    votes_absent INTEGER NOT NULL,
    rice_index REAL NOT NULL,
    PRIMARY KEY (id, period)
);

CREATE TABLE IF NOT EXISTS district_stats (
    id INTEGER NOT NULL,
    period TEXT NOT NULL,
    attendance_present INTEGER NOT NULL,
    attendance_absent INTEGER NOT NULL,
    attendance_license INTEGER NOT NULL,
    votes_in_favor INTEGER NOT NULL,
    votes_against INTEGER NOT NULL,
    votes_absent INTEGER NOT NULL,
    rice_index REAL NOT NULL,
    PRIMARY KEY (id, period)
);

CREATE TABLE IF NOT EXISTS block_stats (
    id INTEGER NOT NULL,
    period TEXT NOT NULL,
    attendance_present INTEGER NOT NULL,
    attendance_absent INTEGER NOT NULL,
    attendance_license INTEGER NOT NULL,
    votes_in_favor INTEGER NOT NULL,
    votes_against INTEGER NOT NULL,
    votes_absent INTEGER NOT NULL,
    rice_index REAL NOT NULL,
    PRIMARY KEY (id, period)
);

CREATE TABLE IF NOT EXISTS congressman_similarity (
    congressman_id INTEGER NOT NULL,
    congressman_2_id INTEGER NOT NULL,
    similarity_score REAL NOT NULL,
    common_votes INTEGER NOT NULL,
    same_votes INTEGER NOT NULL,
    agreement_percentage REAL NOT NULL,
    PRIMARY KEY (congressman_id, congressman_2_id)
);
`);

function loadCSV<T>(filename: string): T[] {
    const filePath = path.resolve('./data', filename);
    if (!fs.existsSync(filePath)) {
        console.warn(`Warning: ${filePath} does not exist. Skipping.`);
        return [];
    }
    const fileContent = fs.readFileSync(filePath, 'utf8');
    return parse(fileContent, {
        columns: true,
        skip_empty_lines: true
    }) as T[];
}

/**
 * Main ingestion function
 */
function ingestData() {
    console.log('Ingesting data into in-memory SQLite database...');

    // Load data
    const blocks: Block[] = loadCSV('blocks.csv');
    const parties: Party[] = loadCSV('parties.csv');
    const districts: District[] = loadCSV('districts.csv');
    const congressmen: Congressman[] = loadCSV('congressmen.csv');
    const sessions: Session[] = loadCSV('sessions.csv');
    const voting: Voting[] = loadCSV('voting.csv');
    const votes: Vote[] = loadCSV('votes.csv');
    const attendance: Attendance[] = loadCSV('attendance.csv');

    // Derived pre-aggregated data
    const c_stats: CongressmanStats[] = loadCSV('congressman_stats.csv');
    const p_stats: PartyStats[] = loadCSV('party_stats.csv');
    const d_stats: DistrictStats[] = loadCSV('district_stats.csv');
    const b_stats: BlockStats[] = loadCSV('block_stats.csv');
    const c_sim: CongressmanSimilarity[] = loadCSV('congressman_similarity.csv');

    // Prepare insert statements
    const insertBlock = db.prepare<Block>('INSERT INTO blocks (id, name, short_name) VALUES (@id, @name, @short_name)');
    const insertParty = db.prepare<Party>('INSERT INTO parties (id, name, short_name, block_id) VALUES (@id, @name, @short_name, @block_id)');
    const insertDistrict = db.prepare<District>('INSERT INTO districts (id, name, key) VALUES (@id, @name, @key)');
    const insertCongressman = db.prepare<Congressman>('INSERT INTO congressmen (id, first_name, last_name, party_id, district_id, birth_date, status, block_id) VALUES (@id, @first_name, @last_name, @party_id, @district_id, @birth_date, @status, @block_id)');
    const insertSession = db.prepare<Session>('INSERT INTO sessions (id, type, session_number, start_date, period) VALUES (@id, @type, @session_number, @start_date, @period)');
    const insertVoting = db.prepare<Voting>('INSERT INTO voting (id, session_id, subject, votes_in_favor, votes_against, votes_absent, attendance_present, attendance_absent, attendance_license, majority) VALUES (@id, @session_id, @subject, @votes_in_favor, @votes_against, @votes_absent, @attendance_present, @attendance_absent, @attendance_license, @majority)');
    const insertVote = db.prepare<Vote>('INSERT INTO votes (voting_id, congressman_id, vote_type, attendance_status, session_id, period, with_majority) VALUES (@voting_id, @congressman_id, @vote_type, @attendance_status, @session_id, @period, @with_majority)');
    const insertAttendance = db.prepare<Attendance>('INSERT INTO attendance (session_id, congressman_id, status) VALUES (@session_id, @congressman_id, @status)');

    // Prep statements for aggregated data
    const insertCStats = db.prepare<CongressmanStats>('INSERT INTO congressman_stats (id, period, attendance_present, attendance_absent, attendance_license, votes_in_favor, votes_against, votes_absent, votes_with_majority, votes_against_majority) VALUES (@id, @period, @attendance_present, @attendance_absent, @attendance_license, @votes_in_favor, @votes_against, @votes_absent, @votes_with_majority, @votes_against_majority)');
    const insertPStats = db.prepare<PartyStats>('INSERT INTO party_stats (id, period, attendance_present, attendance_absent, attendance_license, votes_in_favor, votes_against, votes_absent, rice_index) VALUES (@id, @period, @attendance_present, @attendance_absent, @attendance_license, @votes_in_favor, @votes_against, @votes_absent, @rice_index)');
    const insertDStats = db.prepare<DistrictStats>('INSERT INTO district_stats (id, period, attendance_present, attendance_absent, attendance_license, votes_in_favor, votes_against, votes_absent, rice_index) VALUES (@id, @period, @attendance_present, @attendance_absent, @attendance_license, @votes_in_favor, @votes_against, @votes_absent, @rice_index)');
    const insertBStats = db.prepare<BlockStats>('INSERT INTO block_stats (id, period, attendance_present, attendance_absent, attendance_license, votes_in_favor, votes_against, votes_absent, rice_index) VALUES (@id, @period, @attendance_present, @attendance_absent, @attendance_license, @votes_in_favor, @votes_against, @votes_absent, @rice_index)');
    const insertCSim = db.prepare<CongressmanSimilarity>('INSERT INTO congressman_similarity (congressman_id, congressman_2_id, similarity_score, common_votes, same_votes, agreement_percentage) VALUES (@congressman_id, @congressman_2_id, @similarity_score, @common_votes, @same_votes, @agreement_percentage)');

    // Execute in transactions for speed
    const insertMany = <T extends {}>(stmt: Statement<[T], any>, items: T[]) => {
        const insert = db.transaction((items: T[]) => {
            for (const item of items) stmt.run(item);
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