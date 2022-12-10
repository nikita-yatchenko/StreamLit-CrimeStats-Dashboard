import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import altair as alt
import plotly.express as px
import wget

st.write("""
# Exploratory analysis for crime data from the United Stats

## Analysis will constist of 5 explorations:
1. Which state is the most dangerous? Dangerous is defined by total crimes per 100,000
2. Exploring racial component: what happens to the average crime rate as various race percentages increase?
3. Is there a connection between poor communities and crime, in particular robberies, larcenies, burglaries and auto theft?
4. Is defunding the police helpful? Connection between number of police officer and crimes in areas with non whites.
5. Do divorced men commit more crime, and if yes, which ones?
data source: US Communities Dataset from Kaggle
""")

crime_data = pd.read_csv("./data/crimedata.csv")

crimes_names = ['murders',
                'rapes', 'robberies', 'assaults',
                'burglaries', 'larcenies',
                'autoTheft', 'arsons',
                ]

crime_data.loc[:, 'total_crimes'] = crime_data[crimes_names].sum(axis=1)
crime_data.loc[:, 'total_crimes_per_pop'] = crime_data.loc[:, 'total_crimes'] / crime_data.loc[:,
                                                                                'population'] * 100_000

st.subheader('1. Which state is most dangerous for the location of American communities?')

st.write("""Mean Violent сrimes per population by state""")

number = 0
selection1 = st.multiselect('Select which states you want to be displayed', sorted(crime_data['state'].unique()),
                            sorted(crime_data['state'].unique()), key=number)
crime_data_h1 = crime_data.groupby('state').agg({'total_crimes': 'sum',
                                                 'population': 'sum'}).reset_index()
crime_data_h1.loc[:, 'avg crimes per 100,000'] = crime_data_h1.total_crimes / crime_data_h1.population

# fig = plt.figure(figsize=(10, 4))
# graphic_1 = sns.barplot(data=crime_data_h1[crime_data_h1.state.isin(selection1)], x='state', y='total_crimes_per_pop')
# st.pyplot(fig)

st.write("""This graphic shows correct accounting of average crimes: total crimes in state by total population""")
graphic_1 = alt.Chart(crime_data_h1[crime_data_h1.state.isin(selection1)]).mark_bar().encode(x='state',
                                                                                             y='avg crimes per 100,000')
st.write(graphic_1)

st.write("""This graphic shows incorrect accounting of average crimes: simple average of averages by states""")
inc_crime_data_h1 = crime_data.groupby('state').agg({'total_crimes_per_pop': 'mean'}).reset_index()
inc_crime_data_h1.columns = ['state', 'avg crimes per 100,000']

graphic_2 = alt.Chart(inc_crime_data_h1[inc_crime_data_h1.state.isin(selection1)]).mark_bar().encode(x='state',
                                                                                                     y='avg crimes per 100,000')
st.write(graphic_2)

st.write(""" This is a perfect example how statistics can be misleading. Depending on how you count the averages 
 a completely different picture can be drawn from data. Using the correct calculations we see that the most violent 
 state is Nevada. Population is not that high but there are a lot of crimes there - probably in Las Vegas.""")

st.subheader(
    '2. Exploring racial component: what happens to the average crime rate as various race percentages increase?')

st.write("""Exploring controversial topic of races and crime. First step is to see what the correlation is. Then we 
can start understanding WHY correlation is there. """)


def mapper(x):
    if 0 <= x < 10:
        return 1
    elif 10 <= x < 20:
        return 2
    elif 20 <= x < 30:
        return 3
    elif 30 <= x < 40:
        return 4
    elif 40 <= x < 50:
        return 5
    elif 50 <= x < 60:
        return 6
    elif 60 <= x < 70:
        return 7
    elif 70 <= x < 80:
        return 8
    elif 80 <= x < 90:
        return 9
    elif 90 <= x < 100:
        return 10


race_crime = crime_data[list(crime_data.columns[crime_data.columns.str.contains('race')]) + ['total_crimes_per_pop']]
race_crime_melt = pd.melt(race_crime, ['total_crimes_per_pop'])
race_crime_melt.loc[:, 'quant_label'] = race_crime_melt.value.apply(lambda x: mapper(x))
race_crime_group_quant = race_crime_melt.groupby(['variable', 'quant_label'])[
    'total_crimes_per_pop'].mean().reset_index()
race_crime_group_quant.columns = ['race', 'quantile label', 'avg total crimes per 100,000']

race_crime_group_quant.race = race_crime_group_quant.race.map({
    'racePctAsian': 'asian',
    'racePctHisp': 'hispanic',
    'racePctWhite': 'white',
    'racepctblack': 'black'
})

number = 1
selection2 = st.multiselect('Select which races you want to be displayed',
                            sorted(race_crime_group_quant['race'].unique()),
                            sorted(race_crime_group_quant['race'].unique()), key=number)

graphic_3 = alt.Chart(race_crime_group_quant[race_crime_group_quant.race.isin(selection2)]).mark_line().encode(
    x='quantile label',
    y='avg total crimes per 100,000',
    color='race',
    strokeDash='race',
).interactive().properties(
    width=1000,
    height=500
).configure_legend(
    orient="right"
).configure_point(
    size=200
)

st.write(graphic_3)

st.write("""This graphic shows correlation between race proportion and average total crimes per 100,000 people""")

st.subheader('3. Is there a connection between poor communities and crime, in particular, robberies, '
             'larcenies, burglaries, and auto theft?')
number = 2
selection3 = st.multiselect('Select which states you want to be displayed',
                            sorted(crime_data['state'].unique()),
                            sorted(crime_data['state'].unique()), key=number)

crime_data.loc[:, 'persnl_property_crimes'] = crime_data.loc[:, ['robberies', 'burglaries',
                                                                 'larcenies', 'autoTheft']].sum(
    axis=1) / crime_data.population

fig = px.scatter(crime_data[crime_data.state.isin(selection3)], x="medIncome", y="persnl_property_crimes", labels={
    "medIncome": "Median income",
    "persnl_property_crimes": "Personal Property Crimes"
}, title='Income vs average number of personal property crimes', width=1000, height=500)

st.plotly_chart(fig, use_container_width=True)

st.write(""" Makes sense that the wealthier you are less crime you want to commit. Also in wealthier communities
there is better security and in very poor communities there is not much to steal. So the majority of crimes happen in 
low to medium wealthy communities""")

st.subheader('4. Is defunding the police helpful? Connection between number of police officer and crimes '
             'in areas with non whites.')


to_plot = crime_data[['racePctWhite', 'PolicBudgPerPop', 'total_crimes_per_pop']].copy()
to_plot.columns = [['pct_whites', "Number of police officers per 100,000", "Avg number of crimes per 100,000"]]

number = 3
selection4 = st.selectbox('Select percent of non white population', sorted(range(5, 65, 5), reverse=True), key=number)

# print(to_plot.head())
# fig = alt.Chart(to_plot[
#     (to_plot.pct_whites > (100 - selection4 - 5)) & (to_plot.pct_whites <= (100 - selection4))]).mark_point().encode(
#     x="Number of police officers per 100,000",
#     y="Avg number of crimes per 100,000")

fig = alt.Chart(crime_data[
    (crime_data.racePctWhite > (100 - selection4 - 5)) & (crime_data.racePctWhite < (100 - selection4))]).mark_point().encode(
    x=alt.X("PolicBudgPerPop", title='Number of police officers per 100,000'),
    y=alt.Y("total_crimes_per_pop", title='Avg number of crimes per 100,000'),
)


# final_plot = fig + fig.transform_regression("Number of police officers per 100,000",
#                                             "Avg number of crimes per 100,000").mark_line()

final_plot = fig + fig.transform_regression("PolicBudgPerPop",
                                            "total_crimes_per_pop").mark_line()

st.write(final_plot)

st.write(""" Seems like there is no apparent connection between number of crimes and number of police officers without other 
 factors affecting it. There are examples of positive and negative correlations  """)

st.subheader('5. Do divorced men commit more crime, and if yes, which ones?')

number = 4
selection5 = st.multiselect('Select a state', sorted(crime_data['state'].unique()),
                            sorted(crime_data['state'].unique()),
                            key=number)

fig = px.scatter(crime_data[crime_data.state.isin(selection3)], x="MalePctDivorce", y="total_crimes_per_pop", labels={
    "MalePctDivorce": "Percentage of divorced men",
    "total_crimes_per_pop": "Total crimes per 100,000"
}, title='Percentage of divorced men vs number of crimes per 100,000')
fig.update_layout(margin=dict(t=30))
st.plotly_chart(fig, use_container_width=True)

number = 5
selection6 = st.selectbox('Select a crime', crimes_names, key=number)

fig = px.scatter(crime_data, x="MalePctDivorce", y=selection6, labels={
    "MalePctDivorce": "Percentage of divorced men",
    selection6: selection6
}, title=f'Percentage of divorced men vs number of {selection6}')
fig.update_layout(margin=dict(t=30))
st.plotly_chart(fig, use_container_width=True)

st.write(""" There is a linear relation between the number of divorced men and rapes.
Perhaps in such communities it is worth paying more attention to psychological assistance to vulnerable segments of the population""")
