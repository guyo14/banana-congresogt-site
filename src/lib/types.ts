// ============================================================================
// SQL utility types
// ============================================================================

export interface CountQuery {
  count: number;
}

export interface IdQuery {
  id: number;
}

export interface NoParams extends Array<unknown> {}

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