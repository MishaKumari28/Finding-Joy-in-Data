import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import streamlit as st
import time
import base64
import numpy as np
df=pd.read_csv("cleandata.csv")
st.set_page_config(page_title="Happiness App", layout="wide")

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def get_base64(file_path):
    with open(file_path, "rb") as file:
        encoded = base64.b64encode(file.read()).decode()
    return encoded
img_base64 = get_base64("background_img.jpg")  


st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{img_base64}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    </style>
    """,
    unsafe_allow_html=True)
st.markdown(
    "<h1 style='text-align: center;'>Finding Joy in Data!!!... 😊</h1>",
    unsafe_allow_html=True
)

# --- SIDEBAR FILTERS ---
st.sidebar.header("Filters")
all_countries = sorted(df["Country"].dropna().unique())
selected_countries = st.sidebar.multiselect("Select Countries (leave empty for All)", all_countries)

min_poverty, max_poverty = int(df["Poverty_Rate(%)  "].min()), int(df["Poverty_Rate(%)  "].max())
poverty_rate_filter = st.sidebar.slider("Poverty Rate (%)", min_poverty, max_poverty, (min_poverty, max_poverty))

min_literacy, max_literacy = int(df["Literacy_Rate(%)"].min()), int(df["Literacy_Rate(%)"].max())
literacy_rate_filter = st.sidebar.slider("Literacy Rate (%)", min_literacy, max_literacy, (min_literacy, max_literacy))

filtered_df = df[
    (df["Poverty_Rate(%)  "].between(poverty_rate_filter[0], poverty_rate_filter[1])) &
    (df["Literacy_Rate(%)"].between(literacy_rate_filter[0], literacy_rate_filter[1]))
]

if selected_countries:
    filtered_df = filtered_df[filtered_df["Country"].isin(selected_countries)]


# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 Analysis", "📄 Data"])

# Display a message if the dataframe is empty after filtering
if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust the sidebar filters.")
else:
    with tab1:
        st.markdown(
            "<h2 style=' color: #4CAF50;'>📊 Summary Statistics</h2>",
            unsafe_allow_html=True
        )
        
        # If a single country is selected, show its specific metrics
        if len(selected_countries) == 1:
            country_data = filtered_df.iloc[0]
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Literacy Rate", f"{country_data['Literacy_Rate(%)']:.2f} %")
            col2.metric("Unemployment Rate", f"{country_data['Unemployment_Rate(%)']:.2f} %")
            col3.metric("Poverty Rate", f"{country_data['Poverty_Rate(%)  ']:.2f} %")
            col4.metric("Happiness Score", f"{country_data['Happiness_Score']:.2f}")

        # If multiple or no countries are selected, show average metrics
        else:
            col1, col2, col3 = st.columns(3)  
            col1.metric("AVG. Literacy Rate", f"{filtered_df['Literacy_Rate(%)'].mean():.2f} %")
            col2.metric("AVG. Unemployment Rate", f"{filtered_df['Unemployment_Rate(%)'].mean():.2f} %")
            col3.metric("AVG. Poverty Rate", f"{filtered_df['Poverty_Rate(%)  '].mean():.2f} %")

        # --- DYNAMIC BAR CHART ---
        st.subheader("📊 Country Rankings")
        rankable_metrics = ['Literacy_Rate(%)', 'GDP_per_Capita_USD', 'Unemployment_Rate(%)', 'Poverty_Rate(%)  ', 'Happiness_Score']
        selected_metric = st.selectbox("Select a metric to rank countries by:", rankable_metrics)
        
        chart_df = filtered_df.sort_values(selected_metric, ascending=False)
        # Limit to top 10 only if no specific countries are selected
        if not selected_countries:
            chart_df = chart_df.head(10)
        
        st.bar_chart(chart_df.set_index("Country")[selected_metric])

        # --- PIE CHART ---
        # Only show the pie chart if we are comparing countries
        if len(selected_countries) != 1:
            st.subheader("🚫💰 Poverty Rate Breakdown")
            pie_df = filtered_df
            title = "Poverty Rate for Selected Countries"
            if not selected_countries:
                 pie_df = filtered_df.sort_values("Poverty_Rate(%)  ", ascending=False).head(5)
                 title = "Top 5 Countries with Highest Poverty Rate"

            fig, ax = plt.subplots(figsize=(3, 3), facecolor='none')
            ax.set_facecolor("none") 
            ax.pie(
                pie_df["Poverty_Rate(%)  "],
                labels=pie_df["Country"],  
                autopct='%1.1f%%',
                startangle=140,
                colors=plt.cm.Pastel1.colors,
                textprops={'color': "white"}
            )
            ax.set_title(title, color="silver", fontsize=8)
            st.pyplot(fig)


    with tab2:
        st.subheader("🔍 Interactive Scatter Plot")
        numeric_cols = filtered_df.select_dtypes(include=np.number).columns.tolist()
        
        default_x = "GDP_per_Capita_USD" if "GDP_per_Capita_USD" in numeric_cols else numeric_cols[0]
        default_y = "Happiness_Score" if "Happiness_Score" in numeric_cols else numeric_cols[1]
        
        col1, col2 = st.columns(2)
        with col1:
            x_axis = st.selectbox("Select X-axis", numeric_cols, index=numeric_cols.index(default_x))
        with col2:
            y_axis = st.selectbox("Select Y-axis", numeric_cols, index=numeric_cols.index(default_y))
            
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(filtered_df[x_axis], filtered_df[y_axis], alpha=0.7)
        ax.set_xlabel(x_axis)
        ax.set_ylabel(y_axis)
        ax.set_title(f"{y_axis} vs. {x_axis}")
        st.pyplot(fig)

        st.subheader("Correlation Heatmap")
        # Ensure there's more than one row for correlation
        if len(filtered_df) > 1:
            numeric_cols = filtered_df.select_dtypes(include=np.number)
            corr = numeric_cols.corr()
            
            fig, ax = plt.subplots(figsize=(12, 10))
            sb.heatmap(corr, annot=True, cmap='viridis', ax=ax, fmt='.2f', annot_kws={"size": 8})
            ax.set_title("Correlation Matrix of Numeric Features")
            plt.xticks(rotation=45, ha='right')
            plt.yticks(rotation=0)
            st.pyplot(fig)
        else:
            st.write("Correlation heatmap requires at least two data points. Please select more countries.")


    with tab3:
        st.subheader("Filtered Data")
        st.dataframe(filtered_df)
        csv = convert_df_to_csv(filtered_df)
        st.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='filtered_data.csv',
            mime='text/csv',
        )
