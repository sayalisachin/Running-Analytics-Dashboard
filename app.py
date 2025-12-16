import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Running Analytics", 
    page_icon="🏃", 
    layout="wide",
    initial_sidebar_state="auto"
)

st.title("Running Analytics Dashboard 🏃")
st.markdown("Upload a CSV file with running data to view visualizations and summary metrics.")

def validate_csv(df):
    """Validate CSV structure and data types."""
    errors = []
    
    # Check required columns
    required_columns = ['date', 'person', 'miles run']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"❌ Missing required columns: {', '.join(missing_columns)}")
    
    # Check for empty dataframe
    if df.empty:
        errors.append("❌ CSV file is empty")
        return errors
    
    # Validate data types
    if 'date' in df.columns:
        try:
            pd.to_datetime(df['date'])
        except Exception as e:
            errors.append(f"❌ 'date' column must be valid dates (format: YYYY-MM-DD). Error: {str(e)[:100]}")
    
    if 'person' in df.columns:
        if df['person'].isnull().any():
            errors.append("❌ 'person' column contains empty values")
    
    if 'miles run' in df.columns:
        try:
            miles_numeric = pd.to_numeric(df['miles run'], errors='coerce')
            if miles_numeric.isnull().any():
                null_count = miles_numeric.isnull().sum()
                errors.append(f"❌ 'miles run' column has {null_count} non-numeric values")
            elif (miles_numeric < 0).any():
                errors.append("❌ 'miles run' values must be positive numbers")
        except Exception as e:
            errors.append(f"❌ 'miles run' must be numeric. Error: {str(e)[:100]}")
    
    return errors

# File upload
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

# Sidebar controls
with st.sidebar:
    st.header("Filters & Options")
    theme_choice = st.selectbox("Chart Theme", ["plotly", "plotly_dark"], index=0)
    cals_per_mile = st.slider("Calories per mile (estimate)", 50, 200, 100)
    goal_miles = st.number_input("Weekly mileage goal", min_value=0.0, value=20.0, step=1.0)
    est_pace = st.number_input("Fallback pace (min/mile) if time missing", min_value=5.0, max_value=20.0, value=10.0, step=0.1)

if uploaded_file is not None:
    try:
        # Read the CSV
        df = pd.read_csv(uploaded_file)
        
        # Validate CSV
        validation_errors = validate_csv(df)
        
        if validation_errors:
            st.error("**Validation Errors Found:**")
            for error in validation_errors:
                st.error(error)
            st.stop()
        
        # Convert data types
        df['date'] = pd.to_datetime(df['date'])
        df['miles run'] = pd.to_numeric(df['miles run'])
        has_time = 'minutes' in df.columns
        if has_time:
            df['minutes'] = pd.to_numeric(df['minutes'], errors='coerce')
        
        # Sidebar filters
        min_date, max_date = df['date'].min().date(), df['date'].max().date()
        date_range = st.sidebar.date_input("Date range", (min_date, max_date), min_value=min_date, max_value=max_date)
        if isinstance(date_range, tuple):
            start_date, end_date = date_range
        else:  # single selection fallback
            start_date, end_date = min_date, date_range
        persons = sorted(df['person'].unique())
        selected_persons = st.sidebar.multiselect("Runners", persons, default=persons)
        
        # Apply filters
        mask = (
            (df['date'].dt.date >= start_date)
            & (df['date'].dt.date <= end_date)
            & (df['person'].isin(selected_persons))
        )
        df = df.loc[mask].copy()
        if df.empty:
            st.warning("No data after applying filters.")
            st.stop()
        
        # Pace and calories calculations
        if has_time:
            df['pace_min_per_mile'] = df['minutes'] / df['miles run']
        else:
            df['pace_min_per_mile'] = est_pace
            df['minutes'] = df['miles run'] * est_pace
        df['calories'] = df['miles run'] * cals_per_mile
        
        # Display success message
        st.success(f"✅ CSV loaded successfully! ({len(df)} runs, {df['person'].nunique()} runners)")
        
        # Display data preview
        st.subheader("Data Preview (filtered)")
        st.dataframe(df, use_container_width=True)
        
        # ===== OVERALL METRICS =====
        st.subheader("Overall Summary Metrics")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            total_miles = df['miles run'].sum()
            st.metric("Total Miles", f"{total_miles:.1f}")
        
        with col2:
            avg_miles = df['miles run'].mean()
            st.metric("Avg Miles/Run", f"{avg_miles:.2f}")
        
        with col3:
            max_miles = df['miles run'].max()
            st.metric("Max Miles", f"{max_miles:.2f}")
        
        with col4:
            min_miles = df['miles run'].min()
            st.metric("Min Miles", f"{min_miles:.2f}")
        
        with col5:
            num_runs = len(df)
            st.metric("Total Runs", num_runs)
        
        with col6:
            total_cal = df['calories'].sum()
            st.metric("Calories (est)", f"{total_cal:,.0f}")
        
        # Weekly goal tracking
        st.subheader("Goal Tracking (weekly)")
        week_end = df['date'].max().normalize()
        week_start = week_end - timedelta(days=6)
        week_mask = (df['date'] >= week_start) & (df['date'] <= week_end)
        week_miles = df.loc[week_mask, 'miles run'].sum()
        goal_pct = (week_miles / goal_miles * 100) if goal_miles > 0 else 0
        gcol1, gcol2, gcol3 = st.columns(3)
        gcol1.metric("Weekly miles (last 7 days)", f"{week_miles:.1f}")
        gcol2.metric("Goal", f"{goal_miles:.1f}")
        gcol3.metric("Progress", f"{goal_pct:.0f}%")
        st.progress(min(goal_pct / 100, 1.0))
        
        # ===== VISUALIZATIONS =====
        st.subheader("Overall Visualizations")
        
        col_viz1, col_viz2 = st.columns(2)
        
        with col_viz1:
            st.markdown("### Miles Run Over Time by Person")
            fig_time = px.line(
                df.sort_values('date'),
                x='date',
                y='miles run',
                color='person',
                markers=True,
                title="Tracking Progress Over Time",
                template=theme_choice
            )
            fig_time.update_xaxes(title_text="Date")
            fig_time.update_yaxes(title_text="Miles")
            st.plotly_chart(fig_time, use_container_width=True)
        
        with col_viz2:
            st.markdown("### Total Miles by Person")
            miles_by_person = df.groupby('person')['miles run'].sum().sort_values(ascending=False)
            fig_bar = px.bar(
                x=miles_by_person.values,
                y=miles_by_person.index,
                orientation='h',
                title="Cumulative Distance",
                labels={'x': 'Miles', 'y': 'Person'},
                template=theme_choice
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("### Distribution of Miles per Run (Overall)")
        fig_hist = px.histogram(
            df,
            x='miles run',
            nbins=20,
            title="Frequency Distribution",
            labels={'miles run': 'Miles'},
            template=theme_choice
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        
        # Weekly / monthly summaries
        st.subheader("Weekly and Monthly Summaries")
        df['week'] = df['date'].dt.to_period('W').apply(lambda r: r.start_time)
        df['month'] = df['date'].dt.to_period('M').dt.to_timestamp()
        weekly = df.groupby('week')['miles run'].agg(['sum', 'mean']).reset_index()
        monthly = df.groupby('month')['miles run'].agg(['sum', 'mean']).reset_index()
        wcol, mcol = st.columns(2)
        with wcol:
            st.markdown("### Weekly miles")
            fig_week = px.bar(weekly, x='week', y='sum', title="Weekly Total Miles", template=theme_choice, labels={'sum': 'Miles'})
            st.plotly_chart(fig_week, use_container_width=True)
        with mcol:
            st.markdown("### Monthly miles")
            fig_month = px.bar(monthly, x='month', y='sum', title="Monthly Total Miles", template=theme_choice, labels={'sum': 'Miles'})
            st.plotly_chart(fig_month, use_container_width=True)
        
        # ===== PER-PERSON STATISTICS =====
        st.subheader("Per-Person Statistics")
        person_stats = df.groupby('person')['miles run'].agg([
            ('Total Miles', 'sum'),
            ('Average Miles', 'mean'),
            ('Max Miles', 'max'),
            ('Min Miles', 'min'),
            ('Run Count', 'count'),
            ('Calories (est)', 'sum')
        ]).round(2)
        person_stats = person_stats.sort_values('Total Miles', ascending=False)
        st.dataframe(person_stats, use_container_width=True)
        
        # Outlier detection
        st.subheader("Potential Outliers")
        def detect_outliers(group):
            mean = group['miles run'].mean()
            std = group['miles run'].std(ddof=0)
            upper = mean + 2 * std
            lower = max(mean - 2 * std, 0)
            return group[(group['miles run'] > upper) | (group['miles run'] < lower)]
        outliers = df.groupby('person', group_keys=False).apply(detect_outliers)
        if outliers.empty:
            st.info("No distance outliers detected using ±2σ per person.")
        else:
            st.dataframe(outliers[['date', 'person', 'miles run']], use_container_width=True)
        
        # ===== PER-PERSON DETAILED VIEWS =====
        st.subheader("Per-Person Detailed Views")
        unique_persons = sorted(df['person'].unique())
        selected_person = st.selectbox("Select a runner to view details:", unique_persons)
        person_data = df[df['person'] == selected_person].sort_values('date')
        
        if len(person_data) > 0:
            st.markdown(f"### Metrics for {selected_person}")
            p_col1, p_col2, p_col3, p_col4, p_col5 = st.columns(5)
            
            with p_col1:
                p_total = person_data['miles run'].sum()
                st.metric(f"{selected_person} - Total Miles", f"{p_total:.1f}")
            
            with p_col2:
                p_avg = person_data['miles run'].mean()
                st.metric(f"{selected_person} - Avg Miles/Run", f"{p_avg:.2f}")
            
            with p_col3:
                p_max = person_data['miles run'].max()
                st.metric(f"{selected_person} - Best Run", f"{p_max:.2f}")
            
            with p_col4:
                p_min = person_data['miles run'].min()
                st.metric(f"{selected_person} - Shortest Run", f"{p_min:.2f}")
            
            with p_col5:
                p_cal = person_data['calories'].sum()
                st.metric(f"{selected_person} - Calories (est)", f"{p_cal:,.0f}")
            
            p_col_chart1, p_col_chart2 = st.columns(2)
            
            with p_col_chart1:
                st.markdown(f"### {selected_person}'s Progress Over Time")
                fig_person_line = px.line(
                    person_data,
                    x='date',
                    y='miles run',
                    markers=True,
                    title="Daily Miles Run",
                    template=theme_choice
                )
                fig_person_line.update_xaxes(title_text="Date")
                fig_person_line.update_yaxes(title_text="Miles")
                st.plotly_chart(fig_person_line, use_container_width=True)
            
            with p_col_chart2:
                st.markdown(f"### {selected_person}'s Run Distribution")
                fig_person_hist = px.histogram(
                    person_data,
                    x='miles run',
                    nbins=15,
                    title="Distance Frequency",
                    template=theme_choice
                )
                st.plotly_chart(fig_person_hist, use_container_width=True)
            
            st.markdown(f"### {selected_person}'s Run History")
            st.dataframe(person_data[['date', 'miles run', 'pace_min_per_mile', 'calories']].reset_index(drop=True), use_container_width=True)
        
        # Export buttons
        st.subheader("Export")
        st.download_button("Download filtered data (CSV)", df.to_csv(index=False), file_name="filtered_runs.csv")
        st.download_button("Download per-person stats (CSV)", person_stats.to_csv(), file_name="person_stats.csv")

    except pd.errors.ParserError as e:
        st.error(f"❌ Failed to parse CSV file: {str(e)[:200]}")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {str(e)[:200]}")
else:
    st.info("👆 Upload a CSV file to get started!")
    
    # Show instructions
    with st.expander("📋 CSV Format Instructions"):
        st.markdown("""
        Your CSV file must contain exactly these three columns:
        - **date**: Date in YYYY-MM-DD format (e.g., 2025-12-01)
        - **person**: Name of the runner (text)
        - **miles run**: Distance in miles (positive number, decimal ok)
        
        Optional column:
        - **minutes**: Total minutes for the run (used to compute actual pace)
        
        **Example CSV:**
        ```
        date,person,miles run,minutes
        2025-12-01,Alice,5.2,52
        2025-12-02,Bob,3.1,32
        2025-12-02,Alice,4.5,45
        2025-12-03,Alice,6.0,58
        2025-12-03,Bob,2.8,30
        ```
        """)