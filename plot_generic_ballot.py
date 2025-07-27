# Import the needed libraries.
import pandas as pd
import numpy as np
import altair as alt
import requests 

# Read the API into a pandas dataframe.
response = requests.get("https://api.votehub.com/polls")
polls_json = response.json()
polls_df = pd.DataFrame(polls_json)

# Filter the polls_df so that it is about Donald Trump's approval rating.
generic_ballot = polls_df[polls_df['poll_type'] == 'generic-ballot']
generic_ballot = polls_df[polls_df['subject'] == '2026']

# Wrangle the data regarding the Generic Ballot for visualization.
# This includes flattening the answers, normalizing the structure, converting percentages,
# filtering for relevant dates, and calculating a rolling average for each response choice.
generic_ballot = generic_ballot.explode('answers').reset_index(drop=True)
generic_ballot_answers = pd.json_normalize(generic_ballot['answers'])
generic_ballot = pd.concat([generic_ballot.drop(columns=['answers']), generic_ballot_answers], axis=1)
generic_ballot.loc[generic_ballot['pct'].abs() < 1, 'pct'] *= 100
generic_ballot['end_date'] = pd.to_datetime(generic_ballot['end_date'])
generic_ballot = generic_ballot[generic_ballot['end_date'] >= '2025-01-01']
generic_ballot_avg = generic_ballot.groupby(['end_date', 'choice'], as_index=False)['pct'].mean()
generic_ballot_avg['pct'] = generic_ballot_avg.groupby('choice')['pct'].transform(lambda x: x.rolling(window=14, min_periods=1).mean())
generic_ballot_avg['pct'] = generic_ballot_avg['pct'].round(2)

# Prepare the interactive chart.
nearest = alt.selection_point(name="nearest", fields=['end_date'], nearest=True, on='mouseover', empty='none')

line = alt.Chart(generic_ballot_avg).mark_line().encode(
    x=alt.X('end_date:T',
        title='Date',
        axis=alt.Axis(
            format='%b %Y',
            tickCount='month',
            labelAngle=-45
            ),
        scale=alt.Scale(domain=['2025-01-01', '2025-12-31'])),
    y=alt.Y('pct:Q', title='Percentage', scale=alt.Scale(domain=[30, 60])),
    color=alt.Color('choice:N', title='', scale=alt.Scale(domain=['Dem', 'Rep'], range=['Blue', 'Red'])),
).properties(title='The Generic Ballot (2025-2026)', width=640)

selectors = alt.Chart(generic_ballot_avg).mark_point().encode(
    x='end_date:T',
    opacity=alt.value(0),
).add_params(
    nearest
)

points = line.mark_point().encode(
    opacity=alt.condition(nearest, alt.value(1), alt.value(0))
)

tooltip = alt.Chart(generic_ballot_avg).mark_rule(color='gray').encode(
    x='end_date:T',
).transform_filter(
    nearest
)

text = line.mark_text(align='left', dx=5, dy=-5).encode(
    text=alt.condition(nearest, 'pct:Q', alt.value(''))
)

generic_ballot_avg_plot = alt.layer(
    line, selectors, points, tooltip, text
).properties(
    width=600, height=300
)

# Save the plot to HTML and PNG files.
generic_ballot_avg_plot.save('plot_generic_ballot.html')
print("plot_generic_ballot.html Completed!")
generic_ballot_avg_plot.save('plot_generic_ballot.png')
print("plot_generic_ballot.png Completed!")