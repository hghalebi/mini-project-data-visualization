import streamlit as st
import matplotlib.pyplot as plt
import altair as alt
import pandas as pd
import geopandas as gpd # Requires geopandas -- e.g.: conda install -c conda-forge geopandas
from shapely import wkt
import json
from shapely.geometry import mapping
import folium
import os
from llm import anlyze_data
processed_data_file = 'processed_data.csv'
alt.data_transformers.enable('json')
ui = {
    'title': 'Mini project as data visualization project  ',
    'subtitle': 'This is a mini project aims to visualize the data of first name in France and make some analysis based on name trend over time.',
    'welcome_message': 'Welcome to the mini project',
    'loading_data': 'Loadding data...',
    'raw_data': 'you can see the table of raw data below. You can surf by scrolling down',
    'name of time': 'Please filter data by name then chose a gender to see its trend over time',
    
}
# write  dataframe to csv file
def write_csv(df, filename='processed_data.csv'):
    try:
        df.to_csv(filename, index=False, encoding='utf-8', sep=';')
    except Exception as e:
        raise e
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

st.title(ui['title'])
st.write(ui['subtitle'])
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
    if type(data) is not pd.DataFrame:
        # read the csv file
        return read_csv(data)
    
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
    
    write_csv(df=data, filename=processed_data_file)
    return data

with st.spinner("Loadding data..."):    
    data = read_csv(csv_file=csv_file)
    # if process_data_file exists, read it

    if os.path.exists(processed_data_file):
        data = process_data(data=processed_data_file)
    else:
        data = read_csv(csv_file)
        data = process_data(data=data)
    
    st.write(ui['raw_data'])
    st.dataframe(data)
    # if content_cached:
    #     content_cached = anlyze_content
    # else:
    #     content_cached = ""
    
    with st.expander("See explanation"):
        anlyze_content = anlyze_data(data=data, comment="Trent of evaluation of first name over time, and make sure not repeating any thing in following analysis: {content_cached}}")
        st.markdown(anlyze_content, unsafe_allow_html=True)
    st.success("Done!")

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
st.title("Top 10 popular Names")
st.write("Filter data by gender and year")
genre = st.radio("Gender",("Female","Male"))
year = st.selectbox("Year",get_years(data=data))


with st.spinner('Wait for it...'):
    popular_names = get_popular_names (data=data,year=year,gender=genre,top=10)
    content_cached = anlyze_content
    anlyze_content = anlyze_data(data=popular_names, comment=f"Top 10 most popular {genre} names in {year}. make sur to not repeat the following content {content_cached}") 
    
    st.pyplot(plot_popular_name(data=popular_names[0], title=popular_names[1]))
    with st.expander("See explanation"):
        st.markdown(anlyze_content)    
    st.success("Done!")

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
    return fig, grouped_data

@st.cache_data
def get_geo_data(geo_json_file='Names_hints/departements-version-simplifiee.geojson'):
    if os.path.exists(geo_json_file):
        depts = gpd.read_file(geo_json_file)
        print("geo data read from file")
        print(depts.head())
        return depts
    else:
        raise Exception(f'File {geo_json_file} does not exist')

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
st.title("Names trends over time")
st.write(" In this session we will see the popularity of a name over time by gender")
genre2 = st.radio(ui['name of time'],("Female","Male"))

if genre2 == "Female":
    top_female_name = get_popular_names(data=data,gender=genre2,top=20)
    
    selected_name = st.selectbox(" Name", top_female_name.index.tolist()) 
if genre2 == 'Male':
    top_male_name = get_popular_names(data=data,gender=genre2,top=20)
    selected_name = st.selectbox("Name?" , top_male_name.index.tolist())

with st.spinner(f'Wait for evaluation of the name {selected_name}'):
    map, name_evaluation = plot_name_evaluation(data=data, name=selected_name)
    print(name_evaluation.head())
    content_cached = anlyze_content
    anlyze_content = anlyze_data(data=name_evaluation.head(50), comment=f"The main point of this analyse is the popularity of the name {selected_name} over time and it significances.")
   
    st.pyplot(map)
    with st.expander("See explanation"):
        st.markdown(anlyze_content)     
    st.success("Done!")




# Create the map chart if the "Show the map" button is clicked
# if st.button('Show the map'):
#     st.write("Wait for the map to load")
#     with st.spinner('Wait generating map. It could take several mins...'):
#         print("Going to get the geo data")
#         geographic_data = get_geo_data()
#         print("geo data read")
#         print(geographic_data.head())
#         # print out the geographic data
        
#         # Calculate the latitude and longitude from the geometry column
#         geographic_data['latitude'] = geographic_data['geometry'].centroid.y
#         geographic_data['longitude'] = geographic_data['geometry'].centroid.x

#         # Create the map chart using folium
#         map_chart = folium.Map(location=[geographic_data['latitude'].mean(), geographic_data['longitude'].mean()], zoom_start=4)
#         for _, row in geographic_data.iterrows():
#             folium.Marker([row['latitude'], row['longitude']]).add_to(map_chart)

#         # Display the chart using st.write
#         st.write(map_chart._repr_html_(), unsafe_allow_html=True)
#         st.write("Map added to the browser")