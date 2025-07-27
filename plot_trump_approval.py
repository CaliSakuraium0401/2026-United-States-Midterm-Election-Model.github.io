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
donald_trump_approval = polls_df[polls_df['subject'] == 'Donald Trump']
donald_trump_approval = polls_df[polls_df['poll_type'] == 'approval']

# Do further filting to remove bias polling or other undesireable metrics such as polls conducted to non voters.
donald_trump_approval = donald_trump_approval[donald_trump_approval['pollster'] != 'Trafalgar Group']
donald_trump_approval = donald_trump_approval[donald_trump_approval['pollster'] != 'Trafalgar Group/InsiderAdvantage']
#donald_trump_approval = donald_trump_approval[donald_trump_approval['pollster'] != 'RMG Research']
donald_trump_approval = donald_trump_approval[donald_trump_approval['pollster'] != 'Morning Consult']
donald_trump_approval = donald_trump_approval[donald_trump_approval['pollster'] != 'Ipsos']
donald_trump_approval = donald_trump_approval[donald_trump_approval['pollster'] != 'TIPP Insights']
# Make it so the data only includes registered voters.
donald_trump_approval = donald_trump_approval[donald_trump_approval['population'] != 'a']

# Wrangle the data regarding Donald Trump's approval ratings for visualization.
# This includes flattening the answers, normalizing the structure, converting percentages,
# filtering for relevant dates, and calculating a rolling average for each response choice.
donald_trump_approval = donald_trump_approval.explode('answers').reset_index(drop=True)
donald_trump_approval_answers = pd.json_normalize(donald_trump_approval['answers'])
donald_trump_approval = pd.concat([donald_trump_approval.drop(columns=['answers']), donald_trump_approval_answers], axis=1)
donald_trump_approval.loc[donald_trump_approval['pct'].abs() < 1, 'pct'] *= 100
donald_trump_approval['end_date'] = pd.to_datetime(donald_trump_approval['end_date'])
donald_trump_approval = donald_trump_approval[donald_trump_approval['end_date'] >= '2025-01-01']
donald_trump_approval_avg = donald_trump_approval.groupby(['end_date', 'choice'], as_index=False)['pct'].mean()
donald_trump_approval_avg['pct'] = donald_trump_approval_avg.groupby('choice')['pct'].transform(lambda x: x.rolling(window=14, min_periods=1).mean())
donald_trump_approval_avg['pct'] = donald_trump_approval_avg['pct'].round(2)

# Prepare the interactive chart.
nearest = alt.selection_point(name="nearest", fields=['end_date'], nearest=True, on='mouseover', empty='none')

line = alt.Chart(donald_trump_approval_avg).mark_line().encode(
    x=alt.X('end_date:T',
        title='Date',
        axis=alt.Axis(
            format='%b %Y',
            tickCount='month',
            labelAngle=-45
        ),
        scale=alt.Scale(domain=['2025-01-01', '2025-12-31'])),
    y=alt.Y('pct:Q', title='Percentage', scale=alt.Scale(domain=[25, 65])),
    color=alt.Color('choice:N', title='', scale=alt.Scale(domain=['Approve', 'Disapprove'], range=['purple', 'orange']))
).properties(title='Trump Approval Rating (2025)', width=640)

selectors = alt.Chart(donald_trump_approval_avg).mark_point().encode(
    x='end_date:T',
    opacity=alt.value(0),
).add_params(nearest)

points = line.mark_point().encode(opacity=alt.condition(nearest, alt.value(1), alt.value(0)))

tooltip = alt.Chart(donald_trump_approval_avg).mark_rule(color='gray').encode(
    x='end_date:T',
).transform_filter(nearest)

text = line.mark_text(align='left', dx=5, dy=-5).encode(
    text=alt.condition(nearest, 'pct:Q', alt.value(''))
)

donald_trump_approval_avg_plot = alt.layer(
    line, selectors, points, tooltip, text
).properties(width=600, height=300)

# Save the plot to HTML and PNG files.
donald_trump_approval_avg_plot.save('plot_trump_approval.html')
print("plot_trump_approval.html Completed!")
donald_trump_approval_avg_plot.save('plot_trump_approval.png')
print("plot_trump_approval.png Completed!")