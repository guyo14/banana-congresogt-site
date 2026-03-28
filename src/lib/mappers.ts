export const CONGRESSMAN_STATUS = {
  ACTIVE: 0,
  INACTIVE: 1
};
export const SESSION_TYPE = {
  ORDINARY: 0,
  EXTRAORDINARY: 1,
  SOLEMN: 2
};
export const ATTENDANCE_STATUS = {
  PRESENT: 0,
  ABSENT: 1,
  LICENSE: 2
};
export const VOTE_TYPE = {
  IN_FAVOR: 0,
  AGAINST: 1,
  ABSENT: 2
};
export const MAJORITY = {
  IN_FAVOR: 0,
  AGAINST: 1,
  TIE: 2
};
export const WITH_MAJORITY = {
  YES: 0,
  NO: 1,
  NA: 2
};
export const PERIOD = {
  TOTAL: "total",
  2024: "2024",
  2025: "2025",
  2026: "2026",
  2027: "2027"
};

export const CONGRESSMAN_STATUS_STRING = {
  ACTIVE: 'Activo',
  INACTIVE: 'Inactivo'
};
export const SESSION_TYPE_STRING = {
  ORDINARY: 'Ordinaria',
  EXTRAORDINARY: 'Extraordinaria',
  SOLEMN: 'Solemne'
};
export const ATTENDANCE_STATUS_STRING = {
  PRESENT: 'Presente',
  ABSENT: 'Ausente',
  LICENSE: 'Licencia'
};
export const VOTE_TYPE_STRING = {
  IN_FAVOR: 'A Favor',
  AGAINST: 'En Contra',
  ABSENT: 'Ausente'
};

export function getVoteString(type: number) {
  if (type === VOTE_TYPE.IN_FAVOR) return VOTE_TYPE_STRING.IN_FAVOR;
  if (type === VOTE_TYPE.AGAINST) return VOTE_TYPE_STRING.AGAINST;
  return VOTE_TYPE_STRING.ABSENT;
}

export function getSessionTypeString(type: number) {
  if (type === SESSION_TYPE.SOLEMN) return SESSION_TYPE_STRING.SOLEMN;
  if (type === SESSION_TYPE.EXTRAORDINARY) return SESSION_TYPE_STRING.EXTRAORDINARY;
  return SESSION_TYPE_STRING.ORDINARY;
}

export function getCongressmanStatusString(status: number) {
  if (status === CONGRESSMAN_STATUS.ACTIVE) return CONGRESSMAN_STATUS_STRING.ACTIVE;
  return CONGRESSMAN_STATUS_STRING.INACTIVE;
}