import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json

from config.settings import validate_config, PROVIDERS
from core.document_parser import DocumentParser
from core.ai_providers import get_provider, get_all_providers
from core.generator import StudyMaterialGenerator
from core.benchmarking import BenchmarkRunner
from database.db_manager import DatabaseManager
from utils.concept_mapper import ConceptMapper
from utils.scoring import CrossAPIScorer

# Page config
st.set_page_config(
    page_title="StudyAI - AI-Powered Study Tools",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stAlert {border-radius: 10px;}
    .stButton>button {border-radius: 5px; width: 100%;}
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = None
if 'benchmark_results' not in st.session_state:
    st.session_state.benchmark_results = None
if 'current_doc_content' not in st.session_state:
    st.session_state.current_doc_content = None

# Initialize database
db = DatabaseManager()

def main():
    # Header
    st.title("🧠 StudyAI")
    st.markdown("**Transform static learning materials into dynamic study tools using AI**")
    
    # Validate configuration
    try:
        validate_config()
    except ValueError as e:
        st.error(f"⚠️ Configuration Error: {e}")
        st.info("Please set up your .env file with API keys.")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # AI Provider selection
        provider_choice = st.selectbox(
            "AI Provider",
            options=list(PROVIDERS.keys()) + ['compare_all'],
            format_func=lambda x: PROVIDERS.get(x, "Compare All Providers") if x != 'compare_all' else "Compare All Providers"
        )
        
        # Study tool selection
        st.subheader("Study Tools")
        generate_flashcards = st.checkbox("Flashcards", value=True)
        generate_quiz = st.checkbox("Quiz", value=True)
        generate_summary = st.checkbox("Summary", value=True)
        generate_concepts = st.checkbox("Concept Map", value=False)
        
        # Generation parameters
        if generate_flashcards:
            flashcard_count = st.slider("Flashcard Count", 5, 50, 20)
        
        if generate_quiz:
            quiz_count = st.slider("Quiz Questions", 3, 20, 10)
        
        st.divider()
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["📝 Generate", "📊 Benchmarks", "📚 Library", "ℹ️ About"]
        )
    
    # Main content based on page selection
    if page == "📝 Generate":
        show_generate_page(provider_choice, generate_flashcards, generate_quiz, 
                          generate_summary, generate_concepts,
                          flashcard_count if generate_flashcards else 20,
                          quiz_count if generate_quiz else 10)
    
    elif page == "📊 Benchmarks":
        show_benchmarks_page()
    
    elif page == "📚 Library":
        show_library_page()
    
    elif page == "ℹ️ About":
        show_about_page()

def show_generate_page(provider_choice, gen_flash, gen_quiz, gen_summ, gen_concepts, flash_count, quiz_count):
    """Main generation page."""
    
    st.header("Generate Study Materials")
    
    # Input method tabs
    input_tab1, input_tab2, input_tab3 = st.tabs(["📄 Upload File", "✏️ Text Input", "📦 Sample"])
    
    content = None
    filename = "input"
    
    with input_tab1:
        uploaded_file = st.file_uploader(
            "Upload a document",
            type=['pdf', 'txt', 'docx'],
            help="Supported formats: PDF, TXT, DOCX"
        )
        
        if uploaded_file:
            try:
                # Save temporarily
                temp_path = Path("temp") / uploaded_file.name
                temp_path.parent.mkdir(exist_ok=True)
                
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                content, file_type = DocumentParser.parse_file(str(temp_path))
                filename = uploaded_file.name
                
                st.success(f"✅ Parsed {file_type.upper()} successfully")
                
                # Show stats
                stats = DocumentParser.get_content_stats(content)
                col1, col2, col3 = st.columns(3)
                col1.metric("Words", stats['word_count'])
                col2.metric("Characters", stats['character_count'])
                col3.metric("Sentences", stats['sentence_count'])
                
            except Exception as e:
                st.error(f"Error parsing file: {e}")
    
    with input_tab2:
        text_input = st.text_area(
            "Paste your learning material here",
            height=300,
            placeholder="Enter the content you want to create study materials from..."
        )
        
        if text_input and len(text_input.strip()) > 50:
            content = text_input
            filename = "text_input"
            
            stats = DocumentParser.get_content_stats(content)
            col1, col2 = st.columns(2)
            col1.metric("Words", stats['word_count'])
            col2.metric("Characters", stats['character_count'])
    
    with input_tab3:
        sample_choice = st.selectbox(
            "Select a sample",
            ["Photosynthesis", "Machine Learning", "World War II"]
        )
        
        samples = {
            "Photosynthesis": """Photosynthesis is the process by which green plants and some other organisms use sunlight to synthesize foods with the help of chlorophyll. Plants capture light energy using chlorophyll in their leaves. The energy is used to convert carbon dioxide and water into glucose. Oxygen is released as a by-product. The process occurs in two main stages: light-dependent reactions and light-independent reactions (Calvin cycle). During light-dependent reactions, chlorophyll absorbs light energy which splits water molecules, releasing oxygen and generating ATP and NADPH. In the Calvin cycle, ATP and NADPH are used to convert CO2 into glucose. This process is fundamental to life on Earth as it produces the oxygen we breathe and forms the base of most food chains.""",
            
            "Machine Learning": """Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on the development of computer programs that can access data and use it to learn for themselves. The process begins with observations or data, such as examples, direct experience, or instruction, to look for patterns in data and make better decisions in the future. There are three main types: supervised learning (using labeled data), unsupervised learning (finding patterns in unlabeled data), and reinforcement learning (learning through trial and error). Common applications include recommendation systems, image recognition, natural language processing, and predictive analytics.""",
            
            "World War II": """World War II was a global war that lasted from 1939 to 1945. It involved the vast majority of the world's countries, forming two opposing military alliances: the Allies and the Axis. The war began with Germany's invasion of Poland, which led Britain and France to declare war on Germany. Major events included the Battle of Britain, Pearl Harbor attack, D-Day invasion, and the atomic bombings of Hiroshima and Nagasaki. The Holocaust, perpetrated by Nazi Germany, resulted in the genocide of six million Jews. The war ended with the unconditional surrender of the Axis powers. It was the deadliest conflict in human history, with an estimated 70-85 million fatalities."""
        }
        
        content = samples[sample_choice]
        filename = sample_choice.lower().replace(" ", "_")
        
        st.info(f"📖 Sample: {sample_choice}")
        with st.expander("View content"):
            st.write(content)
    
    # Generate button
    st.divider()
    
    if content:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if provider_choice == 'compare_all':
                generate_btn = st.button("🔄 Compare All Providers", type="primary", use_container_width=True)
            else:
                generate_btn = st.button("✨ Generate Study Materials", type="primary", use_container_width=True)
        
        with col2:
            save_to_db = st.checkbox("Save to Library", value=True)
        
        if generate_btn:
            # Save document if requested
            doc_id = None
            if save_to_db:
                doc_id = db.save_document(filename, content, "text")
            
            # Compare all providers
            if provider_choice == 'compare_all':
                run_benchmark_comparison(content, doc_id, gen_flash, gen_quiz, gen_summ, flash_count, quiz_count)
            
            # Single provider
            else:
                run_single_generation(content, provider_choice, doc_id, gen_flash, gen_quiz, 
                                    gen_summ, gen_concepts, flash_count, quiz_count)
    
    else:
        st.info("👆 Please provide input content above to generate study materials.")

def run_single_generation(content, provider, doc_id, gen_flash, gen_quiz, gen_summ, gen_concepts, flash_count, quiz_count):
    """Run generation with a single provider."""
    
    try:
        ai_provider = get_provider(provider)
        generator = StudyMaterialGenerator(ai_provider)
        
        results = {}
        
        # Generate flashcards
        if gen_flash:
            with st.spinner("Generating flashcards..."):
                results['flashcards'] = generator.generate_flashcards(content, flash_count)
                if doc_id:
                    db.save_study_material(doc_id, 'flashcards', results['flashcards'], provider, ai_provider.model)
        
        # Generate quiz
        if gen_quiz:
            with st.spinner("Generating quiz..."):
                results['quiz'] = generator.generate_quiz(content, quiz_count)
                if doc_id:
                    db.save_study_material(doc_id, 'quiz', results['quiz'], provider, ai_provider.model)
        
        # Generate summary
        if gen_summ:
            with st.spinner("Generating summary..."):
                results['summary'] = generator.generate_summary(content)
                if doc_id:
                    db.save_study_material(doc_id, 'summary', results['summary'], provider, ai_provider.model)
        
        # Generate concept map
        if gen_concepts:
            with st.spinner("Generating concept map..."):
                mapper = ConceptMapper(ai_provider)
                results['concepts'] = mapper.extract_concepts(content)
        
        st.session_state.generated_content = results
        st.success("✅ Study materials generated successfully!")
        
        # Display results
        display_generated_content(results)
        
    except Exception as e:
        st.error(f"❌ Error generating content: {e}")

def run_benchmark_comparison(content, doc_id, gen_flash, gen_quiz, gen_summ, flash_count, quiz_count):
    """Run benchmark comparison across all providers."""
    
    with st.spinner("🔄 Running benchmark comparison across all providers..."):
        runner = BenchmarkRunner(db)
        results = runner.run_comprehensive_benchmark(content, doc_id)
        
        st.session_state.benchmark_results = results
        st.success("✅ Benchmark complete!")
        
        # Display comparison
        display_benchmark_comparison(results)

def display_generated_content(results):
    """Display generated study materials."""
    
    st.divider()
    st.header("📚 Generated Study Materials")
    
    # Create tabs for different materials
    tabs = []
    tab_names = []
    
    if 'flashcards' in results:
        tab_names.append("🃏 Flashcards")
    if 'quiz' in results:
        tab_names.append("❓ Quiz")
    if 'summary' in results:
        tab_names.append("📄 Summary")
    if 'concepts' in results:
        tab_names.append("🗺️ Concept Map")
    
    if tab_names:
        tabs = st.tabs(tab_names)
        
        tab_idx = 0
        
        # Flashcards
        if 'flashcards' in results:
            with tabs[tab_idx]:
                display_flashcards(results['flashcards'])
            tab_idx += 1
        
        # Quiz
        if 'quiz' in results:
            with tabs[tab_idx]:
                display_quiz(results['quiz'])
            tab_idx += 1
        
        # Summary
        if 'summary' in results:
            with tabs[tab_idx]:
                display_summary(results['summary'])
            tab_idx += 1
        
        # Concept Map
        if 'concepts' in results:
            with tabs[tab_idx]:
                display_concept_map(results['concepts'])
            tab_idx += 1

def display_flashcards(result):
    """Display flashcards."""
    
    if 'flashcards' not in result:
        st.warning("No flashcards generated")
        return
    
    flashcards = result['flashcards']
    
    st.subheader(f"Generated {len(flashcards)} Flashcards")
    
    # Metrics
    if 'metrics' in result:
        col1, col2, col3, col4 = st.columns(4)
        m = result['metrics']
        col1.metric("Response Time", f"{m.get('response_time', 0):.2f}s")
        col2.metric("Tokens Used", m.get('token_usage', 0))
        col3.metric("Cost", f"${m.get('cost', 0):.6f}")
        col4.metric("Provider", m.get('provider', 'N/A').title())
    
    st.divider()
    
    # Display flashcards
    for i, card in enumerate(flashcards, 1):
        with st.expander(f"Flashcard {i}: {card.get('topic', 'Unknown Topic')}"):
            st.markdown(f"**Question:** {card.get('question', 'N/A')}")
            st.markdown(f"**Answer:** {card.get('answer', 'N/A')}")
            
            col1, col2 = st.columns(2)
            col1.markdown(f"*Difficulty:* {card.get('difficulty', 'N/A').title()}")
            col2.markdown(f"*Topic:* {card.get('topic', 'N/A')}")
    
    # Export options
    st.divider()
    if st.button("📥 Export as JSON"):
        st.download_button(
            label="Download Flashcards",
            data=json.dumps(flashcards, indent=2),
            file_name="flashcards.json",
            mime="application/json"
        )

def display_quiz(result):
    """Display quiz questions."""
    
    if 'quiz' not in result:
        st.warning("No quiz generated")
        return
    
    quiz = result['quiz']
    
    st.subheader(f"Generated {len(quiz)} Quiz Questions")
    
    # Metrics
    if 'metrics' in result:
        col1, col2, col3, col4 = st.columns(4)
        m = result['metrics']
        col1.metric("Response Time", f"{m.get('response_time', 0):.2f}s")
        col2.metric("Tokens Used", m.get('token_usage', 0))
        col3.metric("Cost", f"${m.get('cost', 0):.6f}")
        col4.metric("Provider", m.get('provider', 'N/A').title())
    
    st.divider()
    
    # Display questions
    for i, q in enumerate(quiz, 1):
        st.markdown(f"### Question {i}")
        st.markdown(f"**{q.get('question', 'N/A')}**")
        
        options = q.get('options', [])
        correct_idx = q.get('correct_answer', 0)
        
        for j, option in enumerate(options):
            if j == correct_idx:
                st.success(f"✅ {chr(65+j)}. {option}")
            else:
                st.info(f"{chr(65+j)}. {option}")
        
        with st.expander("📖 Explanation"):
            st.write(q.get('explanation', 'No explanation provided'))
        
        st.markdown(f"*Difficulty: {q.get('difficulty', 'N/A').title()} | Topic: {q.get('topic', 'N/A')}*")
        st.divider()
    
    # Export options
    if st.button("📥 Export as JSON"):
        st.download_button(
            label="Download Quiz",
            data=json.dumps(quiz, indent=2),
            file_name="quiz.json",
            mime="application/json"
        )

def display_summary(result):
    """Display summary."""
    
    if 'summary' not in result:
        st.warning("No summary generated")
        return
    
    st.subheader("Content Summary")
    
    # Metrics
    if 'metrics' in result:
        col1, col2, col3, col4 = st.columns(4)
        m = result['metrics']
        col1.metric("Response Time", f"{m.get('response_time', 0):.2f}s")
        col2.metric("Tokens Used", m.get('token_usage', 0))
        col3.metric("Cost", f"${m.get('cost', 0):.6f}")
        col4.metric("Provider", m.get('provider', 'N/A').title())
    
    st.divider()
    
    # Display summary
    st.markdown("### Summary")
    st.info(result.get('summary', 'N/A'))
    
    # Key points
    if 'key_points' in result and result['key_points']:
        st.markdown("### Key Points")
        for point in result['key_points']:
            st.markdown(f"• {point}")
    
    # Main topics
    if 'main_topics' in result and result['main_topics']:
        st.markdown("### Main Topics")
        cols = st.columns(len(result['main_topics']))
        for i, topic in enumerate(result['main_topics']):
            cols[i].info(topic)

def display_concept_map(concepts_data):
    """Display concept map."""
    
    if 'concepts' not in concepts_data or not concepts_data['concepts']:
        st.warning("No concepts extracted")
        return
    
    st.subheader("Concept Map")
    
    # Create and display the graph
    mapper = ConceptMapper(None)
    fig = mapper.create_network_graph(concepts_data)
    st.plotly_chart(fig, use_container_width=True)
    
    # Text summary
    st.divider()
    summary = mapper.generate_text_summary(concepts_data)
    st.markdown(summary)

def display_benchmark_comparison(results):
    """Display benchmark comparison results."""
    
    st.divider()
    st.header("📊 Benchmark Comparison")
    
    # Create tabs for each material type
    material_types = [mt for mt in ['flashcards', 'quiz', 'summary'] if mt in results]
    
    if not material_types:
        st.warning("No benchmark results available")
        return
    
    tabs = st.tabs([mt.title() for mt in material_types])
    
    for idx, material_type in enumerate(material_types):
        with tabs[idx]:
            display_material_benchmark(results[material_type], material_type)
    
    # Overall comparison
    st.divider()
    st.subheader("Overall Comparison")
    
    # Collect all metrics
    all_data = []
    for material_type, providers in results.items():
        for provider, result in providers.items():
            if 'metrics' in result:
                m = result['metrics']
                all_data.append({
                    'Provider': provider.title(),
                    'Material Type': material_type.title(),
                    'Response Time': m.get('response_time', 0),
                    'Tokens': m.get('token_usage', 0),
                    'Cost': m.get('cost', 0)
                })
    
    if all_data:
        df = pd.DataFrame(all_data)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig_time = px.bar(
                df,
                x='Provider',
                y='Response Time',
                color='Material Type',
                title='Response Time Comparison',
                barmode='group'
            )
            st.plotly_chart(fig_time, use_container_width=True)
        
        with col2:
            fig_cost = px.bar(
                df,
                x='Provider',
                y='Cost',
                color='Material Type',
                title='Cost Comparison',
                barmode='group'
            )
            st.plotly_chart(fig_cost, use_container_width=True)
        
        # Summary table
        st.subheader("Summary Statistics")
        
        summary_df = df.groupby('Provider').agg({
            'Response Time': 'mean',
            'Tokens': 'mean',
            'Cost': 'sum'
        }).round(4)
        
        st.dataframe(summary_df, use_container_width=True)

def display_material_benchmark(provider_results, material_type):
    """Display benchmark for a specific material type."""
    
    comparison_data = []
    
    for provider, result in provider_results.items():
        if 'error' in result:
            st.error(f"{provider.title()}: {result['error']}")
            continue
        
        if 'metrics' in result:
            m = result['metrics']
            comparison_data.append({
                'Provider': provider.title(),
                'Response Time (s)': round(m.get('response_time', 0), 3),
                'Tokens': m.get('token_usage', 0),
                'Cost ($)': round(m.get('cost', 0), 6),
                'Model': m.get('model', 'N/A')
            })
    
    if comparison_data:
        df = pd.DataFrame(comparison_data)
        st.dataframe(df, use_container_width=True)
        
        # Winner badges
        if len(comparison_data) > 1:
            col1, col2, col3 = st.columns(3)
            
            fastest = df.loc[df['Response Time (s)'].idxmin()]
            cheapest = df.loc[df['Cost ($)'].idxmin()]
            
            with col1:
                st.success(f"⚡ Fastest: **{fastest['Provider']}** ({fastest['Response Time (s)']}s)")
            
            with col2:
                st.success(f"💰 Cheapest: **{cheapest['Provider']}** (${cheapest['Cost ($)']})")
            
            with col3:
                avg_time = df['Response Time (s)'].mean()
                st.info(f"📊 Avg Time: {avg_time:.3f}s")

def show_benchmarks_page():
    """Show benchmarks and analytics page."""
    
    st.header("📊 Benchmark Analytics")
    
    # Get all benchmarks
    benchmarks = db.get_benchmarks()
    
    if not benchmarks:
        st.info("No benchmark data available. Run some comparisons to see analytics here!")
        return
    
    # Provider comparison
    st.subheader("Provider Performance Comparison")
    
    df = CrossAPIScorer.compare_providers(benchmarks)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            fig_quality = px.bar(
                df,
                x='Provider',
                y='Avg Quality Score',
                title='Average Quality Score by Provider',
                color='Avg Quality Score',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig_quality, use_container_width=True)
        
        with col2:
            fig_composite = px.bar(
                df,
                x='Provider',
                y='Composite Score',
                title='Composite Score by Provider',
                color='Composite Score',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig_composite, use_container_width=True)
    
    # Category winners
    st.divider()
    st.subheader("Category Winners")
    
    winners = CrossAPIScorer.generate_winner_by_category(benchmarks)
    
    col1, col2, col3 = st.columns(3)
    
    for idx, (category, data) in enumerate(winners.items()):
        with [col1, col2, col3][idx]:
            st.metric(
                label=category,
                value=data['provider'],
                delta=data['value']
            )
    
    # Recommendation
    st.divider()
    recommendation = CrossAPIScorer.generate_recommendation(benchmarks)
    st.markdown(recommendation)
    
    # Detailed breakdown
    st.divider()
    st.subheader("Detailed Performance Breakdown")
    
    # Create detailed DataFrame
    detailed_data = []
    for bench in benchmarks:
        detailed_data.append({
            'Provider': bench['provider'].title(),
            'Model': bench['model'],
            'Material Type': bench['material_type'].title(),
            'Response Time': bench['response_time'],
            'Tokens': bench['token_usage'],
            'Cost': bench['cost'],
            'Quality Score': bench['quality_score'],
            'Date': bench['created_at']
        })
    
    detailed_df = pd.DataFrame(detailed_data)
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        provider_filter = st.multiselect(
            "Filter by Provider",
            options=detailed_df['Provider'].unique(),
            default=detailed_df['Provider'].unique()
        )
    
    with col2:
        material_filter = st.multiselect(
            "Filter by Material Type",
            options=detailed_df['Material Type'].unique(),
            default=detailed_df['Material Type'].unique()
        )
    
    # Apply filters
    filtered_df = detailed_df[
        (detailed_df['Provider'].isin(provider_filter)) &
        (detailed_df['Material Type'].isin(material_filter))
    ]
    
    st.dataframe(filtered_df, use_container_width=True)

def show_library_page():
    """Show saved documents library."""
    
    st.header("📚 Document Library")
    
    documents = db.get_all_documents()
    
    if not documents:
        st.info("No documents in library. Generate some study materials to populate your library!")
        return
    
    # Display documents
    for doc in documents:
        with st.expander(f"📄 {doc['filename']} (ID: {doc['id']})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Type:** {doc['file_type'].upper()}")
                st.markdown(f"**Created:** {doc['created_at']}")
                st.markdown(f"**Preview:** {doc['content'][:200]}...")
            
            with col2:
                if st.button(f"View Materials", key=f"view_{doc['id']}"):
                    materials = db.get_study_materials(doc['id'])
                    
                    if materials:
                        st.write("### Study Materials")
                        for mat in materials:
                            st.write(f"- {mat['material_type'].title()} ({mat['provider'].title()})")
                    else:
                        st.info("No study materials for this document")
                
                if st.button(f"Delete", key=f"del_{doc['id']}", type="secondary"):
                    db.delete_document(doc['id'])
                    st.success("Document deleted!")
                    st.rerun()

def show_about_page():
    """Show about page."""
    
    st.header("ℹ️ About StudyAI")
    
    st.markdown("""
    ## 🎓 Welcome to StudyAI!
    
    **StudyAI** is an AI-powered study tools generator that transforms static learning materials 
    into dynamic, interactive study resources.
    
    ### ✨ Features
    
    - **📝 Multiple Input Formats**: Upload PDFs, text files, or paste content directly
    - **🤖 Multi-Provider Support**: Compare OpenAI and Groq AI models
    - **🃏 Flashcard Generation**: Create Q&A flashcards automatically
    - **❓ Quiz Creation**: Generate multiple-choice quizzes with explanations
    - **📄 Smart Summaries**: Get concise summaries with key points
    - **🗺️ Concept Mapping**: Visualize relationships between concepts
    - **📊 Benchmarking**: Compare AI provider performance
    - **💾 Library Management**: Save and organize your study materials
    
    ### 🚀 How to Use
    
    1. **Choose an input method** (upload, paste, or select sample)
    2. **Select AI provider** or compare all
    3. **Choose study tools** to generate
    4. **Click generate** and wait for AI to create your materials
    5. **Review and export** your study tools
    
    ### 🔧 Technology Stack
    
    - **AI Providers**: OpenAI GPT, Groq Llama
    - **Framework**: Streamlit
    - **Database**: SQLite
    - **Visualization**: Plotly
    - **Processing**: NetworkX, Pandas
    
    ### 📈 Benchmark Metrics
    
    - **Response Time**: How fast the AI generates content
    - **Token Usage**: Number of tokens consumed
    - **Cost**: Estimated API cost per request
    - **Quality Score**: Automated quality assessment
    - **Composite Score**: Weighted overall performance
    
    ### 💡 Tips
    
    - Use **longer content** for better quality flashcards and quizzes
    - Try **different providers** to find your preferred balance of speed, cost, and quality
    - **Save to library** to track your materials over time
    - Use **benchmark mode** to make informed decisions about AI provider selection
    
    ### 🔐 Privacy & Security
    
    - All data is stored locally in SQLite
    - No data is shared with third parties
    - API keys are stored in environment variables
    
    ### 📞 Support
    
    For issues or questions, please refer to the README.md file or check the configuration settings.
    
    ---
    
    **Version**: 1.0.0  
    **Built for**: Educational Hackathon Project
    """)
    
    st.divider()
    
    # System status
    st.subheader("System Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        doc_count = len(db.get_all_documents())
        st.metric("Documents", doc_count)
    
    with col2:
        benchmark_count = len(db.get_benchmarks())
        st.metric("Benchmarks", benchmark_count)
    
    with col3:
        st.metric("Providers", "2")

if __name__ == "__main__":
    main()
