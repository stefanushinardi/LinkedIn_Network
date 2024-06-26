import io
import pandas as pd
from janitor import clean_names
import janitor
import plotly.express as px
import streamlit.components.v1 as components
from pyvis import network as net
import networkx as nx
import streamlit as st
from io import StringIO

st.set_page_config(
        page_title="LinkedIn Network Graphs",
)

st.title("LinkedIn Network Visualizer")
st.write('Wharton Influence Class Project')
st.write('Created by Stefanus Hinardi, Apr 2024')
st.write("For instructions on downloading your LinkedIn connections file, click on the accordion below")
with st.expander(''):
    st.write("""
        1. Sign in to your LinkedIn account.
        2. Navigate to the upper left corner of the screen and click on the downward arrow below your profile picture.
        3. From the dropdown menu, select "Settings & Privacy" under the 'Account' section.
        4. In the 'Data Privacy' category, choose "Get a copy of your data."
        5. Select the button next to the second option labeled "Specify what you want."
        6. Tick the box next to "Connections."
        7. Click on "Request archive" and, if prompted, enter your password and confirm.
        8. Allow some time for LinkedIn to process your request; typically, it takes less than 20 minutes.
        9. Once your data is ready, LinkedIn will send you an email notification.
        10. Download the zip file provided by LinkedIn, unzip it, and then utilize the file uploader below to share your connections list.   
    """)

video_file = open("example_vid.webm", "rb").read()

# st.write("For a video showing how to use this app, click on the plus sign below")
# with st.expander(''):
#     st.video(video_file)


# uploading and cleaning data file
uploaded_file = st.file_uploader("Choose your LinkedIn Connections.csv file")

if uploaded_file is not None:
  df_ori = pd.read_csv(uploaded_file, skiprows=3) #skiprows=3 gets rid of notes at top of file
else:
    st.warning('Please upload a LinkedIn connections.csv file to begin.')
    st.stop()

df = (
    df_ori
    .clean_names() # remove spacing and capitalization
    .dropna(subset=['company', 'position']) # drop missing values in company and position
    .to_datetime('connected_on', format='%d %b %Y')
  )

pattern = "freelance|self-employed"
df = df[~df['company'].str.contains(pattern, case=False)]

# setting up sidebar for background, color, font, and other graph options
st.sidebar.title('Graph Options')
color_option = st.sidebar.selectbox(
'Color palette for bar graphs:',
('Tealgrn', 'Magenta', 'Rainbow', 'Plotly3', 'Inferno', 'Sunset', 'Cividis', 'Purple-Blue', 'Teal', 'Pink-Yellow'))

def str_to_class(name):
    if name == "Tealgrn":
        return px.colors.sequential.Tealgrn
    elif name == "Plotly3":
        return px.colors.sequential.Plotly3
    elif name == "Inferno":
        return px.colors.sequential.Inferno
    elif name == "Sunset":
        return px.colors.sequential.Sunset
    elif name == "Cividis":
        return px.colors.sequential.Cividis
    elif name == 'Rainbow':
        return px.colors.sequential.Rainbow
    elif name == 'Purple-Blue':
        return px.colors.sequential.PuBu_r
    elif name == 'Magenta':
        return px.colors.sequential.Magenta_r
    elif name == 'Teal':
        return px.colors.sequential.Teal
    elif name == 'Pink-Yellow':
        return px.colors.sequential.Pinkyl_r

graph_option = st.sidebar.radio(label='Select a circular or packed network graph:', options=('Packed graph', 'Spoked graph'))

def str_to_option(option):
    if option == "Spoked graph":
        return nt.repulsion()
    else:
        return nt.hrepulsion()

color_network_option = st.sidebar.selectbox('Color palette for network graphs:', 
('Bolds', 'Pastels', 'Bluegreen', 'Blues', 'Neons'))

Bolds = ['#10EDF5', '#28BCE0', '#556CBC', '#7343A9', '#9B0F8C', '#B8007F']
Pastels = ['#9C82B5', '#C493C9', '#E88EBB', '#FEA2AF', '#FDD6CF', '#FFEDDF']
Bluegreen = ['#0D98BB', '#2AA7BC', '#47B6BC', '#65C4BD', '#82D3BD', '#9FE2BE']
Blues = ['#088CFF', '#36A3FF', '#64BAFE', '#91D1FE', '#BFE8FD', '#EDFFFD']
Neons = ['#FCFF64', '#444AFF', '#FFB6F4', '#F9008F', '#39FF12', '#9D0BFA']

def network_color(color_choice):
    if int(count)/len(df_company_reduced) >=.833:
        return eval(color_choice)[0]
    elif int(count)/len(df_company_reduced) >= .667:
        return eval(color_choice)[1]
    elif int(count)/len(df_company_reduced) >= .50:
        return eval(color_choice)[2]
    elif int(count)/len(df_company_reduced) >= .33:
        return eval(color_choice)[3]
    elif int(count)/len(df_company_reduced) >= .166:
        return eval(color_choice)[4]
    else:
        return eval(color_choice)[5]

count_option = st.sidebar.slider('Choose the minimum number of connections at company for them to be included:', 1, 20, 3)

position_option = st.sidebar.slider('Choose the minimum number of position titles for it to be included:', 1, 20, 3)

number_sample_option = st.sidebar.slider('Choose the number of sample included', 20, 10, 150)


root_name = st.sidebar.text_input("To put your name at the center of the network diagrams, enter it here:")

# st.sidebar.write('Thanks to Benedict Neo for the inspiration and code used from this article: https://medium.com/bitgrit-data-science-publication/visualize-your-linkedin-network-with-python-59a213786c4')
# st.sidebar.write('And to Bradley Schoeneweis: https://bschoeneweis.github.io/visualizing-your-linkedin-connections-using-python')
# creating bar graphs
df_company = df['company'].value_counts().reset_index()
df_company.columns = ['company', 'count']
df_top_co = df_company.sort_values(by='count', ascending=False).head(20)

co_graph = px.bar(df_top_co, x='count', y='company', color='count', orientation='h', color_continuous_scale=str_to_class(color_option)).update_layout(yaxis_categoryorder="total ascending")
st.header('Connections by Company')
st.write(co_graph)
st.markdown('#')

df_pos = df['position'].value_counts().reset_index()
df_pos.columns = ['position', 'count']
df_top_pos = df_pos.sort_values(by='count', ascending=False).head(15)

pos_graph = px.bar(df_top_pos, x='count', y='position', color='count', orientation='h', color_continuous_scale=str_to_class(color_option)).update_layout(yaxis_categoryorder="total ascending")
st.header('Connections by Position')
st.write(pos_graph)
st.markdown('#')


hist_values = px.histogram(df['connected_on'], nbins=15, orientation='h', color=df['connected_on'].dt.year, color_discrete_sequence=str_to_class(color_option)).update_layout(bargap=0.1)
st.header('Connections by Date')
st.write(hist_values)
st.markdown('#')

# prepping data for the first network graph
df_position = df['position'].value_counts().reset_index()
df_position.columns = ['position', 'count']
df_position = df_position.sort_values(by="count", ascending=False)

df_company_reduced = df_company.loc[df_company['count']>=count_option]

# initialize graph
g = nx.Graph()
g.add_node(root_name)

# use iterrows tp iterate through the data frame
for _, row in df_company_reduced.iterrows():

  # store company name and count
  company = row['company']
  count = row['count']

  title = f"<b>{company}</b> – {count}"
  positions = set([x for x in df[company == df['company']]['position']])
  positions = ''.join('<li>{}</li>'.format(x) for x in positions)

  position_list = f"<ul>{positions}</ul>"
  hover_info = title + position_list

  g.add_node(company, size=count*5, weight=count, color=network_color(color_network_option), title=hover_info, borderWidth=4)
  g.add_edge(root_name, company, color='grey')

# generate the graph
nt = net.Network('750px', '100%', bgcolor='#31333f', font_color='white')
nt.from_nx(g)
str_to_option(graph_option) # user option for either a spoked or packed graph
nt.save_graph(f'company_graph.html')
st.header('Connections by Company Graph')
HtmlFile = open(f'company_graph.html','r',encoding='utf-8')

# Load HTML into HTML component for display on Streamlit
components.html(HtmlFile.read(), height=800, width=800)

with open("company_graph.html", "rb") as file:
     btn = st.download_button(
             label="Download company graph",
             data=file,
             file_name="company_graph.html",
             mime="file/html"
           )

st.markdown('#')

# prepping data for the 2nd network graph
df_position_reduced = df_pos.loc[df_pos['count']>=position_option]

# initialize graph
p = nx.Graph()
p.add_node(root_name)

# use iterrows tp iterate through the data frame
for _, row in df_position_reduced.iterrows():

  count = f"{row['count']}"
  position= row['position']
  
  p.add_node(position, size=count, weight=count, color=network_color(color_network_option), title=count, borderWidth=4, strokeWidth=2, strokeColor='black')
  p.add_edge(root_name, position, color='grey')

# generate the graph
nt = net.Network('750px', '100%', bgcolor='#31333f',  font_color='white')
nt.from_nx(p)
str_to_option(graph_option) # user option for either a spoked or packed graph
nt.save_graph(f'position_graph.html')
HtmlFile = open(f'position_graph.html','r',encoding='utf-8')

# Load HTML into HTML component for display on Streamlit
st.header('Connections by Position Graph')
components.html(HtmlFile.read(), height=800, width=800)

with open("position_graph.html", "rb") as file:
     btn = st.download_button(
             label="Download position graph",
             data=file,
             file_name="position_graph.html",
             mime="file/html"
           )

st.markdown('#')

# Preping data for poples graoh

# initialize graph
p = nx.Graph()
p.add_node(root_name)
st.header('People Graph')
number_sample_option = st.slider('Choose the number of sample included', 20, 10, 150, key = "test")
company_dict = {}
position_dict = {}

# use iterrows tp iterate through the data frame
for i , row in df.sample(n=number_sample_option).iterrows():

  size = 10
  name= row['first_name'] + " " + row['last_name']
  company = row['company']
  position = row['position']

  title = name + '<br/> <br/>' + company + '<br/> <br/>' + position
  print(name + " " + company + " " + position)
  p.add_node(name, size=size, weight=count, color=network_color(color_network_option), title=title, borderWidth=4, strokeWidth=2, strokeColor='black')
  p.add_edge(root_name, name, color='grey')

  if company in company_dict.keys():
      for person in company_dict[company]:
          p.add_edge(person, name, color='green')
  else:
      company_dict[company] = [name]
  
  if position == "position":
      continue
  if position in position_dict.keys():
      for person in position_dict[position]:
          p.add_edge(person, name, color='blue')
  else:
      position_dict[position] = [name]

nt = net.Network('750px', '100%', bgcolor='#31333f',  font_color='white')
nt.from_nx(p)
str_to_option(graph_option) # user option for either a spoked or packed graph
nt.save_graph(f'people_graph.html')
HtmlFile = open(f'people_graph.html','r',encoding='utf-8')


# Load HTML into HTML component for display on Streamlit


components.html(HtmlFile.read(), height=800, width=800)
