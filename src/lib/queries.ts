import db from "./db.ts";
import {ATTENDANCE_STATUS, CONGRESSMAN_STATUS, PERIOD, VOTE_TYPE} from "./mappers.ts";

export interface CountQuery {
  count: number;
}

export interface IdQuery {
  id: number;
}

export interface NoParams extends Array<unknown> { }

interface MinifiedCongressman {
  id: number;
  firstName: string;
  lastName: string;
}

interface Congressman extends MinifiedCongressman {
  partyId: number;
  partyName: string;
  districtId: number;
  districtName: string;
  blockId: number;
  blockName: string;
  actionValue: number;
}

interface DetailedCongressman extends Congressman {
  dateOfBirth: string;
  status: number;
}

interface Group {
  id: number,
  name: string,
}

interface Block extends Group {
  shortName: string;
}

interface District extends Group {
  key: string;
}

interface Party extends Group {
  shortName: string;
}

interface SessionSummary {
  id: number;
  type: number;
  sessionNumber: number;
  startDate: string;
  period: string;
  total: number;
  present: number;
  absent: number;
  license: number;
}

interface Attendance {
  status: number;
  sessionDate: string;
  sessionNumber: number;
  sessionType: number;
}

interface Vote {
  votingId: number;
  voteType: number;
  subject: string;
  sessionDate: string;
  totalInFavor: number;
  totalAgainst: number;
  withMajority: number;
}

interface Voting {
  id: number;
  subject: string;
  totalInFavor: number;
  totalAgainst: number;
  totalAbsent: number;
}

interface VotingDetail {
  id: number;
  subject: string;
  startDate: string;
  sessionNumber: number;
  sessionType: number;
  period: string;
  majority: number;
  votesInFavor: number;
  votesAgainst: number;
  votesAbsent: number;
  attendancePresent: number;
  attendanceAbsent: number;
  attendanceLicense: number;
}

interface VotingSummary {
  id: number;
  subject: string;
  startDate: string;
  sessionNumber: number;
  sessionType: number;
  period: string;
  votesInFavor: number;
  votesAgainst: number;
  votesAbsent: number;
  majority: number;
}

interface Stats {
  period: string;
  attendancePresent: number;
  attendanceAbsent: number;
  attendanceLicense: number;
  votesInFavor: number;
  votesAgainst: number;
  votesAbsent: number;
}

export interface CongressmanStats extends Stats {
  withMajority: number;
}

export interface OrgStats extends Stats {
  riceIndex: number;
}

interface MemberCount {
  membersCount: number;
}

interface Badge {
  badge: string;
}

const generateCountQuery = (table: string) =>
  () => db.prepare<NoParams, CountQuery>(`
    SELECT COUNT(*) as count
    FROM ${table}
  `).get()?.count ?? 0;

export const countBlocks = generateCountQuery('blocks');

export const countParties = generateCountQuery('parties');

export const countDistricts = generateCountQuery('districts');

export const countSessions = generateCountQuery('sessions');

export const countVoting = generateCountQuery('voting');

export const countActiveCongressmen = ()=>
  db.prepare<number, CountQuery>(`
    SELECT COUNT(*) as count
    FROM congressmen
    WHERE status = ?
  `).get(CONGRESSMAN_STATUS.ACTIVE)?.count ?? 0;

const generateGetAllIdsQuery = (table: string) =>
  () => db.prepare<NoParams, IdQuery>(`
    SELECT id
    FROM ${table}
  `).all();

export const getAllCongressmenId = generateGetAllIdsQuery('congressmen');

export const getAllBlocksId = generateGetAllIdsQuery('blocks');

export const getAllDistrictsId = generateGetAllIdsQuery('districts');

export const getAllPartiesId = generateGetAllIdsQuery('parties');

export const getAllSessionsId = generateGetAllIdsQuery('sessions');

export const getAllVotingId = generateGetAllIdsQuery('voting');

export function getLastSessionDate() {
  return db.prepare<NoParams, { date: string }>(`
    SELECT start_date AS date
    FROM sessions
    ORDER BY start_date DESC
    LIMIT 1
    `).get()?.date;
}

export function getAllCongressmen() {
  return db.prepare<NoParams, DetailedCongressman>(`
    SELECT 
      c.id,
      c.first_name AS firstName,
      c.last_name AS lastName,
      c.birth_date as dateOfBirth,
      c.status,
      b.id AS blockId,
      b.short_name AS blockName,
      d.id AS districtId,
      d.name AS districtName,
      p.id AS partyId,
      p.name AS partyName
    FROM congressmen c
    LEFT JOIN blocks b ON c.block_id = b.id 
    LEFT JOIN districts d ON c.district_id = d.id
    LEFT JOIN parties p ON c.party_id = p.id
    ORDER BY firstName, lastName
  `).all();
}

export function getCongressman(id: number) {
  return db.prepare<NoParams, DetailedCongressman>(`
    SELECT 
      c.id,
      c.first_name AS firstName,
      c.last_name AS lastName,
      c.birth_date as dateOfBirth,
      c.status,
      b.id AS blockId,
      b.short_name AS blockName,
      d.id AS districtId,
      d.name AS districtName,
      p.id AS partyId,
      p.name AS partyName
    FROM congressmen c
    LEFT JOIN blocks b ON c.block_id = b.id 
    LEFT JOIN districts d ON c.district_id = d.id
    LEFT JOIN parties p ON c.party_id = p.id
    WHERE c.id = ?
    ORDER BY firstName, lastName
  `).get(id);
}

export function getCongressmanStatsTotal(id: number) {
  return db.prepare<number, CongressmanStats>(`
    SELECT
      period,
      attendance_present AS attendancePresent,
      attendance_license AS attendanceLicense,
      attendance_absent AS attendanceAbsent,
      votes_in_favor AS votesInFavor,
      votes_against AS votesAgainst,
      votes_absent AS votesAbsent,
      votes_with_majority AS votesWithMajority
    FROM congressman_stats
    WHERE id = ? AND period = '${PERIOD.TOTAL}'
  `).get(id);
}

export function getCongressmanStatsByYear(id: number) {
  return db.prepare<number, CongressmanStats>(`
    SELECT
      period,
      attendance_present AS attendancePresent,
      attendance_license AS attendanceLicense,
      attendance_absent AS attendanceAbsent,
      votes_in_favor AS votesInFavor,
      votes_against AS votesAgainst,
      votes_absent AS votesAbsent,
      votes_with_majority AS votesWithMajority
    FROM congressman_stats
    WHERE id = ? AND period != '${PERIOD.TOTAL}'
    ORDER BY period
  `).all(id);
}

export function getAllBlocksWithMembersCount() {
  return db.prepare<NoParams, Block & MemberCount>(`
    SELECT
      b.id,
      b.short_name AS shortName,
      b.name,
      COUNT(*) AS membersCount
    FROM blocks b
    LEFT JOIN congressmen c ON b.id = c.block_id
    GROUP BY b.id, b.short_name
    ORDER BY b.short_name, membersCount DESC
  `).all();
}

export function getAllSimpleBlocks() {
  return db.prepare<NoParams, Group>(`
    SELECT
      id,
      short_name AS name
    FROM blocks
    ORDER BY name
  `).all();
}

export function getBlock(id: number) {
  return db.prepare<NoParams, Block>(`
    SELECT
      id,
      short_name AS shortName,
      name
    FROM blocks
    WHERE id = ?
  `).get(id);
}

export function getBlockMembers(id: number) {
  return db.prepare<NoParams, MinifiedCongressman & Badge>(`
    SELECT
      c.id,
      c.first_name AS firstName,
      c.last_name AS lastName,
      d.name as badge
    FROM congressmen c
    LEFT JOIN districts d ON c.district_id = d.id
    WHERE c.block_id = ? AND c.status = ${CONGRESSMAN_STATUS.ACTIVE}
    ORDER BY c.first_name, c.last_name
  `).all(id);
}

export function getBlockStatsTotal(id: number) {
  return db.prepare<number, OrgStats>(`
    SELECT
      attendance_present AS attendancePresent,
      attendance_absent AS attendanceAbsent,
      attendance_license AS attendanceLicense,
      votes_in_favor AS votesInFavor,
      votes_against AS votesAgainst,
      votes_absent AS votesAbsent,
      rice_index AS riceIndex
    FROM block_stats
    WHERE id = ? AND period = '${PERIOD.TOTAL}'
  `).get(id);
}

export function getBlockStatsByYear(id: number) {
  return db.prepare<number, OrgStats>(`
    SELECT
      period,
      attendance_present AS attendancePresent,
      attendance_absent AS attendanceAbsent,
      attendance_license AS attendanceLicense,
      votes_in_favor AS votesInFavor,
      votes_against AS votesAgainst,
      votes_absent AS votesAbsent,
      rice_index AS riceIndex
    FROM block_stats
    WHERE id = ? AND period != '${PERIOD.TOTAL}'
    ORDER BY period
  `).all(id);
}

export function getAllDistrictsWithMembersCount() {
  return db.prepare<NoParams, District & MemberCount>(`
    SELECT
      d.id,
      d.name,
      d.key,
      COUNT(*) AS membersCount
    FROM districts d
    LEFT JOIN congressmen c ON d.id = c.district_id
    GROUP BY d.id, d.name, d.key
    ORDER BY d.name, membersCount DESC
  `).all();
}

export function getAllSimpleDistricts() {
  return db.prepare<NoParams, Group>(`
    SELECT
      id,
      name
    FROM districts
    ORDER BY name
  `).all();
}

export function getDistrict(id: number) {
  return db.prepare<NoParams, District>(`
    SELECT
      id,
      name,
      key
    FROM districts
    WHERE id = ?
  `).get(id);
}

export function getDistrictMembers(id: number) {
  return db.prepare<NoParams, MinifiedCongressman & Badge>(`
    SELECT
      c.id,
      c.first_name AS firstName,
      c.last_name AS lastName,
      b.short_name as badge 
    FROM congressmen c
    LEFT JOIN blocks b ON c.block_id = b.id
    WHERE c.district_id = ? AND c.status = ${CONGRESSMAN_STATUS.ACTIVE}
    ORDER BY c.first_name, c.last_name
  `).all(id);
}

export function getDistrictStatsTotal(id: number) {
  return db.prepare<number, OrgStats>(`
    SELECT
      attendance_present AS attendancePresent,
      attendance_absent AS attendanceAbsent,
      attendance_license AS attendanceLicense,
      votes_in_favor AS votesInFavor,
      votes_against AS votesAgainst,
      votes_absent AS votesAbsent,
      rice_index AS riceIndex
    FROM district_stats
    WHERE id = ? AND period = '${PERIOD.TOTAL}'
  `).get(id);
}

export function getDistrictStatsByYear(id: number) {
  return db.prepare<number, OrgStats>(`
    SELECT
      period,
      attendance_present AS attendancePresent,
      attendance_absent AS attendanceAbsent,
      attendance_license AS attendanceLicense,
      votes_in_favor AS votesInFavor,
      votes_against AS votesAgainst,
      votes_absent AS votesAbsent,
      rice_index AS riceIndex
    FROM district_stats
    WHERE id = ? AND period != '${PERIOD.TOTAL}'
    ORDER BY period
  `).all(id);
}

export function getAllPartiesWithMembersCount() {
  return db
    .prepare<NoParams, Party & MemberCount>(`
      SELECT
        p.id,
        p.name,
        p.short_name AS shortName,
        COUNT(*) AS membersCount
      FROM parties p
      LEFT JOIN congressmen c ON p.id = c.party_id
      GROUP BY p.id, p.short_name
      ORDER BY p.short_name, membersCount DESC
    `).all();
}

export function getParty(id: number) {
  return db.prepare<number, Party>(`
    SELECT
      id,
      name,
      short_name AS shortName
    FROM parties
    WHERE id = ?
  `).get(id);
}

export function getPartyMembers(id: number) {
  return db.prepare<NoParams, MinifiedCongressman & Badge>(`
    SELECT
      c.id,
      c.first_name AS firstName,
      c.last_name AS lastName,
      d.name as badge
    FROM congressmen c
    LEFT JOIN districts d ON c.district_id = d.id
    WHERE c.party_id = ? AND c.status = ${CONGRESSMAN_STATUS.ACTIVE}
    ORDER BY c.first_name, c.last_name
  `).all(id);
}

export function getPartyStatsTotal(id: number) {
  return db.prepare<number, OrgStats>(`
    SELECT
      attendance_present AS attendancePresent,
      attendance_absent AS attendanceAbsent,
      attendance_license AS attendanceLicense,
      votes_in_favor AS votesInFavor,
      votes_against AS votesAgainst,
      votes_absent AS votesAbsent,
      rice_index AS riceIndex
    FROM party_stats
    WHERE id = ? AND period = '${PERIOD.TOTAL}'
  `).get(id);
}

export function getPartyStatsByYear(id: number) {
  return db.prepare<number, OrgStats>(`
    SELECT
      period,
      attendance_present AS attendancePresent,
      attendance_absent AS attendanceAbsent,
      attendance_license AS attendanceLicense,
      votes_in_favor AS votesInFavor,
      votes_against AS votesAgainst,
      votes_absent AS votesAbsent,
      rice_index AS riceIndex
    FROM party_stats
    WHERE id = ? AND period != '${PERIOD.TOTAL}'
    ORDER BY period
  `).all(id);
}

export function getAllSessionsSummary() {
  return db.prepare<[], SessionSummary>(`
    SELECT
      s.id,
      s.type,
      s.session_number AS sessionNumber,
      s.start_date AS startDate,
      s.period,
      COUNT(a.congressman_id) AS total,
      SUM(CASE WHEN a.status = ${ATTENDANCE_STATUS.PRESENT} THEN 1 ELSE 0 END) AS present,
      SUM(CASE WHEN a.status = ${ATTENDANCE_STATUS.ABSENT}  THEN 1 ELSE 0 END) AS absent,
      SUM(CASE WHEN a.status = ${ATTENDANCE_STATUS.LICENSE}  THEN 1 ELSE 0 END) AS license
    FROM sessions s
    LEFT JOIN attendance a ON s.id = a.session_id
    GROUP BY s.id
    ORDER BY s.start_date DESC
  `).all();
}

export function getSessionPeriods() {
  return db.prepare<NoParams, { period: string }>(`
    SELECT DISTINCT period
    FROM sessions
    WHERE period != '${PERIOD.TOTAL}'
    ORDER BY period DESC
  `).all().map(s => s.period);
}

export function getSessionSummary(id: number) {
  return db.prepare<number, SessionSummary>(`
    SELECT
      s.id,
      s.type,
      s.session_number AS sessionNumber,
      s.start_date AS startDate,
      s.period,
      COUNT(a.congressman_id) AS total,
      SUM(CASE WHEN a.status = ${ATTENDANCE_STATUS.PRESENT} THEN 1 ELSE 0 END) AS present,
      SUM(CASE WHEN a.status = ${ATTENDANCE_STATUS.ABSENT}  THEN 1 ELSE 0 END) AS absent,
      SUM(CASE WHEN a.status = ${ATTENDANCE_STATUS.LICENSE}  THEN 1 ELSE 0 END) AS license
    FROM sessions s
    LEFT JOIN attendance a ON s.id = a.session_id
    WHERE s.id = ?
    GROUP BY s.id
    ORDER BY s.start_date DESC
  `).get(id);
}

export function getVotingBySession(id: number) {
  return db.prepare<number, Voting>(`
    SELECT
      vot.id,
      vot.subject,
      SUM(CASE WHEN v.vote_type = ${VOTE_TYPE.IN_FAVOR} THEN 1 ELSE 0 END) AS totalInFavor,
      SUM(CASE WHEN v.vote_type = ${VOTE_TYPE.AGAINST}  THEN 1 ELSE 0 END) AS totalAgainst,
      SUM(CASE WHEN v.vote_type = ${VOTE_TYPE.ABSENT}   THEN 1 ELSE 0 END) AS totalAbsent
    FROM voting vot
    LEFT JOIN votes v ON v.voting_id = vot.id
    WHERE vot.session_id = ?
    GROUP BY vot.id, vot.subject
    ORDER BY vot.id
  `).all(id);
}

export function getAttendanceByCongressman(id: number) {
  return db.prepare<number, Attendance>(`
    SELECT
      a.status,
      s.start_date AS sessionDate,
      s.session_number AS sessionNumber,
      s.type AS sessionType
    FROM attendance a
    LEFT JOIN sessions s ON a.session_id = s.id
    WHERE a.congressman_id = ?
    ORDER BY s.start_date
  `).all(id);
}

export function getVotesByCongressman(id: number) {
  return db.prepare<number, Vote>(`
    SELECT
      v.vote_type AS voteType,
      vot.subject,
      s.start_date AS sessionDate,
      vot.id as votingId,
      vot.votes_in_favor as totalInFavor,
      vot.votes_against as totalAgainst,
      v.with_majority AS withMajority
    FROM votes v
    JOIN voting vot ON v.voting_id = vot.id
    JOIN sessions s ON vot.session_id = s.id
    WHERE v.congressman_id = ?
    ORDER BY votingId DESC
  `).all(id);
}

export function getCongressmenSessionAction(id: number) {
  return db.prepare<number, Congressman>(`
    SELECT
      a.status AS actionValue,
      c.id AS congressmanId,
      c.first_name AS firstName,
      c.last_name AS lastName,
      p.id as partyId,
      p.short_name AS partyName,
      d.id AS districtId,
      d.name AS districtName,
      c.block_id AS blockId,
      COALESCE(b.short_name, 'Independientes') AS blockName
    FROM attendance a
    JOIN congressmen c ON c.id = a.congressman_id
    LEFT JOIN parties p ON c.party_id = p.id
    LEFT JOIN districts d ON c.district_id = d.id
    LEFT JOIN blocks b ON b.id = c.block_id
    WHERE a.session_id = ?
    ORDER BY c.first_name
  `).all(id);
}

export const getVotingById = (id: number) =>
  db.prepare<number, VotingDetail>(`
    SELECT 
      v.id,
      v.subject,
      s.start_date AS startDate,
      s.session_number AS sessionNumber,
      s.type as session_type,
      s.period,
      v.majority,
      v.votes_in_favor AS votesInFavor,
      v.votes_against AS votesAgainst,
      v.votes_absent AS votesAbsent,
      v.attendance_present AS attendancePresent,
      v.attendance_absent AS attendanceAbsent,
      v.attendance_license AS attendanceLicense
    FROM voting v
    JOIN sessions s ON v.session_id = s.id
    WHERE v.id = ?
  `).get(id);

export const getCongressmenVotingAction = (id: number) =>
  db.prepare<number, Congressman>(`
    SELECT 
      v.vote_type AS actionValue, 
      c.id AS congressmanId,
      c.first_name AS firstName,
      c.last_name AS lastName,
      p.id AS partyId,
      p.short_name AS partyName,
      d.id AS districtId,
      d.name AS districtName,
      c.block_id AS blockId,
      COALESCE(b.short_name, 'Independientes') AS blockName
    FROM votes v
    JOIN congressmen c ON v.congressman_id = c.id
    LEFT JOIN parties p ON c.party_id = p.id
    LEFT JOIN districts d ON c.district_id = d.id
    LEFT JOIN blocks b ON c.block_id = b.id
    WHERE v.voting_id = ?
    ORDER BY b.short_name, p.name, c.first_name
  `).all(id);

export const getVotingSummaries = () =>
  db.prepare<[], VotingSummary>(`
    SELECT
      v.id,
      v.subject,
      s.start_date AS startDate,
      s.session_number AS sessionNumber,
      s.type AS session_type,
      s.period,
      v.votes_in_favor AS votesInFavor,
      v.votes_against AS votesAgainst,
      v.votes_absent AS votesAbsent,
      v.majority
    FROM voting v
    JOIN sessions s ON v.session_id = s.id
    ORDER BY s.start_date DESC, v.id DESC
  `).all();