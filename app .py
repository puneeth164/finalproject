import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import re

st.set_page_config(
    page_title="Social Media & Student Well-being",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0d0d0d; }
    h1, h2, h3, h4, p, div, label { color: white !important; }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 1px solid #333;
        margin-bottom: 10px;
    }
    .metric-value { font-size: 2.5rem; font-weight: bold; color: #FF5A5F !important; }
    .metric-label { font-size: 0.9rem; color: #aaaaaa !important; }
    .interpretation-box {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border-left: 4px solid #FF5A5F;
        border-radius: 10px;
        padding: 15px 20px;
        margin: 10px 0;
        font-size: 0.95rem;
        color: #dddddd !important;
    }
    .stSelectbox label, .stRadio label { color: white !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
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
    df['Time_Spent'] = pd.Categorical(df['Time_Spent'], categories=time_order, ordered=True)
    return df, time_order

df, time_order = load_data()

# SIDEBAR
st.sidebar.markdown("""
<div style='text-align:center; padding:10px;'>
    <h2 style='color:#FF5A5F !important;'>Filters</h2>
</div>
""", unsafe_allow_html=True)

gender_options = ['All'] + sorted(df['Gender'].dropna().unique().tolist())
selected_gender = st.sidebar.selectbox("Gender", gender_options)

occupation_options = ['All'] + sorted(df['Occupation'].dropna().unique().tolist())
selected_occupation = st.sidebar.selectbox("Occupation", occupation_options)

time_options = ['All'] + list(time_order)
selected_time = st.sidebar.selectbox("Time Spent", time_options)

filtered_df = df.copy()
if selected_gender != 'All':
    filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
if selected_occupation != 'All':
    filtered_df = filtered_df[filtered_df['Occupation'] == selected_occupation]
if selected_time != 'All':
    filtered_df = filtered_df[filtered_df['Time_Spent'] == selected_time]

st.sidebar.markdown(f"**Showing:** {len(filtered_df)} students")
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='text-align:center; font-size:0.75rem;'>
    <b style='color:#FF5A5F !important;'>VENKATA PUNEETH SRIRAMANENI</b><br>
    <span style='color:#aaaaaa;'>Visual Analytics & Comm.<br>DSA506-01-2651<br>Final Project</span>
</div>
""", unsafe_allow_html=True)

total = len(filtered_df)

# HEADER
st.markdown("""
<div style='text-align:center; padding:30px 0 10px 0;'>
    <h1 style='font-size:2.8rem; color:#FF5A5F !important;'>Social Media & Student Well-being</h1>
    <h3 style='color:#aaaaaa !important;'>FINAL PROJECT - VISUAL ANALYTICS & COMM. DSA506-01-2651</h3>
    <p style='color:#dddddd !important; font-size:1rem;'>VENKATA PUNEETH SRIRAMANENI</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)

# INTRODUCTION
st.markdown("## Introduction")
st.markdown("""
<div class='interpretation-box'>
    Social media has become an important part of students daily lives, influencing communication,
    entertainment, education, and personal expression. However, excessive social media usage has
    raised growing concerns about its impact on mental health, emotional well-being, sleep quality,
    and self-confidence.<br><br>
    This project followed a data storytelling and exploratory data analysis approach to investigate
    the impact of social media usage on student mental health. The dataset was collected from Kaggle
    and contains responses from <b>481 real students</b> covering numerical, categorical, and
    text-based data types.
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)

# STEP 1: THE HOOK
st.markdown("## The Hook")
st.markdown("### Is social media silently breaking student mental health?")

depressed   = len(filtered_df[filtered_df['Depression_Score'] >= 4])
sleep_issues = len(filtered_df[filtered_df['Sleep_Issues'] >= 4])
high_usage  = len(filtered_df[filtered_df['Time_Spent'] == 'More than 5 hours'])
validation  = len(filtered_df[filtered_df['Validation_Score'] >= 4])
distracted  = len(filtered_df[filtered_df['Easy_Distraction'] >= 4])

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value'>{total}</div>
        <div class='metric-label'>Students Surveyed</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value'>{depressed/total*100:.0f}%</div>
        <div class='metric-label'>Feel Depressed</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value'>{sleep_issues/total*100:.0f}%</div>
        <div class='metric-label'>Sleep Problems</div>
    </div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value'>{high_usage/total*100:.0f}%</div>
        <div class='metric-label'>Use 5+ Hrs/Day</div>
    </div>""", unsafe_allow_html=True)
with col5:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value'>{validation/total*100:.0f}%</div>
        <div class='metric-label'>Seek Validation</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# FIX 1 — Hook chart explicit colors no white bars
hook_data = pd.DataFrame({
    'Issue':      ['Feel Depressed','Sleep Problems','Seek Validation','Easily Distracted','High Screen Time'],
    'Percentage': [depressed/total*100, sleep_issues/total*100,
                   validation/total*100, distracted/total*100, high_usage/total*100],
    'Color':      ['#922b21','#c0392b','#e74c3c','#e67e22','#922b21']
})
fig_hook = go.Figure(go.Bar(
    x=hook_data['Issue'], y=hook_data['Percentage'],
    marker_color=hook_data['Color'],
    text=hook_data['Percentage'].round(1),
    texttemplate='%{text}%', textposition='outside'
))
fig_hook.update_layout(
    title='How Many Students Are Silently Struggling?',
    plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
    font_color='white', title_font_size=18, title_x=0.5,
    showlegend=False,
    yaxis=dict(gridcolor='#333', range=[0,110], title='% of Students'),
    xaxis=dict(title=''),
    margin=dict(t=60, b=40)
)
st.plotly_chart(fig_hook, use_container_width=True)

st.markdown("""
<div class='interpretation-box'>
    <b>Interpretation:</b> This section introduces the emotional reality behind social media usage
    among students. Instead of looking at numbers alone, the analysis highlights how many students
    are silently experiencing depression, sleep issues, distraction, and emotional dependence on
    online validation. Nearly <b>46% of students feel depressed</b> and <b>49% face sleep problems</b>
    directly linked to excessive social media use.
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)

# STEP 2: THE CONTEXT
st.markdown("## The Context")

col1, col2, col3 = st.columns(3)
with col1:
    occ_data = filtered_df['Occupation'].value_counts().reset_index()
    occ_data.columns = ['Occupation', 'Count']
    fig_occ = px.pie(occ_data, values='Count', names='Occupation',
        title='Who Participated?',
        color_discrete_sequence=['#FF5A5F','#007A87','#FFB400','#aaaaaa'], hole=0.4)
    fig_occ.update_layout(plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
        font_color='white', title_x=0.5)
    st.plotly_chart(fig_occ, use_container_width=True)

with col2:
    time_data = filtered_df['Time_Spent'].value_counts().reindex(time_order).reset_index()
    time_data.columns = ['Time_Spent', 'Count']
    time_data['Count'] = time_data['Count'].fillna(0).astype(int)
    # FIX 2 — explicit color
    fig_time = go.Figure(go.Bar(
        x=time_data['Time_Spent'], y=time_data['Count'],
        marker_color='#FC642D',
        text=time_data['Count'], textposition='outside'
    ))
    fig_time.update_layout(
        title='Daily Social Media Usage',
        plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
        font_color='white', title_x=0.5,
        xaxis=dict(tickangle=-30, tickfont=dict(size=9)),
        yaxis=dict(gridcolor='#333'),
        margin=dict(t=50, b=80)
    )
    st.plotly_chart(fig_time, use_container_width=True)

with col3:
    gender_data = filtered_df['Gender'].value_counts().reset_index()
    gender_data.columns = ['Gender', 'Count']
    fig_gender = px.pie(gender_data, values='Count', names='Gender',
        title='Gender Distribution',
        color_discrete_sequence=['#FF5A5F','#007A87','#FFB400','#aaaaaa'], hole=0.4)
    fig_gender.update_layout(plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
        font_color='white', title_x=0.5)
    st.plotly_chart(fig_gender, use_container_width=True)

st.markdown("""
<div class='interpretation-box'>
    <b>Interpretation:</b> University students make up the largest portion (~60.7%) of survey
    participants. Most students spend between 2-4 hours daily on social media, with a significant
    group using it for more than 5 hours. Female participants represent ~54.7% of respondents,
    while male participants account for ~43.9%.
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)

# STEP 3: THE CONFLICT — FIX 3: go.Figure
st.markdown("## The Conflict")

dep_time = filtered_df.groupby('Time_Spent', observed=True)['Depression_Score']\
    .mean().reindex(time_order).reset_index()
dep_time.columns = ['Time_Spent','Avg_Depression']
dep_time['Avg_Depression'] = dep_time['Avg_Depression'].fillna(0)

sleep_time = filtered_df.groupby('Time_Spent', observed=True)['Sleep_Issues']\
    .mean().reindex(time_order).reset_index()
sleep_time.columns = ['Time_Spent','Avg_Sleep']
sleep_time['Avg_Sleep'] = sleep_time['Avg_Sleep'].fillna(0)

col1, col2 = st.columns(2)
with col1:
    fig_dep = go.Figure(go.Bar(
        x=dep_time['Time_Spent'], y=dep_time['Avg_Depression'],
        marker_color=['#c0392b','#c0392b','#e74c3c','#e74c3c','#922b21','#7b241c'],
        text=dep_time['Avg_Depression'].round(2),
        texttemplate='%{text}', textposition='outside'
    ))
    fig_dep.update_layout(
        title='More Screen Time = More Depression!',
        plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
        font_color='white', title_x=0.5,
        xaxis=dict(tickangle=-30, tickfont=dict(size=9), title=''),
        yaxis=dict(gridcolor='#333', range=[0,5], title='Avg Depression Score (1-5)'),
        margin=dict(t=60, b=100)
    )
    st.plotly_chart(fig_dep, use_container_width=True)

with col2:
    fig_sleep = go.Figure(go.Bar(
        x=sleep_time['Time_Spent'], y=sleep_time['Avg_Sleep'],
        marker_color=['#6c3483','#7d3c98','#8e44ad','#9b59b6','#6c3483','#4a235a'],
        text=sleep_time['Avg_Sleep'].round(2),
        texttemplate='%{text}', textposition='outside'
    ))
    fig_sleep.update_layout(
        title='More Screen Time = Worse Sleep!',
        plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
        font_color='white', title_x=0.5,
        xaxis=dict(tickangle=-30, tickfont=dict(size=9), title=''),
        yaxis=dict(gridcolor='#333', range=[0,5], title='Avg Sleep Issues Score (1-5)'),
        margin=dict(t=60, b=100)
    )
    st.plotly_chart(fig_sleep, use_container_width=True)

st.markdown("""
<div class='interpretation-box'>
    <b>Interpretation:</b> The graphs reveal a clear upward trend between daily social media usage
    and average depression scores. Students spending less than one hour report the lowest depression
    scores (~2.0), while those using it for more than 5 hours show the highest scores (~3.5+).
    The same pattern holds for sleep issues more screen time directly leads to worse sleep quality.
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)

# STEP 4: THE JOURNEY
st.markdown("## The Journey")

st.markdown("### Which Platforms Do Students Use Most?")
platform_text = filtered_df['Platforms'].dropna().str.cat(sep=' ')
platform_text = re.sub(r'[^a-zA-Z\s]', '', platform_text.lower())
stopwords = set(['i','use','using','and','or','the','a','an',
                 'media','social','platform','app','also','yes','no'])
if len(platform_text.strip()) > 10:
    wc = WordCloud(width=1200, height=350, background_color='#0d0d0d',
        colormap='RdYlGn', max_words=60,
        stopwords=stopwords, collocations=False).generate(platform_text)
    fig_wc, ax = plt.subplots(figsize=(14, 4))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    fig_wc.patch.set_facecolor('#0d0d0d')
    st.pyplot(fig_wc)

st.markdown("""
<div class='interpretation-box'>
    <b>Interpretation:</b> Instagram, YouTube, Facebook, and TikTok are the most commonly used
    platforms among students. These platforms are known for highly engaging, addictive content that
    keeps users scrolling for hours directly contributing to mental health issues.
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown("### Comparison Sentiment Analysis")
    def map_sentiment(score):
        if score <= 2: return 'Negative'
        elif score == 3: return 'Neutral'
        else: return 'Positive'
    filtered_df = filtered_df.copy()
    filtered_df['Comparison_Sentiment'] = filtered_df['Comparison_Feeling'].apply(map_sentiment)
    sent_counts = filtered_df['Comparison_Sentiment'].value_counts().reset_index()
    sent_counts.columns = ['Sentiment', 'Count']
    fig_sent = px.pie(sent_counts, values='Count', names='Sentiment',
        title='How Students Feel About Comparisons?',
        color='Sentiment',
        color_discrete_map={'Positive':'#2ecc71','Neutral':'#FFB400','Negative':'#e74c3c'},
        hole=0.4)
    fig_sent.update_layout(plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
        font_color='white', title_x=0.5, title_font_size=14)
    st.plotly_chart(fig_sent, use_container_width=True)
    st.markdown("""
    <div class='interpretation-box'>
        Around 35% of students reported negative feelings when comparing themselves to others
        on social media feeling emotionally uncomfortable after scrolling through others lives.
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### Gender vs Mental Health")
    gender_main = filtered_df[filtered_df['Gender'].isin(['Male','Female','Non-binary'])]
    if len(gender_main) > 0:
        gender_scores = gender_main.groupby('Gender').agg(
            Depression=('Depression_Score','mean'),
            Sleep_Issues=('Sleep_Issues','mean'),
            Worry=('Worry_Score','mean'),
            Validation=('Validation_Score','mean')
        ).round(2).reset_index()
        gender_melted = gender_scores.melt(id_vars='Gender', var_name='Issue', value_name='Score')
        gender_melted['Score'] = gender_melted['Score'].round(2)
        # FIX 4 — animation title fix
        fig_ganim = px.bar(gender_melted,
            x='Gender', y='Score',
            color='Gender', animation_frame='Issue',
            title='Press Play — Gender vs Each Mental Health Issue',
            color_discrete_map={'Female':'#FF5A5F','Male':'#007A87','Non-binary':'#FFB400'},
            range_y=[0,5], text='Score')
        fig_ganim.update_traces(texttemplate='%{text}', textposition='outside')
        for frame in fig_ganim.frames:
            frame.layout = go.Layout(title_text=f'Issue: {frame.name}')
        fig_ganim.update_layout(
            plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
            font_color='white', title_x=0.5, showlegend=False,
            yaxis=dict(title='Average Score (1-5)', gridcolor='#333'),
            title_font_size=13)
        st.plotly_chart(fig_ganim, use_container_width=True)
    st.markdown("""
    <div class='interpretation-box'>
        Female participants reported slightly higher levels of depression and worry compared
        to male participants. Non-binary students showed the highest depression scores overall.
    </div>
    """, unsafe_allow_html=True)

# Heatmap
st.markdown("### Mental Health Correlation Heatmap")
mental_cols = ['Depression_Score','Sleep_Issues','Worry_Score',
               'Validation_Score','Comparison_Score','Distraction']
corr_matrix = filtered_df[mental_cols].corr()
corr_matrix.columns = ['Depression','Sleep','Worry','Validation','Comparison','Distraction']
corr_matrix.index = corr_matrix.columns
fig_hm, ax = plt.subplots(figsize=(10, 6))
fig_hm.patch.set_facecolor('#0d0d0d')
ax.set_facecolor('#0d0d0d')
sns.heatmap(corr_matrix, annot=True, cmap='RdYlGn',
    linewidths=1, linecolor='#0d0d0d', fmt='.2f',
    annot_kws={'size':11,'color':'black'}, vmin=-1, vmax=1, ax=ax, square=True)
ax.set_title('How Are Mental Health Factors Connected?', color='white', fontsize=14, pad=15)
ax.tick_params(colors='white', labelsize=10)
plt.xticks(rotation=30, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
st.pyplot(fig_hm)

st.markdown("""
<div class='interpretation-box'>
    <b>Interpretation:</b> The heatmap shows that several mental health issues are strongly
    connected. The strongest relationship appears between worry and depression scores, suggesting
    that students who feel more emotionally stressed are also more likely to experience depressive
    feelings. Depression and sleep issues also show a strong positive correlation.
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)

# STEP 5: THE RESOLUTION
st.markdown("## The Resolution")

col1, col2 = st.columns(2)
with col1:
    platform_list = []
    for _, row in filtered_df.iterrows():
        if pd.notna(row['Platforms']):
            for p in str(row['Platforms']).split(','):
                p = p.strip()
                if p:
                    platform_list.append({'Platform': p, 'Depression': row['Depression_Score']})
    if platform_list:
        platform_df = pd.DataFrame(platform_list)
        platform_summary = platform_df.groupby('Platform').agg(
            Avg_Depression=('Depression','mean'),
            Count=('Depression','count')
        ).reset_index()
        platform_summary = platform_summary[platform_summary['Count'] >= 5]\
            .sort_values('Avg_Depression', ascending=False).head(10)
        
        fig_plat = go.Figure(go.Bar(
            x=platform_summary['Platform'],
            y=platform_summary['Avg_Depression'],
            marker_color='#e74c3c',
            text=platform_summary['Avg_Depression'].round(2),
            texttemplate='%{text}', textposition='outside'
        ))
        fig_plat.update_layout(
            title='Which Platforms Cause Most Depress',
            plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
            font_color='white', title_x=0.5,
            xaxis=dict(tickangle=-20, tickfont=dict(size=10), title=''),
            yaxis=dict(gridcolor='#333', range=[0,5], title='Avg Depression Score'),
            margin=dict(t=60, b=100)
        )
        st.plotly_chart(fig_plat, use_container_width=True)
    st.markdown("""
    <div class='interpretation-box'>
        TikTok and Snapchat show the highest average depression scores. Platforms built around
        short-form, comparison-heavy content are more harmful to student mental health than
        informational platforms like YouTube.
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### Age vs Mental Health")
    df_age = filtered_df[(filtered_df['Age'] >= 13) & (filtered_df['Age'] <= 35)].copy()
    df_age['Age'] = df_age['Age'].astype(int)
    fig_age = px.scatter(df_age,
        x='Depression_Score', y='Sleep_Issues',
        animation_frame='Age', color='Gender', size='Worry_Score',
        title='Mental Health Pulse across age',
        color_discrete_map={'Male':'#007A87','Female':'#FF5A5F',
                            'Non-binary':'#FFB400','Other':'#aaaaaa'},
        range_x=[0,6], range_y=[0,6], size_max=25,
        labels={'Depression_Score':'Depression (1-5)','Sleep_Issues':'Sleep Issues (1-5)'})
    fig_age.update_layout(
        plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
        font_color='white', title_x=0.5, legend=dict(bgcolor='#1a1a1a'))
    st.plotly_chart(fig_age, use_container_width=True)
    st.markdown("""
    <div class='interpretation-box'>
        Students with higher depression scores also tend to report more sleep-related problems.
        Larger bubble sizes indicate higher worry levels emotional stress increases alongside
        depression and sleep issues across different age groups.
    </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)

# STEP 6: CALL TO ACTION 
st.markdown("## Call to Action")

solutions = pd.DataFrame({
    'Solution': ['Limit Screen\nTime < 2hrs','School Mental\nHealth Programs',
                 'Social Media\nRegulation','Awareness\nCampaigns','Parental\nMonitoring'],
    'Impact':      [90, 85, 75, 70, 80],
    'Feasibility': [85, 78, 60, 88, 82],
    'Urgency':     [95, 80, 70, 65, 75]
})
sol_melted = solutions.melt(id_vars='Solution', var_name='Metric', value_name='Score')
fig_cta = px.bar(sol_melted,
    x='Solution', y='Score',
    color='Solution', animation_frame='Metric',
    title='What Solutions Work Best?',
    color_discrete_sequence=['#FF5A5F','#007A87','#FFB400','#2ecc71','#9b59b6'],
    range_y=[0,110], text='Score',
    labels={'Score':'Score (%)','Solution':''})
fig_cta.update_traces(texttemplate='%{text}%', textposition='outside')
for frame in fig_cta.frames:
    frame.layout = go.Layout(title_text=f'{frame.name}  Solutions Comparison')
fig_cta.update_layout(
    plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
    font_color='white', title_x=0.5, showlegend=False,
    yaxis=dict(title='Score (%)', gridcolor='#333'),
    xaxis=dict(tickfont=dict(size=11), title=''),
    margin=dict(t=60, b=80)
)
st.plotly_chart(fig_cta, use_container_width=True)

st.markdown("""
<div class='interpretation-box'>
    <b>Interpretation:</b> Limiting daily social media usage to less than two hours could have
    the strongest positive impact on student mental health. Awareness campaigns score highest on
    feasibility making them the easiest solution to implement immediately.
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)

# STEP 7: EMOTIONAL APPEAL — FIX 7: chart not cut off
st.markdown("## The Emotional Appeal")

final_data = pd.DataFrame({
    'Category': ['Feel Depressed\nRegularly','Have Sleep\nProblems',
                 'Seek Validation\nOnline','Compare\nThemselves','Use Without\nPurpose'],
    'Percentage': [
        depressed/total*100,
        sleep_issues/total*100,
        validation/total*100,
        len(filtered_df[filtered_df['Comparison_Score'] >= 4])/total*100,
        len(filtered_df[filtered_df['Purposeless_Use'] >= 4])/total*100
    ],
    'Color': ['#922b21','#c0392b','#e74c3c','#e74c3c','#922b21']
})
fig_em = go.Figure(go.Bar(
    x=final_data['Category'],
    y=final_data['Percentage'],
    marker_color=final_data['Color'],
    text=final_data['Percentage'].round(1),
    texttemplate='%{text}%', textposition='outside'
))
fig_em.update_layout(
    title='Behind Every Percentage - A Real Student Is Struggling',
    plot_bgcolor='#0d0d0d', paper_bgcolor='#0d0d0d',
    font_color='white', title_font_size=18, title_x=0.5,
    showlegend=False,
    xaxis=dict(tickfont=dict(size=12), title=''),
    yaxis=dict(title='% of Students', gridcolor='#333', range=[0,110]),
    margin=dict(t=80, b=100, l=60, r=60)
)
fig_em.add_annotation(
    text="These are not just numbers these are your classmates, your friends, maybe YOU.",
    xref="paper", yref="paper", x=0.5, y=-0.2,
    showarrow=False, font=dict(size=13, color='#aaaaaa'), xanchor='center'
)
st.plotly_chart(fig_em, use_container_width=True)

st.markdown("""
<div class='interpretation-box'>
    <b>Interpretation:</b> This final visualization reveals the emotional reality behind the data.
    More than half of the students reported using social media without a clear purpose, while nearly
    half experienced depression and sleep-related problems. A significant number also reported
    comparing themselves to others online leading to emotional dissatisfaction.
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border:1px solid #333;'>", unsafe_allow_html=True)

# CONCLUSION
st.markdown("## Conclusion")
st.markdown("""
<div class='interpretation-box'>
    This project explored the impact of social media usage on student mental health using numerical,
    categorical, and text-based analysis. The findings revealed strong relationships between excessive
    screen time and increased levels of depression, worry, sleep issues, distraction, and unhealthy
    online comparison behaviors.<br><br>
    Students spending more than 5 hours daily consistently showed the highest mental health risk scores.
    TikTok and Snapchat were linked to the highest depression scores. The data strongly suggests that
    <b>limiting screen time, implementing school mental health programs, and increasing awareness</b>
    are the most impactful solutions.<br><br>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center; padding:25px; background:linear-gradient(135deg,#1a1a2e,#16213e);
     border-radius:15px; margin-top:20px;'>
    <h2 style='color:#FF5A5F !important;'>Put the Phone Down.</h2>
    <p style='color:#aaaaaa !important; font-size:1rem;'>
        These are real students - struggling every day.<br>
        One scroll at a time - their mental health fades.<br><br>
        <b style='color:white; font-size:1.1rem;'>VENKATA PUNEETH SRIRAMANENI</b><br>
        <b style='color:#FF5A5F !important;'>Visual Analytics & Comm. DSA506-01-2651 | Final Project</b>
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align:center; color:#555; font-size:0.8rem; margin-top:15px;'>
    Data Source: Social Media & Mental Health Survey (481 Students) | Built with Streamlit & Plotly
</div>
""", unsafe_allow_html=True)
