import streamlit as st
import matplotlib.pyplot as plt

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

@st.cache_data
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


genre2 = st.radio("Gender? ",("Female","Male"))

if genre2 == "Female":
    top_female_name = get_popular_names(data=data,gender=genre2,top=20)
    selected_name = st.selectbox(" Name", top_female_name.index.tolist()) 
if genre2 == 'Male':
    top_male_name = get_popular_names(data=data,gender=genre2,top=20)
    selected_name = st.selectbox("Name?" , top_male_name.index.tolist())

with st.spinner(f'Wait for evaluation of the name {selected_name}'):
    st.pyplot(plot_name_evaluation(data=data, name=selected_name))