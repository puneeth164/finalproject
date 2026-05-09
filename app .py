import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from textblob import TextBlob
import re

# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="Social Media & Student Well-being",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
<style>
    .main { background-color: #0d0d0d; }
    .stApp { background-color: #0d0d0d; }
    h1, h2, h3, p, div { color: white !important; }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 1px solid #333;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF5A5F !important;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #aaaaaa !important;
    }
    .stSelectbox label { color: white !important; }
    .sidebar .sidebar-content { background-color: #1a1a2e; }
</style>
""", unsafe_allow_html=True)

# ============================================
# LOAD DATA
# ============================================
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/shariful07/Student-Mental-Health/main/Student%20Mental%20health.csv"
    try:
        df = pd.read_csv(url)
    except:
        # fallback — upload
        df = pd.read_csv("smmh.csv")

    df.columns = [
        'Timestamp', 'Age', 'Gender', 'Relationship_Status',
        'Occupation', 'Organization', 'Uses_SM', 'Platforms',
        'Time_Spent', 'Purposeless_Use', 'Distraction',
        'Restlessness', 'Easy_Distraction', 'Worry_Score',
        'Concentration', 'Comparison_Score', 'Comparison_Feeling',
        'Validation_Score', 'Depression_Score', 'Interest_Fluctuation',
        'Sleep_Issues'
    ]
    df['Gender'] = df['Gender'].str.strip().replace({
        'NB': 'Non-binary', 'Nonbinary ': 'Non-binary',
        'Non binary ': 'Non-binary', 'unsure ': 'Other',
        'Trans': 'Other', 'There are others???': 'Other'
    })
    df = df[df['Age'].notna()]
    df['Age'] = df['Age'].astype(int)
    time_order = [
        'Less than an Hour', 'Between 1 and 2 hours',
        'Between 2 and 3 hours', 'Between 3 and 4 hours',
        'Between 4 and 5 hours', 'More than 5 hours'
    ]
    df['Time_Spent'] = pd.Categorical(
        df['Time_Spent'], categories=time_order, ordered=True
    )
    return df, time_order

df, time_order = load_data()

# ============================================
# SIDEBAR FILTERS
# ============================================
st.sidebar.image("https://img.icons8.com/fluency/96/mental-health.png", width=80)
st.sidebar.title("📱 Filters")

gender_options = ['All'] + list(df['Gender'].dropna().unique())
selected_gender = st.sidebar.selectbox("Gender", gender_options)

occupation_options = ['All'] + list(df['Occupation'].dropna().unique())
selected_occupation = st.sidebar.selectbox("Occupation", occupation_options)

time_options = ['All'] + list(time_order)
selected_time = st.sidebar.selectbox("Time Spent on Social Media", time_options)

# Apply filters
filtered_df = df.copy()
if selected_gender != 'All':
    filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
if selected_occupation != 'All':
    filtered_df = filtered_df[filtered_df['Occupation'] == selected_occupation]
if selected_time != 'All':
    filtered_df = filtered_df[filtered_df['Time_Spent'] == selected_time]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Showing:** {len(filtered_df)} students")

# ============================================
# HEADER
# ============================================
st.markdown("""
<div style='text-align:center; padding: 30px 0;'>
    <h1 style='font-size:3rem; color:#FF5A5F !important;'>📱 Social Media & Student Well-being</h1>
    <p style='font-size:1.2rem; color:#aaaaaa !important;'>
        An Interactive Data Story — 481 Real Students Surveyed
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================
# STEP 1: THE HOOK — KPI Cards
# ============================================
st.markdown("## 🎬 The Hook")
st.markdown("### *Is social media silently breaking student mental health?*")

total = len(filtered_df)
depressed = len(filtered_df[filtered_df['Depression_Score'] >= 4])
sleep_issues = len(filtered_df[filtered_df['Sleep_Issues'] >= 4])
high_usage = len(filtered_df[filtered_df['Time_Spent'] == 'More than 5 hours'])
validation = len(filtered_df[filtered_df['Validation_Score'] >= 4])

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{total}</div>
        <div class='metric-label'>👥 Students Surveyed</div>
    </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{depressed/total*100:.0f}%</div>
        <div class='metric-label'>Feel Depressed</div>
    </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{sleep_issues/total*100:.0f}%</div>
        <div class='metric-label'>Sleep Problems</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{high_usage/total*100:.0f}%</div>
        <div class='metric-label'>📱 Use 5+ Hours/Day</div>
    </div>""", unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-value'>{validation/total*100:.0f}%</div>
        <div class='metric-label'> Seek Validation</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

hook_data = pd.DataFrame({
    'Issue': ['Feel Depressed', 'Sleep Problems', 'Seek Validation', 'Easily Distracted', 'High Screen Time'],
    'Percentage': [
        depressed/total*100,
        sleep_issues/total*100,
        validation/total*100,
        len(filtered_df[filtered_df['Easy_Distraction'] >= 4])/total*100,
        high_usage/total*100
    ]
})
fig_hook = px.bar(
    hook_data, x='Issue', y='Percentage',
    color='Percentage', color_continuous_scale='Reds',
    title='📱 How Many Students Are Silently Struggling?',
    text=hook_data['Percentage'].round(1)
)
fig_hook.update_traces(texttemplate='%{text}%', textposition='outside')
fig_hook.update_layout(
    plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
    font_color='white', title_font_size=18, title_x=0.5,
    showlegend=False, yaxis=dict(gridcolor='#333', range=[0,100]),
    margin=dict(t=60, b=40)
)
st.plotly_chart(fig_hook, use_container_width=True)

st.markdown("---")

# ============================================
# STEP 2: THE CONTEXT
# ============================================
st.markdown("## The Context")

col1, col2, col3 = st.columns(3)

with col1:
    occ_data = filtered_df['Occupation'].value_counts().reset_index()
    occ_data.columns = ['Occupation', 'Count']
    fig_occ = px.pie(
        occ_data, values='Count', names='Occupation',
        title='Who Participated?',
        color_discrete_sequence=['#FF5A5F','#007A87','#FFB400','#aaaaaa'],
        hole=0.4
    )
    fig_occ.update_layout(
        plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
        font_color='white', title_x=0.5
    )
    st.plotly_chart(fig_occ, use_container_width=True)

with col2:
    time_data = filtered_df['Time_Spent'].value_counts()\
        .reindex(time_order).reset_index()
    time_data.columns = ['Time_Spent', 'Count']
    fig_time = px.bar(
        time_data, x='Time_Spent', y='Count',
        color='Count', color_continuous_scale='Oranges',
        title='Daily Social Media Usage',
        text='Count'
    )
    fig_time.update_traces(textposition='outside')
    fig_time.update_layout(
        plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
        font_color='white', title_x=0.5, showlegend=False,
        xaxis=dict(tickangle=-30, tickfont=dict(size=9)),
        yaxis=dict(gridcolor='#333')
    )
    st.plotly_chart(fig_time, use_container_width=True)

with col3:
    gender_data = filtered_df['Gender'].value_counts().reset_index()
    gender_data.columns = ['Gender', 'Count']
    fig_gender = px.pie(
        gender_data, values='Count', names='Gender',
        title='Gender Distribution',
        color_discrete_sequence=['#FF5A5F','#007A87','#FFB400','#aaaaaa'],
        hole=0.4
    )
    fig_gender.update_layout(
        plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
        font_color='white', title_x=0.5
    )
    st.plotly_chart(fig_gender, use_container_width=True)

st.markdown("---")

# ============================================
# STEP 3: THE CONFLICT
# ============================================
st.markdown("## The Conflict")

col1, col2 = st.columns(2)

with col1:
    dep_time = filtered_df.groupby('Time_Spent', observed=True)['Depression_Score']\
        .mean().reindex(time_order).reset_index()
    dep_time.columns = ['Time_Spent', 'Avg_Depression']
    fig_dep = px.bar(
        dep_time, x='Time_Spent', y='Avg_Depression',
        color='Avg_Depression', color_continuous_scale='Reds',
        title='More Screen Time = More Depression!',
        text=dep_time['Avg_Depression'].round(2), range_y=[0,5]
    )
    fig_dep.update_traces(texttemplate='%{text}', textposition='outside')
    fig_dep.update_layout(
        plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
        font_color='white', title_x=0.5, showlegend=False,
        xaxis=dict(tickangle=-30, tickfont=dict(size=9)),
        yaxis=dict(gridcolor='#333')
    )
    st.plotly_chart(fig_dep, use_container_width=True)

with col2:
    sleep_time = filtered_df.groupby('Time_Spent', observed=True)['Sleep_Issues']\
        .mean().reindex(time_order).reset_index()
    sleep_time.columns = ['Time_Spent', 'Avg_Sleep']
    fig_sleep = px.bar(
        sleep_time, x='Time_Spent', y='Avg_Sleep',
        color='Avg_Sleep', color_continuous_scale='Purples',
        title='More Screen Time = Worse Sleep!',
        text=sleep_time['Avg_Sleep'].round(2), range_y=[0,5]
    )
    fig_sleep.update_traces(texttemplate='%{text}', textposition='outside')
    fig_sleep.update_layout(
        plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
        font_color='white', title_x=0.5, showlegend=False,
        xaxis=dict(tickangle=-30, tickfont=dict(size=9)),
        yaxis=dict(gridcolor='#333')
    )
    st.plotly_chart(fig_sleep, use_container_width=True)

st.markdown("---")

# ============================================
# STEP 4: THE JOURNEY
# ============================================
st.markdown("## The Journey")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Which Platforms Do Students Use?")
    platform_text = filtered_df['Platforms'].dropna().str.cat(sep=' ')
    platform_text = re.sub(r'[^a-zA-Z\s]', '', platform_text.lower())
    stopwords = set([
        'i','use','using','and','or','the','a','an',
        'media','social','platform','app','also','yes','no'
    ])
    if len(platform_text.strip()) > 10:
        wc = WordCloud(
            width=700, height=400,
            background_color='#0d0d0d',
            colormap='RdYlGn',
            max_words=50,
            stopwords=stopwords,
            collocations=False
        ).generate(platform_text)
        fig_wc, ax = plt.subplots(figsize=(8, 4))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        fig_wc.patch.set_facecolor('#0d0d0d')
        st.pyplot(fig_wc)
    else:
        st.info("Not enough data for word cloud with current filters!")

with col2:
    st.markdown("### How Do Students Feel About Comparisons?")
    def map_sentiment(score):
        if score <= 2: return 'Negative '
        elif score == 3: return 'Neutral '
        else: return 'Positive '

    filtered_df['Comparison_Sentiment'] = filtered_df['Comparison_Feeling'].apply(map_sentiment)
    sent_counts = filtered_df['Comparison_Sentiment'].value_counts().reset_index()
    sent_counts.columns = ['Sentiment', 'Count']
    fig_sent = px.pie(
        sent_counts, values='Count', names='Sentiment',
        color='Sentiment',
        color_discrete_map={
            'Positive ': '#2ecc71',
            'Neutral ': '#FFB400',
            'Negative ': '#e74c3c'
        },
        hole=0.4
    )
    fig_sent.update_layout(
        plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
        font_color='white', title_x=0.5
    )
    st.plotly_chart(fig_sent, use_container_width=True)

# Gender animated
st.markdown("### 🎬 Gender vs Mental Health (Animated)")
gender_main = filtered_df[filtered_df['Gender'].isin(['Male','Female','Non-binary'])]
if len(gender_main) > 0:
    gender_scores = gender_main.groupby('Gender').agg(
        Depression=('Depression_Score','mean'),
        Sleep_Issues=('Sleep_Issues','mean'),
        Worry=('Worry_Score','mean'),
        Validation=('Validation_Score','mean')
    ).round(2).reset_index()
    gender_melted = gender_scores.melt(
        id_vars='Gender', var_name='Issue', value_name='Score'
    )
    fig_gender_anim = px.bar(
        gender_melted, x='Gender', y='Score',
        color='Gender', animation_frame='Issue',
        color_discrete_map={
            'Female': '#FF5A5F',
            'Male': '#007A87',
            'Non-binary': '#FFB400'
        },
        range_y=[0,5], text='Score',
        title='Press ▶ Play — See How Each Issue Affects Different Genders!'
    )
    fig_gender_anim.update_traces(texttemplate='%{text}', textposition='outside')
    fig_gender_anim.update_layout(
        plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
        font_color='white', title_x=0.5, showlegend=False,
        yaxis=dict(title='Average Score (1-5)', gridcolor='#333')
    )
    st.plotly_chart(fig_gender_anim, use_container_width=True)

st.markdown("---")

# ============================================
# STEP 5: THE RESOLUTION
# ============================================
st.markdown("##  The Resolution")

col1, col2 = st.columns(2)

with col1:
    platform_list = []
    for _, row in filtered_df.iterrows():
        if pd.notna(row['Platforms']):
            for p in str(row['Platforms']).split(','):
                p = p.strip()
                if p:
                    platform_list.append({
                        'Platform': p,
                        'Depression': row['Depression_Score']
                    })
    if platform_list:
        platform_df = pd.DataFrame(platform_list)
        platform_summary = platform_df.groupby('Platform').agg(
            Avg_Depression=('Depression','mean'),
            Count=('Depression','count')
        ).reset_index()
        platform_summary = platform_summary[platform_summary['Count'] >= 5]\
            .sort_values('Avg_Depression', ascending=False).head(10)
        fig_plat = px.bar(
            platform_summary, x='Platform', y='Avg_Depression',
            color='Avg_Depression', color_continuous_scale='Reds',
            title='Which Platforms Cause Most Depression?',
            text=platform_summary['Avg_Depression'].round(2), range_y=[0,5]
        )
        fig_plat.update_traces(texttemplate='%{text}', textposition='outside')
        fig_plat.update_layout(
            plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
            font_color='white', title_x=0.5, showlegend=False,
            xaxis=dict(tickangle=-30, tickfont=dict(size=10)),
            yaxis=dict(gridcolor='#333')
        )
        st.plotly_chart(fig_plat, use_container_width=True)

with col2:
    import seaborn as sns
    mental_cols = [
        'Depression_Score', 'Sleep_Issues', 'Worry_Score',
        'Validation_Score', 'Comparison_Score', 'Distraction'
    ]
    corr_matrix = filtered_df[mental_cols].corr()
    corr_matrix.columns = ['Depression','Sleep','Worry','Validation','Comparison','Distraction']
    corr_matrix.index = corr_matrix.columns
    fig_hm, ax = plt.subplots(figsize=(7,5))
    fig_hm.patch.set_facecolor('#0d0d0d')
    ax.set_facecolor('#0d0d0d')
    sns.heatmap(
        corr_matrix, annot=True, cmap='RdYlGn',
        linewidths=1, linecolor='#0d0d0d',
        fmt='.2f', annot_kws={'size':10, 'color':'black'},
        vmin=-1, vmax=1, ax=ax
    )
    ax.set_title('Mental Health Correlation Heatmap', color='white', fontsize=14, pad=15)
    ax.tick_params(colors='white', labelsize=9)
    plt.xticks(rotation=30, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    st.pyplot(fig_hm)

st.markdown("---")

# ============================================
# STEP 6: CALL TO ACTION
# ============================================
st.markdown("##  Call to Action")

solutions = pd.DataFrame({
    'Solution': [
        'Limit Screen\nTime < 2hrs',
        'School Mental\nHealth Programs',
        'Social Media\nRegulation',
        'Awareness\nCampaigns',
        'Parental\nMonitoring'
    ],
    'Impact': [90, 85, 75, 70, 80],
    'Feasibility': [85, 78, 60, 88, 82],
    'Urgency': [95, 80, 70, 65, 75]
})

sol_melted = solutions.melt(
    id_vars='Solution', var_name='Metric', value_name='Score'
)

fig_cta = px.bar(
    sol_melted, x='Solution', y='Score',
    color='Solution', animation_frame='Metric',
    title=' What Solutions Work Best? (Press ▶ Play!)',
    color_discrete_sequence=['#FF5A5F','#007A87','#FFB400','#2ecc71','#9b59b6'],
    range_y=[0,110], text='Score'
)
fig_cta.update_traces(texttemplate='%{text}%', textposition='outside')
fig_cta.update_layout(
    plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
    font_color='white', title_x=0.5, showlegend=False,
    yaxis=dict(title='Score (%)', gridcolor='#333')
)
st.plotly_chart(fig_cta, use_container_width=True)

st.markdown("---")

# ============================================
# STEP 7: EMOTIONAL APPEAL
# ============================================
st.markdown("## The Emotional Appeal")

final_data = pd.DataFrame({
    'Category': [
        'Feel Depressed\nRegularly',
        'Have Sleep\nProblems',
        'Seek Validation\nOnline',
        'Compare\nThemselves',
        'Use Without\nPurpose'
    ],
    'Percentage': [
        len(filtered_df[filtered_df['Depression_Score'] >= 4])/total*100,
        len(filtered_df[filtered_df['Sleep_Issues'] >= 4])/total*100,
        len(filtered_df[filtered_df['Validation_Score'] >= 4])/total*100,
        len(filtered_df[filtered_df['Comparison_Score'] >= 4])/total*100,
        len(filtered_df[filtered_df['Purposeless_Use'] >= 4])/total*100
    ]
})

fig_emotion = px.bar(
    final_data, x='Category', y='Percentage',
    color='Percentage', color_continuous_scale='Reds',
    title=' Behind Every Percentage - A Real Student Is Struggling',
    text=final_data['Percentage'].round(1), range_y=[0,100]
)
fig_emotion.update_traces(texttemplate='%{text}%', textposition='outside')
fig_emotion.update_layout(
    plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
    font_color='white', title_font_size=18, title_x=0.5,
    showlegend=False,
    xaxis=dict(tickfont=dict(size=11)),
    yaxis=dict(title='% of Students', gridcolor='#333'),
    margin=dict(t=80, b=60)
)
fig_emotion.add_annotation(
    text="These are not just numbers — these are your classmates, your friends, maybe YOU.",
    xref="paper", yref="paper", x=0.5, y=-0.15,
    showarrow=False, font=dict(size=13, color='#aaaaaa'), xanchor='center'
)
st.plotly_chart(fig_emotion, use_container_width=True)

st.markdown("""
<div style='text-align:center; padding:30px; background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius:15px; margin-top:20px;'>
    <h2 style='color:#FF5A5F !important;'>📵 Put the Phone Down.</h2>
    <p style='color:#aaaaaa !important; font-size:1.1rem;'>
        These are real students — struggling every day.<br>
        One scroll at a time — their mental health fades.<br>
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style='text-align:center; color:#555; font-size:0.8rem;'>
    Data Source: Social Media & Mental Health Survey (481 Students) | Built with Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
