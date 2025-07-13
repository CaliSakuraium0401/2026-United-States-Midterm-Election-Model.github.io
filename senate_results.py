import pandas as pd
import numpy as np

# Read the data from the github into a dataframe.
senate_election_data = pd.read_csv('https://raw.githubusercontent.com/fivethirtyeight/election-results/refs/heads/main/election_results_senate.csv')

min_year = 2024
max_year = 2026
year = min_year

while year != 2026:
    senate_election_year = senate_election_data[senate_election_data['cycle'] == year]
    senate_election_year = senate_election_year[(senate_election_year['ballot_party'] == "DEM") | (senate_election_year['ballot_party'] == "REP")]
    senate_election_year = senate_election_year.pivot_table(
            index=['state_abbrev', 'state', 'office_seat_name', 'special'],
            columns='ballot_party',
            values=['candidate_name', 'votes', 'percent'],
            aggfunc='first'
        )

    senate_election_year.columns = ['_'.join(col).strip() for col in senate_election_year.columns.values]
    senate_election_year = senate_election_year.reset_index()

    # Rename the columns for user friendlyness.
    senate_election_year.rename(
        columns={
            'state_abbrev': 'state_code',
            'state': 'state',
            'seat_class': 'Office Seat Name',
            'special': 'special',
            'candidate_name_DEM': 'dem_candidate',
            'candidate_name_REP': 'rep_candidate',
            'percent_DEM': 'dem_per',
            'percent_REP': 'rep_per',
            'votes_DEM': 'dem_votes',
            'votes_REP': 'rep_votes'
        },
        inplace=True
    )

    senate_election_year['dem_candidate'] = senate_election_year['dem_candidate'].fillna("None")
    senate_election_year['rep_candidate'] = senate_election_year['rep_candidate'].fillna("None")
    senate_election_year['dem_per'] = senate_election_year['dem_per'].fillna(0)
    senate_election_year['rep_per'] = senate_election_year['rep_per'].fillna(0)
    senate_election_year['dem_votes'] = senate_election_year['dem_votes'].fillna(0)
    senate_election_year['rep_votes'] = senate_election_year['rep_votes'].fillna(0)

    # Create array that will be the new order of the data frame.
    order = [
        'state_code',
        'state',
        'office_seat_name',
        'special',
        'dem_candidate',
        'rep_candidate',
        'dem_votes',
        'rep_votes',
        'dem_per',
        'rep_per'
    ]
    senate_election_year = senate_election_year[order]
    # Creates 'winner' column basd off whoever has more votes.
    senate_election_year['winner'] = np.where(
        senate_election_year['dem_votes'] > senate_election_year['rep_votes'],
        'Democrat',
        'Republican'
    )

    senate_election_year.to_csv(f'election_data/senate/senate_election_{year}.csv', index=False)
    print(f'Completed: senate_election_{year}.csv' )
    year += 2