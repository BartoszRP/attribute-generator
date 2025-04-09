import streamlit as st
import pandas as pd
import itertools
from io import BytesIO

st.title("🔧 Attribute Combination Generator")

st.markdown("### 🧩 Enter values for each attribute (separated by commas):")

# Session state for dynamic fields
if "num_fields" not in st.session_state:
    st.session_state.num_fields = 3  # default number of fields

# Buttons to add/remove attribute fields
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("➕ Add Attribute"):
        st.session_state.num_fields += 1
with col2:
    if st.button("➖ Remove Last Attribute") and st.session_state.num_fields > 1:
        st.session_state.num_fields -= 1

# Input for each dynamic attribute
user_inputs = {}
for i in range(1, st.session_state.num_fields + 1):
    field_name = f"Attribute {i}"
    values = st.text_input(f"{field_name}:", key=field_name)
    if values.strip():  # ignore empty inputs
        user_inputs[field_name] = [v.strip() for v in values.split(",") if v.strip()]

# Input for prefix
prefix = st.text_input("Prefix for RESULT column (e.g. BSB, ID, Code):", value="BSB")

# Initialize result DataFrame
if "result_df" not in st.session_state:
    st.session_state.result_df = None

# Generate combinations
if st.button("▶️ Generate combinations"):
    if user_inputs:
        columns = list(user_inputs.keys())
        value_lists = list(user_inputs.values())

        combinations = list(itertools.product(*value_lists))
        result_df = pd.DataFrame(combinations, columns=columns)

        if prefix.strip():
            result_df["RESULT"] = (
                prefix.strip()
                + "-"
                + result_df[columns].astype(str).agg("-".join, axis=1)
            )
        else:
            result_df["RESULT"] = result_df[columns].astype(str).agg("-".join, axis=1)

        st.session_state.result_df = result_df
        st.success(f"{len(result_df)} combinations generated.")
        st.dataframe(result_df)
    else:
        st.warning("Please enter at least one attribute with values.")

# Download Excel button
if st.session_state.result_df is not None:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        st.session_state.result_df.to_excel(writer, index=False)
    output.seek(0)

    st.download_button(
        label="💾 Download as Excel",
        data=output,
        file_name="attribute_combinations.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
