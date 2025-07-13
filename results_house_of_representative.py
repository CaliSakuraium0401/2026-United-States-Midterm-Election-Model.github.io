# Import the needed libraries.
import pandas as pd
import numpy as np

# Read the data from the github into a dataframe.
house_election_data = pd.read_csv('https://raw.githubusercontent.com/fivethirtyeight/election-results/refs/heads/main/election_results_house.csv')

# Create a state abbreviaion map (this will become important later for merging the dataframe with geojson ddata)
state_abbreviaion_map = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
    'District of Columbia': 'DC'
}

# The year that the file will start retrieving from.
# 1998 is the minimum year that fivethirtyeight has data for.
min_year = 1998
max_year = 2026
year = min_year

while year != 2026:
    # Filter the house election data to the specified year.
    house_election_year = house_election_data[house_election_data['cycle'] == year]
    # Filter the data of the specified election year to only include Democrats and Republicans.
    house_election_year = house_election_year[(house_election_year['ballot_party'] == "DEM") | (house_election_year['ballot_party'] == "REP")]
    # Create a pivot table so that the Democrats and Republicans are in the same row,
    # so that it is easier to compare them.
    house_election_year = house_election_year.pivot_table(
        index=['state', 'office_seat_name'],
        columns='ballot_party',
        values=['candidate_name', 'votes', 'percent'],
        aggfunc='first'
    )
    # Flattens the headers so that they all share one row.
    house_election_year.columns = ['_'.join(col).strip() for col in house_election_year.columns.values]
    house_election_year = house_election_year.reset_index()
    # Rename the columns for user friendlyness.
    house_election_year.rename(
        columns={
            'office_seat_name': 'district_number',
            'candidate_name_DEM': 'dem_candidate',
            'candidate_name_REP': 'rep_candidate',
            'percent_DEM': 'dem_per',
            'percent_REP': 'rep_per',
            'votes_DEM': 'dem_votes',
            'votes_REP': 'rep_votes',
        }, 
        inplace=True)
    # Fill empty columns.
    house_election_year['dem_candidate'] = house_election_year['dem_candidate'].fillna("None")
    house_election_year['rep_candidate'] = house_election_year['rep_candidate'].fillna("None")
    house_election_year['dem_per'] = house_election_year['dem_per'].fillna(0)
    house_election_year['rep_per'] = house_election_year['rep_per'].fillna(0)
    house_election_year['dem_votes'] = house_election_year['dem_votes'].fillna(0)
    house_election_year['rep_votes'] = house_election_year['rep_votes'].fillna(0)
    # Create a state abbreivation column based off the 'state' column and a map.
    house_election_year['state_code'] = (house_election_year['state'].map(state_abbreviaion_map))
    # Removes 'District' from the cells in 'district_number'.
    house_election_year['district_number'] = (house_election_year['district_number'].str.replace('District ', '', regex=False).str.strip())
    # For district_number 1 - 9, 0 will be added in front.
    house_election_year['district_number'] = (house_election_year['district_number'].astype(int).astype(str).str.zfill(2))
    # Create a new 'district_code' by combining state_code and district_number.
    house_election_year['district_code'] = house_election_year['state_code'].astype(str) + house_election_year['district_number'].astype(str)
    # Create array that will be the new order of the data frame.
    order = ['state_code', 'state', 'district_number', 'district_code', 'dem_candidate', 'rep_candidate', 'dem_votes', 'rep_votes', 'dem_per', 'rep_per']
    house_election_year = house_election_year[order]
    # Creates 'winner' column basd off whoever has more votes.
    house_election_year['winner'] = np.where(
        house_election_year['dem_votes'] > house_election_year['rep_votes'],
        'Democrat',
        'Republican'
    )
    # Drops the rows of non-voting member districts (Guam and Virgin Islands).
    house_election_year = house_election_year.dropna(subset=['state_code'])
    # Export to csv
    house_election_year.to_csv(f'election_data/house_of_representatives/house_election_{year}.csv', index=False)
    print(f'Completed: house_election_{year}.csv' )
    year += 2
    
