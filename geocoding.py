import pandas as pd
import pydeck as pdk
import streamlit as st
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from database import engine

# geocoding.py

def get_branch_locations():
    query = """
    SELECT ba.BranchID, b.Name as BranchName, ba.Street, ba.City, ba.State, ba.ZipCode, ba.Country
    FROM branchaddress ba
    JOIN branch b ON ba.BranchID = b.BranchID
    """
    with engine.connect() as conn:
        data = pd.read_sql(query, conn)
    return data

def geocode_addresses(addresses_df):
    geolocator = Nominatim(user_agent="branch_locator")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    addresses_df['FullAddress'] = (
        addresses_df['Street'] + ', ' +
        addresses_df['City'] + ', ' +
        addresses_df['State'] + ', ' +
        addresses_df['Country']
    )
    addresses_df['Location'] = addresses_df['FullAddress'].apply(geocode)
    addresses_df['Latitude'] = addresses_df['Location'].apply(lambda loc: loc.latitude if loc else None)
    addresses_df['Longitude'] = addresses_df['Location'].apply(lambda loc: loc.longitude if loc else None)
    addresses_df = addresses_df.dropna(subset=['Latitude', 'Longitude'])
    addresses_df = addresses_df.drop(columns=['Location'])
    return addresses_df

def plot_branch_locations():
    addresses_df = get_branch_locations()
    addresses_df = geocode_addresses(addresses_df)
    if addresses_df.empty:
        st.warning("No branch locations available to display.")
    else:
        # Define the tooltip
        tooltip = {
            "html": "<b>Branch Name:</b> {BranchName}<br/>"
                    "<b>Address:</b> {FullAddress}",
            "style": {"backgroundColor": "steelblue", "color": "white", "zIndex": "1000"}
        }
        # Create the layer with pickable=True
        layer = pdk.Layer(
            'ScatterplotLayer',
            data=addresses_df,
            get_position='[Longitude, Latitude]',
            get_color='[200, 30, 0, 160]',
            get_radius=5000,
            pickable=True,
            auto_highlight=True,
        )
        view_state = pdk.ViewState(
            latitude=addresses_df['Latitude'].mean(),
            longitude=addresses_df['Longitude'].mean(),
            zoom=6,
            pitch=0,
        )
        r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip)
        st.pydeck_chart(r)


