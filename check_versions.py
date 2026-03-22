import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

print(f"Streamlit version: {st.__version__}")
print(f"Folium version: {folium.__version__}")
# Try to get streamlit-folium version if possible
try:
    import streamlit_folium
    print(f"streamlit-folium version: {streamlit_folium.__version__}")
except AttributeError:
    print("streamlit-folium version not found via __version__")

# Test if we can create a map
m = folium.Map(location=[-10.913, -37.052], zoom_start=15)
print("Folium map object created successfully")
