import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv
from enum import IntEnum
from .logger import Log

class CongressmanStatus(IntEnum):
    active = 0
    inactive = 1

class VoteType(IntEnum):
    in_favor = 0
    against = 1
    absent = 2

class AttendanceStatus(IntEnum):
    present = 0
    absent = 1
    license = 2

class VoteMajority(IntEnum):
    in_favor = 0
    against = 1
    tie = 2

class WithMajority(IntEnum):
    yes = 0
    no = 1
    na = 2

class SessionType(IntEnum):
    ordinary = 0
    extraordinary = 1
    solemn = 2

load_dotenv()

def get_engine():
    return create_engine(
        f"postgresql+psycopg2://"
        f"{os.getenv('DB_USER', 'postgres')}:"
        f"{os.getenv('DB_PASSWORD', 'postgres')}@"
        f"{os.getenv('DB_HOST', 'localhost')}:"
        f"{os.getenv('DB_PORT', '5432')}/"
        f"{os.getenv('DB_NAME', 'postgres')}"
    )

def run_transform():
    """
    Transform raw database data and generate statistical analyses.

    This function:
    - Fetches data from the database
    - Calculates voting aggregations and majority alignments
    - Generates congressman statistics
    - Computes group statistics with Rice Index
    - Calculates congressman similarity scores
    - Exports all results to CSV files in the data/ directory
    """
    Log.info("Connecting to DB and fetching tables...")
    engine = get_engine()
    c_df = pd.read_sql("SELECT * FROM congressmen", engine)
    d_df = pd.read_sql("SELECT * FROM districts", engine)
    b_df = pd.read_sql("SELECT * FROM blocks", engine)
    p_df = pd.read_sql("SELECT * FROM parties", engine)
    a_df = pd.read_sql("SELECT * FROM attendance", engine)
    s_df = pd.read_sql("SELECT * FROM sessions", engine)
    vot_df = pd.read_sql("SELECT * FROM voting", engine)
    v_df = pd.read_sql("SELECT * FROM votes", engine)
    engine.dispose()

    # Data prep
    c_df['status'] = c_df['status'].map({
        'active': CongressmanStatus.active.value,
        'inactive': CongressmanStatus.inactive.value,
    }).astype(int)
    c_df.drop(columns=["key"], inplace=True)
    a_df['status'] = a_df['status'].map({
        'present': AttendanceStatus.present.value,
        'absent': AttendanceStatus.absent.value,
        'license': AttendanceStatus.license.value,
    }).astype(int)
    v_df['vote_type'] = v_df['vote_type'].map({
        'in_favor': VoteType.in_favor,
        'against': VoteType.against,
        'absent': VoteType.absent,
    }).astype(int)
    v_df['attendance_status'] = v_df['attendance_status'].map({
        'present': AttendanceStatus.present,
        'absent': AttendanceStatus.absent,
        'license': AttendanceStatus.license,
    }).astype(int)
    s_df['type'] = s_df['type'].map({
        'ordinary': SessionType.ordinary.value,
        'extraordinary': SessionType.extraordinary.value,
        'solemn': SessionType.solemn.value,
    })
    vot_df.drop(columns=["start_date"], inplace=True)

    s_df['start_date'] = pd.to_datetime(s_df['start_date'])
    s_df['period'] = s_df['start_date'].dt.year.astype(str)

    # Replace null block_id with -1
    c_df['block_id'] = c_df['block_id'].fillna(-1).astype(int)
    p_df['block_id'] = p_df['block_id'].fillna(-1).astype(int)

    # Write blocks, districts, parties, congressmen and attendance to CSV
    b_df.to_csv('data/blocks.csv', index=False)
    d_df.to_csv('data/districts.csv', index=False)
    p_df.to_csv('data/parties.csv', index=False)
    c_df.to_csv('data/congressmen.csv', index=False)
    a_df.to_csv('data/attendance.csv', index=False)
    s_df.to_csv('data/sessions.csv', index=False)

    # Merge attendance with sessions to get the period
    a_df = a_df.merge(
        s_df[['id', 'period']].rename(columns={'id': 'session_id'}),
        on='session_id',
        how='left'
    )

    # Merge votes with voting and session to get the period
    v_df = v_df.merge(
        vot_df[['id', 'session_id']].rename(columns={'id': 'voting_id'}),
        on='voting_id',
        how='left'
    )
    v_df = v_df.merge(
        s_df[['id', 'period']].rename(columns={'id': 'session_id'}),
        on='session_id',
        how='left'
    )

    Log.info("Calculating Voting Aggregations...")
    # Voting Stats
    if v_df.empty:
        vot_stats = pd.DataFrame(columns=['voting_id', 'votes_in_favor', 'votes_against', 'votes_absent', 'attendance_present', 'attendance_absent', 'attendance_license'])
    else:
        vot_stats = v_df.groupby('voting_id').apply(
            lambda x: pd.Series({
                'votes_in_favor': (x['vote_type'] == VoteType.in_favor.value).sum(),
                'votes_against': (x['vote_type'] == VoteType.against.value).sum(),
                'votes_absent': (x['vote_type'] == VoteType.absent.value).sum(),
                'attendance_present': (x['attendance_status'] == AttendanceStatus.present.value).sum(),
                'attendance_absent': (x['attendance_status'] == AttendanceStatus.absent.value).sum(),
                'attendance_license': (x['attendance_status'] == AttendanceStatus.license.value).sum(),
            })
        ).reset_index()
        vot_stats['majority'] = np.where(
            vot_stats['votes_in_favor'] > vot_stats['votes_against'],
            VoteMajority.in_favor.value,
            np.where(vot_stats['votes_against'] > vot_stats['votes_in_favor'], VoteMajority.against.value, VoteMajority.tie.value)
        )
    v_df = v_df.merge(vot_stats[['voting_id', 'majority']], on='voting_id', how='left')
    vot_stats.rename(columns={'voting_id': 'id'}, inplace=True)
    vot_df = vot_df.merge(vot_stats, on='id', how='left')
    vot_df.to_csv('data/voting.csv', index=False)
    
    # Add with_majority when the vote is aligned to the majority
    v_df['with_majority'] = pd.Series(
        np.where(
            (v_df['vote_type'] == VoteType.absent.value),
            WithMajority.na.value,
            np.where(
                (
                    (v_df['vote_type'] == VoteType.in_favor.value) &
                    (v_df['majority'] == VoteMajority.in_favor.value)
                ) |
                (
                    (v_df['vote_type'] == VoteType.against.value) &
                    (v_df['majority'] == VoteMajority.against.value)
                ),
                WithMajority.yes.value,
                WithMajority.no.value
            )
        ),
        index=v_df.index,
        dtype=int
    )
    v_df.drop(columns=['majority'], inplace=True)
    v_df.to_csv('data/votes.csv', index=False)


    Log.info("Calculating Congressman Stats...")
    # Attendance aggregates
    if not a_df.empty:
        a_grp = a_df.groupby(['congressman_id', 'period']).apply(lambda x: pd.Series({
            'attendance_present': (x['status'] == AttendanceStatus.present.value).sum(),
            'attendance_absent': (x['status'] == AttendanceStatus.absent.value).sum(),
            'attendance_license': (x['status'] == AttendanceStatus.license.value).sum()
        })).reset_index()
        a_tot = a_df.groupby('congressman_id').apply(lambda x: pd.Series({
            'attendance_present': (x['status'] == AttendanceStatus.present.value).sum(),
            'attendance_absent': (x['status'] == AttendanceStatus.absent.value).sum(),
            'attendance_license': (x['status'] == AttendanceStatus.license.value).sum()
        })).reset_index()
        a_tot['period'] = 'total'
        a_all = pd.concat([a_grp, a_tot])
    else:
        a_all = pd.DataFrame(columns=['congressman_id', 'period', 'attendance_present', 'attendance_absent', 'attendance_license'])

    # Votes aggregates
    if not v_df.empty:
        v_grp = v_df.groupby(['congressman_id', 'period']).apply(lambda x: pd.Series({
            'votes_in_favor': (x['vote_type'] == VoteType.in_favor.value).sum(),
            'votes_against': (x['vote_type'] == VoteType.against.value).sum(),
            'votes_absent': (x['vote_type'] == VoteType.absent.value).sum(),
            'votes_with_majority': (x['with_majority'] == WithMajority.yes.value).sum(),
            'votes_against_majority': (x['with_majority'] == WithMajority.no.value).sum(),
        })).reset_index()
        v_tot = v_df.groupby('congressman_id').apply(lambda x: pd.Series({
            'votes_in_favor': (x['vote_type'] == VoteType.in_favor.value).sum(),
            'votes_against': (x['vote_type'] == VoteType.against.value).sum(),
            'votes_absent': (x['vote_type'] == VoteType.absent.value).sum(),
            'votes_with_majority': (x['with_majority'] == WithMajority.yes.value).sum(),
            'votes_against_majority': (x['with_majority'] == WithMajority.no.value).sum(),
        })).reset_index()
        v_tot['period'] = 'total'
        v_all = pd.concat([v_grp, v_tot])
    else:
        v_all = pd.DataFrame(columns=['congressman_id', 'period', 'votes_in_favor', 'votes_against', 'votes_absent', 'votes_with_majority', 'votes_against_majority'])

    c_stats = pd.merge(a_all, v_all, on=['congressman_id', 'period'], how='outer').fillna(0)
    c_stats.rename(columns={'congressman_id': 'id'}, inplace=True)
    c_stats.to_csv('data/congressman_stats.csv', index=False)

    Log.info("Calculating Group Stats (Rice Index)...")
    def calc_group_stats(group_col, out_file):
        # merge congressman group info
        if a_df.empty:
            ga_df = pd.DataFrame(columns=['congressman_id', 'period', 'status', group_col])
        else:
            ga_df = a_df.merge(c_df[['id', group_col]], left_on='congressman_id', right_on='id')

        if v_df.empty:
            gv_df = pd.DataFrame(columns=['congressman_id', 'period', 'voting_id', 'vote_type', group_col])
        else:
            gv_df = v_df.merge(c_df[['id', group_col]], left_on='congressman_id', right_on='id')

        # Attendance
        if not ga_df.empty:
            ga_grp = ga_df.groupby([group_col, 'period']).apply(lambda x: pd.Series({
                'attendance_present': (x['status'] == AttendanceStatus.present.value).sum(),
                'attendance_absent': (x['status'] == AttendanceStatus.absent.value).sum(),
                'attendance_license': (x['status'] == AttendanceStatus.license.value).sum()
            })).reset_index()
            ga_tot = ga_df.groupby(group_col).apply(lambda x: pd.Series({
                'attendance_present': (x['status'] == AttendanceStatus.present.value).sum(),
                'attendance_absent': (x['status'] == AttendanceStatus.absent.value).sum(),
                'attendance_license': (x['status'] == AttendanceStatus.license.value).sum()
            })).reset_index()
            ga_tot['period'] = 'total'
            ga_all = pd.concat([ga_grp, ga_tot])
        else:
            ga_all = pd.DataFrame(columns=[group_col, 'period', 'attendance_present', 'attendance_absent', 'attendance_license'])

        # Votes & Rice index
        if not gv_df.empty:
            v_group_stats = gv_df.groupby([group_col, 'period', 'voting_id']).apply(lambda x: pd.Series({
                'in_favor': (x['vote_type'] == VoteType.in_favor.value).sum(),
                'against': (x['vote_type'] == VoteType.against.value).sum(),
                'absent': (x['vote_type'] == VoteType.absent.value).sum()
            })).reset_index()
            v_group_stats['rice'] = abs(v_group_stats['in_favor'] - v_group_stats['against']) / (v_group_stats['in_favor'] + v_group_stats['against']).replace(0, np.nan)

            gv_period = v_group_stats.groupby([group_col, 'period']).apply(lambda x: pd.Series({
                'votes_in_favor': x['in_favor'].sum(),
                'votes_against': x['against'].sum(),
                'votes_absent': x['absent'].sum(),
                'rice_index': x['rice'].mean()
            })).reset_index()

            gv_tot = v_group_stats.groupby(group_col).apply(lambda x: pd.Series({
                'votes_in_favor': x['in_favor'].sum(),
                'votes_against': x['against'].sum(),
                'votes_absent': x['absent'].sum(),
                'rice_index': x['rice'].mean()
            })).reset_index()
            gv_tot['period'] = 'total'
            gv_all = pd.concat([gv_period, gv_tot])
        else:
            gv_all = pd.DataFrame(columns=[group_col, 'period', 'votes_in_favor', 'votes_against', 'votes_absent', 'rice_index'])

        res = pd.merge(ga_all, gv_all, on=[group_col, 'period'], how='outer').fillna({'rice_index': 0})
        res.rename(columns={group_col: 'id'}, inplace=True)
        # Drop nans in sum cols
        sum_cols = ['attendance_present','attendance_absent','attendance_license','votes_in_favor','votes_against','votes_absent']
        for c in sum_cols:
            res[c] = res[c].fillna(0).astype(int)

        res.to_csv(f'data/{out_file}', index=False)

    calc_group_stats('party_id', 'party_stats.csv')
    calc_group_stats('district_id', 'district_stats.csv')
    calc_group_stats('block_id', 'block_stats.csv')

    Log.info("Calculating Congressman Similarity...")
    if not v_df.empty:
        # Only consider votes where the congressman was present (not absent)
        present_votes = v_df[v_df['vote_type'] != VoteType.absent.value][['congressman_id', 'voting_id', 'vote_type']].copy()
        val_map = {VoteType.in_favor.value: 1, VoteType.against.value: -1}
        present_votes['vote_val'] = present_votes['vote_type'].map(val_map)

        # Pivot: NaN means the congressman was absent for that voting
        pivot = present_votes.pivot_table(index='congressman_id', columns='voting_id', values='vote_val')
        congressman_ids = pivot.index.tolist()
        pivot_values = pivot.values

        rows = []
        for i in range(len(congressman_ids)):
            for j in range(i + 1, len(congressman_ids)):
                a = pivot_values[i]
                b = pivot_values[j]
                # Mask: both congressmen voted (neither is NaN)
                both_present = ~np.isnan(a) & ~np.isnan(b)
                common_votes = int(both_present.sum())

                if common_votes < 2:
                    continue

                a_common = a[both_present]
                b_common = b[both_present]

                same_votes = int((a_common == b_common).sum())
                agreement_percentage = round(same_votes / common_votes, 4)

                # Pearson correlation on the common votes only
                std_a = np.std(a_common)
                std_b = np.std(b_common)
                if std_a == 0 or std_b == 0:
                    # Both voted the same way every time they coincided
                    similarity_score = 1.0 if np.array_equal(a_common, b_common) else -1.0
                else:
                    similarity_score = round(float(np.corrcoef(a_common, b_common)[0, 1]), 6)

                c1 = congressman_ids[i]
                c2 = congressman_ids[j]
                rows.append((c1, c2, similarity_score, common_votes, same_votes, agreement_percentage))
                rows.append((c2, c1, similarity_score, common_votes, same_votes, agreement_percentage))

        sim_df = pd.DataFrame(rows, columns=[
            'congressman_id', 'congressman_2_id', 'similarity_score',
            'common_votes', 'same_votes', 'agreement_percentage'
        ])
        sim_df.to_csv('data/congressman_similarity.csv', index=False)
    else:
        pd.DataFrame(columns=['congressman_id', 'congressman_2_id', 'similarity_score', 'common_votes', 'same_votes', 'agreement_percentage']).to_csv('data/congressman_similarity.csv', index=False)

    print("All transformations complete.")
