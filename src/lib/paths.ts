export const CONGRESSMEN_PATH = "/diputados";
export const DISTRICTS_PATH = "/distritos";
export const BLOCKS_PATH = "/bancadas";
export const PARTIES_PATH = "/partidos";
export const SESSIONS_PATH = "/sesiones";
export const VOTING_PATH = "/votaciones";
export const RANKINGS_PATH = "/rankings";

export function getCongressmanPath(id: number) {
  return `/diputados/${id}`;
}

export function getCongressmanPhotoPath(id: number) {
  return `/diputados/${id}.jpg`;
}

export function getDistrictPath(id: number) {
  return `/distritos/${id}`;
}

export function getBlockPath(id: number) {
  return `/bancadas/${id}`;
}

export function getBlockImagePath(id: number) {
  return `/bancadas/${id}.svg`;
}

export function getPartyPath(id: number) {
  return `/partidos/${id}`;
}

export function getPartyImagePath(id: number) {
  return `/partidos/${id}.svg`;
}

export function getSessionPath(id: number) {
  return `/sesiones/${id}`;
}

export function getVotingPath(id: number) {
  return `/votaciones/${id}`;
}