import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Excel to Header Generator")

st.title("📄 Excel to Header File Generator")

# --- Function to align columns and apply custom header format ---
def format_header(data: pd.DataFrame, raw_data: pd.DataFrame, comment_col: str = None) -> str:
    data = data.fillna("nan")
    col_widths = [max(data[col].astype(str).map(len).max(), len(str(col))) for col in data.columns]
    lines = []
    for _, row in data.iterrows():
        row_values = [str(row[col]).ljust(col_widths[i]) for i, col in enumerate(data.columns)]
        comment = f" // {raw_data.loc[row.name, comment_col]}" if comment_col else ""
        if len(row_values) >= 3:
            formatted = f"{{{row_values[0]} , {{{', '.join(row_values[1:])}}}}},{comment}"
        else:
            formatted = f"{{{', '.join(row_values)}}},{comment}"
        lines.append(formatted)
    return '\n'.join(lines)

# --- Upload Excel file ---
uploaded_file = st.file_uploader("Upload Excel file (.xlsx)", type="xlsx")

if uploaded_file:
    try:
        df_raw = pd.read_excel(uploaded_file, header=4)
        st.success("✅ Excel file loaded successfully!")

        columns = df_raw.columns.tolist()

        st.markdown("---")
        st.subheader("1️⃣ Select Columns")

        selected_columns = st.multiselect("Select columns to include in output:", options=columns)

        if selected_columns:
            if ("column_order" not in st.session_state or
                set(st.session_state.column_order) != set(selected_columns)):
                st.session_state.column_order = selected_columns.copy()
                st.session_state.selected_column = st.session_state.column_order[0]

            st.markdown("---")
            st.subheader("2️⃣ Reorder Selected Columns")

            col1, col2 = st.columns([3, 1])

            selected = col1.selectbox(
                "Select a column to move:",
                options=st.session_state.column_order,
                index=st.session_state.column_order.index(st.session_state.selected_column)
            )

            idx = st.session_state.column_order.index(selected)
            up_disabled = idx == 0
            down_disabled = idx == len(st.session_state.column_order) - 1

            if col2.button("↑ Move Up") and not up_disabled:
                st.session_state.column_order[idx - 1], st.session_state.column_order[idx] = (
                    st.session_state.column_order[idx], st.session_state.column_order[idx - 1]
                )
                st.session_state.selected_column = st.session_state.column_order[idx - 1]

            if col2.button("↓ Move Down") and not down_disabled:
                st.session_state.column_order[idx + 1], st.session_state.column_order[idx] = (
                    st.session_state.column_order[idx], st.session_state.column_order[idx + 1]
                )
                st.session_state.selected_column = st.session_state.column_order[idx + 1]

            st.write("Current Order:")
            st.write(st.session_state.column_order)

            df_selected = df_raw[st.session_state.column_order]

            st.markdown("---")
            st.subheader("3️⃣ Select Comment Column (optional)")
            comment_col = st.selectbox("Select column to be used as comment: (Optional)", ["None"] + columns)
            comment_col = None if comment_col == "None" else comment_col

            st.markdown("---")
            st.subheader("4️⃣ Output")

            filename = st.text_input("Output file name (with .h extension):", value="output_gpio.h")

            if st.button("🚀 Generate Header File"):
                header_output = format_header(df_selected, df_raw, comment_col)
                st.code(header_output, language="c")

                buffer = io.StringIO()
                buffer.write(header_output)
                buffer.seek(0)

                st.download_button(
                    label="📥 Download Header File",
                    data=buffer,
                    file_name=filename,
                    mime="text/plain"
                )

    except Exception as e:
        st.error(f"❌ Failed to read Excel file: {e}")
