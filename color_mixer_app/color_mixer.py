import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import colorspacious as cs
import json
import datetime
import base64
import matplotlib.colors as mcolors

def calculate_mixed_color(paints, ratios, strengths):
    adjusted_ratios = np.array(ratios) * np.array(strengths)
    total_ratio = np.sum(adjusted_ratios)
    weights = adjusted_ratios / total_ratio

    L_mix = np.sum(weights * np.array([paint['L'] for paint in paints]))
    a_mix = np.sum(weights * np.array([paint['a'] for paint in paints]))
    b_mix = np.sum(weights * np.array([paint['b'] for paint in paints]))

    return L_mix, a_mix, b_mix, weights

def lab_to_rgb(L, a, b):
    lab_color = np.array([L, a, b])
    rgb_color = cs.cspace_convert(lab_color, "CIELab", "sRGB1")
    return np.clip(rgb_color, 0, 1)

def rgb_to_hex(rgb):
    return "Hex : "+ mcolors.to_hex(rgb)

def create_download_link(data, filename):
    json_data = json.dumps(data, indent=4)
    b64 = base64.b64encode(json_data.encode()).decode()
    href = f'<a href="data:file/json;base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

st.title("Color Mixer")

num_paints = st.sidebar.selectbox("Select number of paints (2-6)", range(2, 7))

paints = []
ratios = []
strengths = []

tabs = st.sidebar.tabs([f"Paint {i+1}" for i in range(num_paints)])

for i, tab in enumerate(tabs):
    with tab:
        paint = {
            'L': st.slider(f"L__{i+1}", 0, 100, 50),
            'a': st.slider(f"a__{i+1}", -128, 127, 0),
            'b': st.slider(f"b__{i+1}", -128, 127, 0)
        }
        ratio = st.slider(f"Ratio__{i+1}", 1, 10, 1)
        strength = st.slider(f"Strength__{i+1}", 0.1, 1.0, 1.0, step=0.1)
        
        paints.append(paint)
        ratios.append(ratio)
        strengths.append(strength)

L_mix, a_mix, b_mix, weights = calculate_mixed_color(paints, ratios, strengths)
mixed_color_rgb = lab_to_rgb(L_mix, a_mix, b_mix)
mixed_color_hex = rgb_to_hex(mixed_color_rgb)

input_colors_rgb = [lab_to_rgb(paint['L'], paint['a'], paint['b']) for paint in paints]
input_colors_hex = [rgb_to_hex(rgb) for rgb in input_colors_rgb]

input_colors_labels = [f'Paint {i+1}' for i in range(len(paints))]
input_colors_labels.append('Mixed Color')

lab_values = [f"Lab({paint['L']}, {paint['a']}, {paint['b']})" for paint in paints]
lab_values.append(f"Lab({L_mix:.2f}, {a_mix:.2f}, {b_mix:.2f})")

rgb_values = [f"RGB({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)})" for rgb in input_colors_rgb]
rgb_values.append(f"RGB({int(mixed_color_rgb[0]*255)}, {int(mixed_color_rgb[1]*255)}, {int(mixed_color_rgb[2]*255)})")

hex_values = input_colors_hex + [mixed_color_hex]

ratio_strength_labels = [f"R: {ratios[i]}  S: {strengths[i]:.1f}" for i in range(num_paints)]
ratio_strength_labels.append("")

max_ratio = 10
max_height = 500
normalized_heights = [(ratio / max_ratio) * max_height for ratio in ratios]

fig, ax = plt.subplots(1, 1, figsize=(9, 7.5), dpi=100)

bar_width = 100
total_bars = num_paints + 1
total_gap_width = 900 - (total_bars * bar_width)
gap_width = total_gap_width / (total_bars + 1)

left_offset = gap_width

for i, color in enumerate(input_colors_rgb + [mixed_color_rgb]):
    if i < num_paints:
        bar_height = normalized_heights[i]
    else:
        bar_height = max_height

    ax.bar(left_offset, bar_height, color=color, edgecolor='black', width=bar_width, align='edge')
    ax.text(left_offset, bar_height + 10, input_colors_labels[i], ha='left', va='bottom', fontsize=12)

    ax.text(left_offset, -20, lab_values[i], ha='left', va='top', fontsize=8, rotation=0)
    ax.text(left_offset, -35, rgb_values[i], ha='left', va='top', fontsize=8, rotation=0)
    ax.text(left_offset, -50, hex_values[i], ha='left', va='top', fontsize=8, rotation=0)
    ax.text(left_offset, -65, ratio_strength_labels[i], ha='left', va='top', fontsize=8, rotation=0)

    left_offset += bar_width + gap_width

ax.set_xlim(0, 900)
ax.set_ylim(-100, 550)
ax.set_xticks([])
ax.set_yticks([])
plt.title('Input and Mixed Colors', fontsize=14, pad=20)
plt.tight_layout()

st.pyplot(fig, use_container_width=True)

# Prepare data for export
data_to_save = {
    "number_of_colors": num_paints,
    "input_colors": [
        {
            "Lab": f"Lab({paint['L']}, {paint['a']}, {paint['b']})",
            "RGB": rgb_values[i],
            "HEX": hex_values[i],
            "ratio": ratios[i],
            "strength": strengths[i]
        }
        for i, paint in enumerate(paints)
    ],
    "mixed_color": {
        "Lab": f"Lab({L_mix:.2f}, {a_mix:.2f}, {b_mix:.2f})",
        "RGB": rgb_values[-1],
        "HEX": hex_values[-1]
    }
}

if st.sidebar.button("Save to JSON"):
    now = datetime.datetime.now().strftime("%y%m%d%H%M%S")
    filename = f"colorMix_{now}.json"
    href = create_download_link(data_to_save, filename)
    st.sidebar.markdown(href, unsafe_allow_html=True)
