import folium
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import matplotlib as mpl
from matplotlib import pyplot as plt
from numpy import interp

#=============Data=============

#Load data 
df = pd.read_csv("earthquakes.csv",header=0, parse_dates=["Date"])
#Only keep usefull columns
df = df.query("Type == 'Earthquake'")[["Date","Time","Latitude","Longitude","Depth","Magnitude","Loc_country","Type_ew","Loc_flag_country","Loc_name"]].sort_values(by='Magnitude',ascending=False)
#Adding a year column
df["year"] = df["Date"].dt.strftime("%Y").astype('int')

#=============Variable Initalization=============

years = df.year.unique()
countries = df.Loc_flag_country.sort_values().unique().tolist()
countries.insert(0,"TOUS")

#=============Interface=============
st.set_page_config(layout="wide")

#Sidebar
with st.sidebar:
    st.title(":hammer_and_pick: Paramètres")
    st.markdown("<br />", unsafe_allow_html=True)

    #slider year element
    current_year = st.slider("Année",min_value=years.min(),max_value=years.max(),value=years.min())
    st.divider()

    #Magnitude
    current_magnitude = st.select_slider("Magnitude", options=[5,6,7,8,9,10], value=(5,10))
    st.divider()

    #Pays
    selected_country = st.selectbox('Pays',countries)
    st.divider()

    #Type
    st.markdown("<span style='font-size:16px;'>Type</span>", unsafe_allow_html=True)
    cb_type_ground = st.checkbox("Terrestre", value=True)
    cb_type_water = st.checkbox("Sous-marin", value=True)

    #crédits
    st.divider()
    st.caption(" *_**Significatifs**_ : Tremblements de terre d'une magnitude supérieure ou égale à 5.")
    st.write("Données : [Kaggle](https://www.kaggle.com/datasets/usgs/earthquake-database)")
    st.divider()
    st.subheader(":computer: Réalisé par [:orange[Damien Rollot]](https://www.linkedin.com/in/damien-rollot/)")
    

st.header(':volcano: Tremblements de terre _significatifs_* dans le monde de 1965 à 2016', divider="grey")

st.subheader('Tremblements de terre en :orange[' + str(current_year) + "]", divider=False)
st.markdown("<br />",unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

#Filter country logic
if selected_country == "TOUS" :
    country_filter = ""
else :
    country_filter = " & Loc_flag_country == '" + selected_country + "'"

#Filter type earthquake logic
if cb_type_ground and cb_type_water :
    type_filter = ""
elif cb_type_ground :
    type_filter = " & Type_ew == 'ground'"
elif cb_type_water :
    type_filter = " & Type_ew == 'water'"
else :
    type_filter = " & Type_ew == ''"


df_filtered = df.query(
    "year == " + str(current_year) + " & " +
    "Magnitude >= " + str(current_magnitude[0]) + " & " + "Magnitude <= " + str(current_magnitude[1]) + 
    type_filter +
    country_filter
)

#dataframe element
with col1 :
    st.dataframe(
        df_filtered[["Loc_flag_country","Date","Time","Magnitude"]],
        column_config={
            "Loc_flag_country" : st.column_config.TextColumn(
                "Pays / Océan",
            ),
            "Date" : st.column_config.DatetimeColumn(
                "Date",
                format="DD-MM-YYYY",
            ),
            "Time" : st.column_config.DatetimeColumn(
                "Heure",
                format="hh:mm:ss"
            ),
        },
        hide_index=True,
        height=510,
        use_container_width=True,
    )


#map element
cmap = plt.get_cmap('Reds')
#cmap = plt.get_cmap('Wistia')

m = folium.Map(zoom_start=1)

for i in range(0,len(df_filtered)):

    tooltip = "<div align='center'>"+ str(df_filtered.iloc[i]["Loc_flag_country"]) + "</div>"
    tooltip = tooltip + "<hr style='margin-top:2px'>"
    tooltip = tooltip + "- Magnitude : <b>" + str(df_filtered.iloc[i]['Magnitude']) + "</b><br/>"
    tooltip = tooltip + "- Date : <b>" + str(df_filtered.iloc[i]['Date'].strftime("%d/%m/%Y")) + " " + str(df_filtered.iloc[i]['Time']) + "</b><br/>"
    tooltip = tooltip + "- Profondeur : <b>" + str(df_filtered.iloc[i]['Depth']) + "</b><br/>"

    if df_filtered.iloc[i]['Type_ew'] != "water":
        tooltip = tooltip + "<br>- Localité : <b>" + str(df_filtered.iloc[i]['Loc_name']) + "</b><br/>"


    magn = df_filtered.iloc[i]['Magnitude']
    col = cmap(interp(magn,[5,7.5,10],[0,0.5,1]))
    col = mpl.colors.rgb2hex(col)
    tooltip = tooltip

    folium.CircleMarker(
        location=[
            df_filtered.iloc[i]['Latitude'], 
            df_filtered.iloc[i]['Longitude']
        ],
        radius=magn*0.80,
        color="#757070",
        fill_color=col,
        fill_opacity=0.9,
        weight=1,
        tooltip=tooltip
   ).add_to(m)

# call to render Folium map in Streamlit
with col2:
    st_data = st_folium(m, width=825, height=510)
    map_zoom_level = st_data["zoom"]

    st.caption(":information_source: Zoomer, passez votre souris sur les :orange[points] pour plus de détails.")

st.divider()

#=============Style=============
st.markdown("""
        <style>
            
            .css-z5fcl4 {
                padding-top:2rem;
            }
            .css-10oheav {
                padding-top:2rem;
            }
            .css-5rimss hr {
               margin: 1em 0; 
            }
            .css-ue6h4q p {
                font-size:16px;
            }
        </style>
        """, unsafe_allow_html=True)