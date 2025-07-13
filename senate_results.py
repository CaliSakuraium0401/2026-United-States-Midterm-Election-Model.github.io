import pandas as pd
import numpy as np
print("✓ | #0 Import Libraries")

# Read the data from the github into a dataframe.
senate_election_data = pd.read_csv('https://raw.githubusercontent.com/fivethirtyeight/election-results/refs/heads/main/election_results_senate.csv')
print("✓ | #1 Read Data")

party_map = {
    "DEM": "Democratic",
    "REP": "Republican",
    "LIB": "Libertarian",
    "W": "Write-In",
    "IND": "Independent",
    "OTH": "Other",
    "GRE": "Green",
    "SWP": "Socialist Workers",
    "CON": "Constitution",
    "NLP": "Natural Law",
    "NPA": "No Party Affiliation",
    "REF": "Reform",
    "AMP": "American Party",
    "CRV": "Civic Reform",
    "UN": "Unity",
    "IAP": "Independent American",
    "WFP": "Working Families",
    "IDP": "Independence",
    "UST": "U.S. Taxpayers",
    "AIP": "American Independent",
    "LBU": "Liberty Union",
    "PAF": "Peace and Freedom",
    "GRT": "Grassroots",
    "COM": "Communist",
    "NAP": "New Alliance",
    "LBL": "Liberty Bell",
    "RTL": "Right to Life",
    "PG": "Progressive",
    "CIT": "Citizen's",
    "SUS": "Sustaining",
    "SLP": "Socialist Labor",
    "CNC": "Concerned Citizens",
    "LBR": "Labor",
    "IDE": "Independent Democrat",
    "AKI": "Alaskan Independence",
    "UTY": "Unity",
    "N": "Nonpartisan",
    "LAB": "Labor",
    "ACP": "American Constitution",
    "LMN": "Lemon",
    "PRO": "Prohibition",
    "MTP": "Mountain",
    "AVP": "American Veterans",
    "IGR": "Independent Green",
    "NNE": "None",
    "SEP": "Socialist Equality",
    "SOC": "Socialist",
    "PCH": "Peace",
    "DRP": "Democratic-Republican",
    "CPC": "Conservative",
    "LRU": "La Raza Unida",
    "CFP": "Constitutional Freedom",
    "DGR": "Democratic Green",
    "FTP": "Freedom",
    "HRP": "Human Rights",
    "MJP": "Majority Party",
    "MRP": "Moderate Republican",
    "LMP": "Liberty Movement",
    "COU": "Country",
    "GMP": "Green Mountain",
    "GLC": "Green Liberty",
    "NEB": "Nebraska",
    "NOP": "No Party",
    "RES": "Rescue",
    "NDP": "National Democratic",
    "NON": "Nonpartisan",
    "TEA": "Tea Party",
    "TLP": "Taxpayers",
    "UC": "United Citizens",
    "VET": "Veterans",
    "WTP": "We The People"
}
print("✓ | #2 Create Party Map")

senate_election_data['party_name'] = senate_election_data['ballot_party'].replace(party_map)
print("✓ | #3 Apply Party Map")

min_year = 1998
max_year = 2026
year = min_year
step = 4

while year != 2026:
    senate_election_year = senate_election_data[senate_election_data['cycle'] == year]
    
    senate_election_year = senate_election_year.drop(
            [
                'id',
                'race_id',
                'office_id',
                'office_name',
                'cycle',
                'stage',
                'party',
                'candidate_id',
                'politician_id',
                'unopposed',
                'alt_result_text',
                'source'
            ],
            axis=1
        )

    senate_election_year.rename(
        columns={
            'state_abbrev': 'state_code',
            'state': 'state',
            'office_seat_name': 'seat_class',
            'ballot_party': 'party_code'
        },
        inplace=True
    )

    senate_election_year['candidate_name'] = senate_election_year['candidate_name'].fillna("None")
    senate_election_year['party_code'] = senate_election_year['party_code'].fillna("W")
    senate_election_year['party_name'] = senate_election_year['party_name'].fillna("Write-In")
    senate_election_year['votes'] = senate_election_year['votes'].fillna(0)
    senate_election_year['percent'] = senate_election_year['percent'].fillna(0)
    senate_election_year['ranked_choice_round'] = senate_election_year['ranked_choice_round'].fillna('None')
    senate_election_year['winner'] = senate_election_year['winner'].fillna('False')
    
    senate_election_year = senate_election_year.groupby(['state_code', 'state', 'seat_class', 'special', 'candidate_name',
       'party_code', 'party_name', 'ranked_choice_round', 'winner'], as_index=False).sum()
    
    order = ['state_code', 'state', 'seat_class', 'special', 'candidate_name',
       'party_code', 'party_name', 'ranked_choice_round', 'votes', 'percent', 'winner']
    
    senate_election_year = senate_election_year[order]
        
    senate_election_year = senate_election_year.sort_values(
        by=['state_code', 'percent'],
        ascending=[True, False]
    )

    filename = f'senate_election_{year}'
    
    if len(senate_election_year) >= 1:
        senate_election_year.to_csv(f'election_data/senate/{filename}.csv', index=False)
        print(f"✓ | #{step} Completed {filename}")
    
    year += 1
    step += 1