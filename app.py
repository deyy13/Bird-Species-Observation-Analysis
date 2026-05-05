import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title='Bird Species Analysis', layout='wide')
st.title('Bird Species Observation Analysis')
st.markdown('**Forest & Grassland Monitoring — 11 Admin Units | 2018**')

@st.cache_data
def load_data():
    df = pd.read_csv('Bird_Cleaned_Dataset.csv', parse_dates=['Date'])
    return df

df = load_data()

# ── Sidebar Filters ──
st.sidebar.header('Filters')
habitat     = st.sidebar.multiselect('Habitat', df['Location_Type'].unique(), default=list(df['Location_Type'].unique()))
admin_units = st.sidebar.multiselect('Admin Unit', sorted(df['Admin_Unit_Code'].unique()), default=list(df['Admin_Unit_Code'].unique()))
watchlist   = st.sidebar.checkbox('Watchlist species only', value=False)

fdf = df[df['Location_Type'].isin(habitat) & df['Admin_Unit_Code'].isin(admin_units)]
if watchlist:
    fdf = fdf[fdf['PIF_Watchlist_Status'] == True]

# ── KPI Metrics ──
col1, col2, col3, col4 = st.columns(4)
col1.metric('Total Observations', f"{len(fdf):,}")
col2.metric('Unique Species',     fdf['Scientific_Name'].nunique())
col3.metric('Admin Units',        fdf['Admin_Unit_Code'].nunique())
col4.metric('Watchlist Species',  fdf[fdf['PIF_Watchlist_Status']==True]['Scientific_Name'].nunique())

st.markdown('---')
tab1, tab2, tab3, tab4, tab5 = st.tabs(['Temporal','Spatial','Species','Environment','Distance'])

# Tab 1: Temporal
with tab1:
    st.subheader('Observations by Month')
    monthly = fdf.groupby(['Month','Location_Type']).size().reset_index(name='Count')
    fig = px.bar(monthly, x='Month', y='Count', color='Location_Type', barmode='group',
                 color_discrete_map={"Forest":"#2E8B57","Grassland":"#DAA520"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader('Activity by Hour of Day')
    fdf2 = fdf.copy()
    fdf2['Hour'] = fdf2['Start_Time'].str.split(':').str[0].astype(float)
    hourly = fdf2.groupby(['Hour','Location_Type']).size().reset_index(name='Count').dropna()
    fig2 = px.line(hourly, x='Hour', y='Count', color='Location_Type', markers=True,
                   color_discrete_map={"Forest":"#2E8B57","Grassland":"#DAA520"})
    st.plotly_chart(fig2, use_container_width=True)

# Tab 2: Spatial
with tab2:
    st.subheader('Species Diversity by Admin Unit')
    admin_div = fdf.groupby(['Admin_Unit_Code','Location_Type'])['Scientific_Name'].nunique().reset_index(name='Unique_Species')
    fig = px.bar(admin_div, x='Admin_Unit_Code', y='Unique_Species', color='Location_Type', barmode='group',
                 color_discrete_map={"Forest":"#2E8B57","Grassland":"#DAA520"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader('Top 15 Hotspot Plots')
    hotspots = fdf.groupby(['Plot_Name','Location_Type'])['Scientific_Name'].nunique().reset_index(name='Unique_Species')
    hotspots = hotspots.sort_values('Unique_Species', ascending=False).head(15)
    fig2 = px.bar(hotspots, x='Plot_Name', y='Unique_Species', color='Location_Type',
                  color_discrete_map={"Forest":"#2E8B57","Grassland":"#DAA520"})
    fig2.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)

# Tab 3: Species
with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Top Species — Forest')
        top_f = fdf[fdf['Location_Type']=="Forest"]['Common_Name'].value_counts().head(10).reset_index()
        top_f.columns = ['Species','Count']
        fig = px.bar(top_f, x='Count', y='Species', orientation='h', color_discrete_sequence=['#2E8B57'])
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader('Top Species — Grassland')
        top_g = fdf[fdf['Location_Type']=="Grassland"]['Common_Name'].value_counts().head(10).reset_index()
        top_g.columns = ['Species','Count']
        fig2 = px.bar(top_g, x='Count', y='Species', orientation='h', color_discrete_sequence=['#DAA520'])
        fig2.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader('ID Method Distribution')
    fig3 = px.pie(fdf, names='ID_Method', color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader('Watchlist Species')
    wl = fdf[fdf['PIF_Watchlist_Status']==True].groupby('Common_Name').size().reset_index(name='Count').sort_values('Count',ascending=False)
    fig4 = px.bar(wl, x='Common_Name', y='Count', color='Count', color_continuous_scale='Reds')
    fig4.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig4, use_container_width=True)

# Tab 4: Environment
with tab4:
    st.subheader('Temperature vs Humidity')
    fig = px.scatter(fdf.dropna(subset=['Temperature']), x='Temperature', y='Humidity',
                     color='Location_Type', opacity=0.5,
                     color_discrete_map={"Forest":"#2E8B57","Grassland":"#DAA520"})
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Sky Condition')
        sky = fdf.groupby('Sky').size().reset_index(name='Count')
        fig2 = px.bar(sky, x='Sky', y='Count', color_discrete_sequence=['#5B9BD5'])
        fig2.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        st.subheader('Disturbance Effect')
        dist = fdf.groupby('Disturbance').size().reset_index(name='Count')
        fig3 = px.bar(dist, x='Disturbance', y='Count', color_discrete_sequence=['#ED7D31'])
        fig3.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(fig3, use_container_width=True)

# Tab 5: Distance
with tab5:
    st.subheader('Distance Distribution')
    dist_df = fdf.groupby(['Distance','Location_Type']).size().reset_index(name='Count')
    fig = px.bar(dist_df, x='Distance', y='Count', color='Location_Type', barmode='group',
                 color_discrete_map={"Forest":"#2E8B57","Grassland":"#DAA520"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader('Flyover vs Non-Flyover')
    fly = fdf.copy()
    fly['Flyover'] = fly['Flyover_Observed'].map({True:'Flyover',False:'Not Flyover'})
    fly_cnt = fly.groupby(['Location_Type','Flyover']).size().reset_index(name='Count')
    fig2 = px.bar(fly_cnt, x='Location_Type', y='Count', color='Flyover', barmode='stack',
                  color_discrete_map={'Flyover':'#E74C3C','Not Flyover':'#3498DB'})
    st.plotly_chart(fig2, use_container_width=True)

st.markdown('---')
st.caption('Bird Species Observation Analysis | Data: NCRN Bird Monitoring 2018')
