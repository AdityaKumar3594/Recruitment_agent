import streamlit as st
import pandas as pd
import base64
import io
import matplotlib.pyplot as plt

def setup_page():
    apply_custom_css()
    st.markdown("""<script> document.addEventListener('DOMContentLoaded', function() {
                var logoImg = document.querySelector('img[alt="Streamlit"]');
                if (logoImg) {
                    logoImg.src = 'https://example.com/custom_logo.png';
                    logoImg.style.width = '150px';
        }<script/>""")