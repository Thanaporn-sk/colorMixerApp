import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import json
import datetime

def mix_paints(available_paints, desired_color):
    num_paints = len(available_paints)
    available_paints = np.array(available_paints, dtype=float)
    desired_color = np.array(desired_color, dtype=float)
    desired_color_normalized = desired_color / num_paints
    differences = available_paints - desired_color_normalized
    proportions = np.linalg.lstsq(available_paints.T, desired_color, rcond=None)[0]
    proportions = proportions / proportions.sum()
    return proportions.tolist()

# Function to display color as RGB and Hex
def display_color_info(color):
    hex_color = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
    return f"RGB: {color}  |  Hex: {hex_color}"

# Function to get CSS for color display
def get_color_display_css(color):
    return f'<div style="background-color:rgb{color}; width: 50px; height: 50px; border: 1px solid #000;"></div>'

# Streamlit app
st.title('Paint Mixer')

# Sidebar for inputs
with st.sidebar:
    st.write("### Desired Color")
    col1, col2, col3 = st.columns(3)
    with col1:
        desired_r = st.slider('Red', 0, 255, 128, key='desired_r')
    with col2:
        desired_g = st.slider('Green', 0, 255, 128, key='desired_g')
    with col3:
        desired_b = st.slider('Blue', 0, 255, 128, key='desired_b')
    desired_color = (desired_r, desired_g, desired_b)
    hex_color = "#{:02x}{:02x}{:02x}".format(desired_r, desired_g, desired_b)
    st.markdown(f'<div style="background-color:{hex_color}; width: 50px; height: 50px; border: 1px solid #000; margin-top: 10px;"></div>', unsafe_allow_html=True)
    st.write(display_color_info(desired_color))

    st.write("### Paint Colors")
    
    # Session state for storing colors
    if 'colors' not in st.session_state:
        st.session_state.colors = [(255, 0, 0), (0, 255, 0)]  # Initial colors: Red and Green

    # Display color inputs
    for idx, color in enumerate(st.session_state.colors):
        st.write(f"**Paint {idx+1}**")
        col1, col2, col3 = st.columns(3)
        with col1:
            r = st.slider(f'Red {idx+1}', 0, 255, color[0], key=f'r{idx}')
        with col2:
            g = st.slider(f'Green {idx+1}', 0, 255, color[1], key=f'g{idx}')
        with col3:
            b = st.slider(f'Blue {idx+1}', 0, 255, color[2], key=f'b{idx}')
        st.session_state.colors[idx] = (r, g, b)

        # Display color info (RGB and Hex)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(get_color_display_css((r, g, b)), unsafe_allow_html=True)
        with col2:
            st.write(f"RGB: ({r}, {g}, {b})")
        with col3:
            hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
            st.write(f"Hex: {hex_color}")
        with col4:
            if len(st.session_state.colors) > 2 and st.button('Remove', key=f'remove_{idx}'):
                st.session_state.colors.pop(idx)
                st.experimental_rerun()

    # Add color button
    if st.button('Add Color'):
        st.session_state.colors.append((0, 0, 0))  # Add a new black color
        st.experimental_rerun()

    # Calculate proportions
    proportions = mix_paints(st.session_state.colors, desired_color)

    # Update the session state with the latest desired color
    st.session_state.desired_color = desired_color

    # Save button to download proportions as JSON
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    if st.download_button('Download Proportions as JSON', json.dumps({
        "Desired Color": {
            "Desired Color": "Desired Color",
            "RGB": desired_color,
            "HEX": "#{:02x}{:02x}{:02x}".format(desired_color[0], desired_color[1], desired_color[2])
        },
        "proportions": [
            {
                "Paint": f'Paint {i+1}',
                "RGB": st.session_state.colors[i],
                "HEX": "#{:02x}{:02x}{:02x}".format(st.session_state.colors[i][0], st.session_state.colors[i][1], st.session_state.colors[i][2]),
                "Proportion (%)": proportions[i] * 100
            } for i in range(len(st.session_state.colors))
        ]
    }), file_name=f'MixingApp{timestamp}.json', mime='application/json'):
        st.success(f'Proportions saved to MixingApp{timestamp}.json')

# Right-side table for Desired Color information
st.write("## Desired Color Information")
desired_rgb_str = f"RGB: ({desired_color[0]}, {desired_color[1]}, {desired_color[2]})"
desired_hex_str = "#{:02x}{:02x}{:02x}".format(desired_color[0], desired_color[1], desired_color[2])
desired_display_str = f'<div style="background-color:rgb{desired_color}; width: 50px; height: 50px; border: 1px solid #000;"></div>'
desired_table_data = pd.DataFrame({
    'RGB': [desired_rgb_str],
    'Hex': [desired_hex_str],
    'Display Color': [desired_display_str]
})
st.write(desired_table_data.to_html(escape=False, index=False), unsafe_allow_html=True)

# Prepare data for proportions table
table_data = []
for i, prop in enumerate(proportions):
    color = st.session_state.colors[i]
    rgb_str = f"RGB: ({color[0]}, {color[1]}, {color[2]})"
    hex_str = "#{:02x}{:02x}{:02x}".format(color[0], color[1], color[2])
    table_data.append({
        'Color': f'Paint {i+1}',
        'RGB': rgb_str,
        'HEX': hex_str,
        'Display': f'<div style="background-color:{hex_str}; width: 50px; height: 50px; border: 1px solid #000;"></div>',
        'Proportion (%)': prop * 100
    })

df_proportions = pd.DataFrame(table_data)

# Display proportions
st.write("## Proportions")
st.write(df_proportions.to_html(escape=False, index=False), unsafe_allow_html=True)

# Plot proportions with consistent colors
fig = go.Figure(data=[go.Pie(labels=df_proportions['Color'], values=proportions, hole=.3,
                             marker=dict(colors=[f'rgb{color}' for color in st.session_state.colors]))])
st.plotly_chart(fig)
