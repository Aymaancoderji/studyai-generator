# 🧠 StudyAI: AI-Powered Study Tools Generator

Transform static learning materials into dynamic, interactive study resources using cutting-edge AI.

## 🎯 Project Overview

StudyAI is an EdTech application that leverages multiple AI providers (OpenAI and Groq) to automatically generate study materials from any text content. It includes both a powerful CLI tool and an interactive Streamlit dashboard.

### Key Features

- 📝 **Multi-Format Input**: PDF, TXT, DOCX, and direct text input
- 🤖 **Multi-Provider Support**: OpenAI GPT and Groq Llama models
- 🃏 **Flashcard Generation**: Automatic Q&A flashcard creation
- ❓ **Quiz Creation**: Multiple-choice questions with explanations
- 📄 **Smart Summaries**: Concise summaries with key points extraction
- 🗺️ **Concept Mapping**: Visual relationship diagrams
- 📊 **Performance Benchmarking**: Compare AI providers across metrics
- 💾 **SQLite Database**: Local storage for materials and analytics
- 🎨 **Beautiful UI**: Rich CLI interface and Streamlit dashboard

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- OpenAI API key
- Groq API key

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/studyai.git
cd studyai
```

2. **Create and activate virtual environment**:
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
OPENAI_API_KEY=your_openai_key_here
GROQ_API_KEY=your_groq_key_here
```

### Getting API Keys

**OpenAI**:
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key

**Groq**:
1. Go to https://console.groq.com
2. Sign up for free account
3. Navigate to API Keys section
4. Create new API key

## 💻 Usage

### CLI Tool

#### Basic Usage

Generate flashcards from a PDF:
```bash
python studyai.py generate --input biology_chapter.pdf --output flashcards
```

Generate quiz questions:
```bash
python studyai.py generate --input notes.txt --output quiz --count 10
```

Generate all study materials:
```bash
python studyai.py generate --input lecture.pdf --output all --save
```

#### Benchmark Mode

Compare all AI providers:
```bash
python studyai.py generate --input content.txt --output flashcards --benchmark
```

Compare specific provider:
```bash
python studyai.py generate --input notes.pdf --provider openai --output all --benchmark
```

#### View Benchmarks

```bash
python studyai.py benchmark
```

View benchmarks for specific document:
```bash
python studyai.py benchmark --doc-id 1
```

#### Concept Mapping

Generate visual concept map:
```bash
python studyai.py concept-map --input chapter.pdf --provider groq
```

#### Library Management

List all saved documents:
```bash
python studyai.py list
```

### Streamlit Dashboard

Launch the interactive dashboard:
```bash
streamlit run streamlit_app.py
```

Then navigate to `http://localhost:8501` in your browser.

#### Dashboard Features

1. **Generate Page**: Upload files, paste text, or use samples to generate study materials
2. **Benchmarks Page**: View detailed performance analytics and comparisons
3. **Library Page**: Browse and manage saved documents and materials
4. **About Page**: Learn about features and view system status

## 📁 Project Structure

```
studyai/
├── studyai.py              # CLI entry point
├── streamlit_app.py        # Streamlit dashboard
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── config/
│   └── settings.py        # Configuration management
├── core/
│   ├── ai_providers.py    # OpenAI & Groq integration
│   ├── document_parser.py # PDF/TXT/DOCX parsing
│   ├── generator.py       # Study material generation
│   └── benchmarking.py    # Performance comparison
├── database/
│   └── db_manager.py      # SQLite database operations
├── utils/
│   ├── concept_mapper.py  # Visual concept mapping
│   └── scoring.py         # Cross-API scoring
├── data/
│   └── studyai.db        # SQLite database (auto-created)
└── output/               # Generated files (auto-created)
```

## 🎓 Sprint Implementation

### Sprint 1: CLI Tool ✅

- ✅ File parsing (PDF, TXT, DOCX)
- ✅ Flashcard generation
- ✅ Quiz generation
- ✅ Summary generation
- ✅ API benchmarking with metrics
- ✅ Rich terminal output
- ✅ Database persistence

### Sprint 2: Streamlit Dashboard ✅

- ✅ Multi-tab interface
- ✅ File upload and text input
- ✅ Real-time generation
- ✅ Interactive visualizations
- ✅ Benchmark comparisons
- ✅ Document library management

### Bonus Challenges ✅

- ✅ Cross-API scoring reports
- ✅ Performance consistency analysis
- ✅ Visual concept mapping with NetworkX
- ✅ Interactive network graphs with Plotly
- ✅ Comprehensive analytics dashboard

## 📊 Benchmarking Metrics

StudyAI tracks and compares the following metrics:

- **Response Time**: Generation speed in seconds
- **Token Usage**: Total tokens consumed
- **Cost**: Estimated API cost per request
- **Quality Score**: Automated content quality assessment (0-10)
- **Composite Score**: Weighted overall performance metric

### Scoring Methodology

**Composite Score** = (Quality × 0.5) + (Speed × 0.25) + (Cost × 0.25)

## 🛠️ Configuration

### Model Selection

Edit `.env` to change default models:

```
OPENAI_MODEL=gpt-3.5-turbo  # or gpt-4, gpt-4-turbo
GROQ_MODEL=llama-3.1-70b-versatile  # or llama-3.1-8b-instant, mixtral-8x7b-32768
```

### Generation Parameters

```
MAX_TOKENS=2000        # Maximum response length
TEMPERATURE=0.7        # Creativity (0-1)
```

### Output Settings

```
DEFAULT_FLASHCARD_COUNT=20
DEFAULT_QUIZ_COUNT=10
DEFAULT_SUMMARY_LENGTH=medium  # short, medium, long
```

## 📈 Example Outputs

### Flashcard Example

```
Question: What is photosynthesis?
Answer: The process by which green plants use sunlight to synthesize foods from CO2 and water.
Difficulty: Medium
Topic: Biology
```

### Quiz Example

```
Question: Which organelle is responsible for photosynthesis?
A. Mitochondria
B. Chloroplast ✓
C. Nucleus
D. Ribosome

Explanation: Chloroplasts contain chlorophyll which captures light energy for photosynthesis.
```

## 🔍 Troubleshooting

### Common Issues

**API Key Errors**:
- Ensure `.env` file exists and contains valid API keys
- Check that keys don't have extra spaces or quotes

**File Parsing Errors**:
- Verify file format is supported (PDF, TXT, DOCX)
- Check file isn't corrupted or password-protected
- Ensure file contains extractable text (not just images)

**Database Errors**:
- Delete `data/studyai.db` and restart to reset database
- Check write permissions in the data directory

**Import Errors**:
- Run `pip install -r requirements.txt` again
- Verify Python version is 3.10+

## 🎯 Use Cases

1. **Students**: Convert lecture notes and textbooks into study materials
2. **Teachers**: Generate quiz questions from course content
3. **Content Creators**: Extract key points and summaries from articles
4. **Researchers**: Map concepts and relationships in papers
5. **Test Takers**: Create flashcards from study guides

## 🚧 Future Enhancements

- [ ] Support for audio/video transcription
- [ ] Spaced repetition algorithm for flashcards
- [ ] Collaborative study sessions
- [ ] Mobile app version
- [ ] Integration with LMS platforms
- [ ] Advanced analytics and learning insights
- [ ] Export to Anki, Quizlet formats
- [ ] Multi-language support

## 🤝 Contributing

This is a hackathon project, but contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use this project for learning and development.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Groq for ultra-fast inference
- Streamlit for the amazing dashboard framework
- The open-source community for excellent libraries

## 📞 Support

For questions or issues:
- Check this README first
- Review the `.env.example` file
- Ensure all dependencies are installed
- Verify API keys are valid

---

**Built with ❤️ for a Hackathon Project**

Happy Learning! 🎓✨
