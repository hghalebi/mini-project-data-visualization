import streamlit as st
import matplotlib.pyplot as plt
import altair as alt
import pandas as pd
import geopandas as gpd # Requires geopandas -- e.g.: conda install -c conda-forge geopandas
from shapely import wkt
import json
from shapely.geometry import mapping

alt.data_transformers.enable('json')

def geo_name_evaluation2(data, _geo_data, name = 'Marie' ):
    print("in the geo_name_evaluation")

    # Filter data based on 'name' as soon as possible
    data = data[data['First name'] == name]

    # Group by necessary columns and compute the sum of births
    data_grouped = data.groupby(['Department', 'First name','Gender'], as_index=False).agg(
        {'Number of births': 'sum'}
        )

    # Merge once 
    merged_data = _geo_data.merge(data_grouped, left_on='code', right_on='Department')

    # Convert the geometry to GeoJSON format using vectorized operation
    merged_data['geometry'] = merged_data['geometry'].map(mapping)

    # Create a DataFrame with GeoJSON objects
    geo_data = pd.DataFrame({
        'properties': merged_data[['Department', 'First name', 'Gender', 'Number of births']].to_dict('records'),
        'geometry': merged_data['geometry'].tolist()
    })

    # Flatten properties column in geo_data DataFrame
    geo_data = pd.json_normalize(geo_data['properties']).join(geo_data['geometry'])

    # Create the Altair Chart
    chart = alt.Chart(alt.Data(values=geo_data.to_dict('records'))).mark_geoshape(
        stroke='white'
            ).encode(
                tooltip=[
                    alt.Tooltip('Department:N'),
                    alt.Tooltip('First name:N'),
                    alt.Tooltip('Gender:N'),
                    alt.Tooltip('Number of births:Q')
                ],
                color='Number of births:Q',
            ).properties(
                width=800, 
                height=600, 
                title=f'Popularity of the name {name} over time'
            )

    return chart

st.title("Mini project")
st.write("This is a mini project for streamlit")
csv_file = 'Names_hints/dpt2020.csv'
import pandas as pd

def get_gender(gender):
    if gender == 1 or gender == '1':
        return "Male"
    elif gender == 2 or gender == '2':
        return "Female"
    return "No binary"



@st.cache_data
def read_csv(csv_file):
    df = pd.read_csv(csv_file, sep=';')
    return df

#@st.cache_data
def process_data(data):
    new_column_names = ['Gender', 'First name', 'Year','Department', 'Number of births']
    data.columns = new_column_names
    # drope rows with NaN values
    data = data.dropna()
    # drop rows with XXXX values
    data = data[data['Year'] != 'XXXX']
    data = data[data['Department'] != 'XX']
    # convert the column 'Number of births' to integer, and the column 'Year' to datetime format
    data['Number of births'] = data['Number of births'].astype(int)
    data['Year'] = pd.to_datetime(data['Year'], format='%Y', errors='coerce').dt.strftime('%Y')
    # Conver Gender to Male and Female instead of 1 and 2

    data['Gender'] = data['Gender'].apply(get_gender)
    # drop First name is "_PRENOMS_RARES"

    data = data[data['First name'] != '_PRENOMS_RARES']
    data['First name'] = data['First name'].str.lower().str.capitalize()
    
    return data

with st.spinner("Loadding data..."):    
    data = read_csv(csv_file=csv_file)
    data = process_data(data=data)
    st.dataframe(data)


@st.cache_data
def get_yearly_births(data):
    return data.groupby(['Year'])['Number of births'].sum()

@st.cache_data
def get_popular_names(data, year,gender, top=10):
    title = f"Top {top} Most {gender} Popular First Names of {year}"
    return data[(data['Year'] == year) & (data['Gender'] == gender)].sort_values(by='Number of births', ascending=False).head(top) , title

@st.cache_data
def plot_popular_name(data,top = 10, title="You need modify the title"):
    grouped = data.groupby('First name')['Number of births'].sum()
    sorted_grouped = grouped.sort_values(ascending=False)

    tops = sorted_grouped[:top]

    # Now we can plot the pie chart
    
    fig = plt.figure(figsize=(10,10))
    plt.pie(tops ,labels=tops.index, autopct='%1.1f%%')
    
    plt.title(title, fontsize=20)
    
    return fig

@st.cache_data
def get_years(data):
    return data['Year'].unique().tolist()

genre = st.radio("Gender",("Female","Male"))
year = st.selectbox("Year",get_years(data=data))


with st.spinner('Wait for it...'):
    popular_names = get_popular_names (data=data,year=year,gender=genre,top=10)
    st.pyplot(plot_popular_name(data=popular_names[0], title=popular_names[1]))


@st.cache_data
def get_popular_names(data,gender='Female',top = 20):
    
    # Filter the data for only rows based on the gender
    top_data = data[data['Gender'] == gender]

    # Group the data by first name and sum up the number of births
    grouped_data = top_data.groupby('First name')['Number of births'].sum()

    # Sort the data in descending order
    sorted_data = grouped_data.sort_values(ascending=False)

    # Get the top names
    top_names = sorted_data[:top]
    
    return top_names

@st.cache_data
def plot_name_evaluation(data, name = 'Marie' ):
    name_data = data[data['First name'] == name]

# Group the data by year and sum up the number of births
    grouped_data = name_data.groupby('Year')['Number of births'].sum()

    # Plot the data
    fig = plt.figure(figsize=(40,6))
    plt.xticks(fontsize=5)
    plt.plot(grouped_data.index, grouped_data, marker='o')
    plt.title(f'Popularity of the name {name} over time')
    plt.xlabel('Year')
    plt.ylabel('Number of births')
    plt.grid()
    return fig

@st.cache_data
def get_geo_data(geo_json_file='Names_hints/departements-version-simplifiee.geojson'):
    depts = gpd.read_file(geo_json_file)
    
    return depts

@st.cache_data
def geo_name_evaluation(data, _geo_data, name = 'Marie' ):
    print("in the geo_name_evaluation")
    merged_data = pd.merge(data, _geo_data, left_on='Department', right_on='code')
    grouped_data = merged_data.groupby(['Department', 'First name','Gender'], as_index=False).agg(
        {'Number of births': 'sum'}
        )
    grouped_data = _geo_data.merge(
            grouped_data,
            left_on='code',
            right_on='Department'
            )
    ## Convert the geometry to WKT format
    #grouped_data['geometry'] = grouped_data['geometry'].apply(lambda geom: json.dumps(mapping(geom)))
    grouped_data['geometry'] = grouped_data['geometry'].apply(lambda x: mapping(x))

    # Create a DataFrame with GeoJSON objects
    geo_data = pd.DataFrame({
        'properties': grouped_data[['Department', 'First name', 'Gender', 'Number of births']].to_dict('records'),
        'geometry': grouped_data['geometry'].tolist()
    })

    # Flatten properties column in geo_data DataFrame
    geo_data = pd.json_normalize(geo_data['properties']).join(geo_data['geometry'])

    # Create the Altair Chart
    # Create the Altair Chart
    c = alt.Chart(alt.Data(values=geo_data.to_dict('records'))).mark_geoshape(
        stroke='white'
            ).encode(
                tooltip=[
                    alt.Tooltip('Department:N'),
                    alt.Tooltip('First name:N'),
                    alt.Tooltip('Gender:N'),
                    alt.Tooltip('Number of births:Q')
                ],
                color='Number of births:Q',
            ).properties(
                width=800, 
                height=600, 
                title=f'Popularity of the name {name} over time'
            )

    return c

genre2 = st.radio("Gender? ",("Female","Male"))

if genre2 == "Female":
    top_female_name = get_popular_names(data=data,gender=genre2,top=20)
    selected_name = st.selectbox(" Name", top_female_name.index.tolist()) 
if genre2 == 'Male':
    top_male_name = get_popular_names(data=data,gender=genre2,top=20)
    selected_name = st.selectbox("Name?" , top_male_name.index.tolist())

with st.spinner(f'Wait for evaluation of the name {selected_name}'):
    st.pyplot(plot_name_evaluation(data=data, name=selected_name))
    
    



# Create the map chart is it clicked on the button

if st.button('Show the map'):
    st.write("Wait for the map to load")
    with st.spinner('Wait genrating map. It could take several mins...'):
        with st.spinner('Wait for it...'):
            goegraphic_data = get_geo_data()
        
        map_chart = geo_name_evaluation2(data=data,
                                _geo_data=get_geo_data(),
                                name=selected_name)

        st.altair_chart(map_chart, use_container_width=True)
        st.write("Map added to the browser")
            
