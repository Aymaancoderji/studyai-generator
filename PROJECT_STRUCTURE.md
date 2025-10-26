# 📁 StudyAI Project Structure

Complete file structure and organization guide.

## Directory Tree

```
studyai/
├── 📄 studyai.py                    # Main CLI application
├── 📄 streamlit_app.py              # Streamlit dashboard
├── 📄 requirements.txt              # Python dependencies
├── 📄 .env.example                  # Environment template
├── 📄 .env                          # Your API keys (git-ignored)
├── 📄 .gitignore                    # Git ignore rules
├── 📄 README.md                     # Main documentation
├── 📄 QUICKSTART.md                 # Quick start guide
├── 📄 PROJECT_STRUCTURE.md          # This file
├── 📄 setup.sh                      # Setup script
│
├── 📁 config/                       # Configuration module
│   ├── __init__.py
│   └── settings.py                  # App settings & constants
│
├── 📁 core/                         # Core functionality
│   ├── __init__.py
│   ├── ai_providers.py              # OpenAI & Groq wrappers
│   ├── document_parser.py           # PDF/TXT/DOCX parsing
│   ├── generator.py                 # Study material generation
│   └── benchmarking.py              # Performance comparison
│
├── 📁 database/                     # Database management
│   ├── __init__.py
│   └── db_manager.py                # SQLite operations
│
├── 📁 utils/                        # Utility functions
│   ├── __init__.py
│   ├── concept_mapper.py            # Concept visualization
│   └── scoring.py                   # Cross-API scoring
│
├── 📁 data/                         # Data directory (auto-created)
│   └── studyai.db                   # SQLite database
│
├── 📁 output/                       # Generated files (auto-created)
│   ├── flashcards_*.json
│   ├── quiz_*.json
│   └── concept_map_*.html
│
└── 📁 temp/                         # Temporary files (auto-created)
    └── uploaded_files/
```

## File Descriptions

### Root Files

| File | Purpose | Key Features |
|------|---------|--------------|
| `studyai.py` | CLI application | Commands: generate, benchmark, list, concept-map |
| `streamlit_app.py` | Web dashboard | Interactive UI with tabs and visualizations |
| `requirements.txt` | Dependencies | All required Python packages |
| `.env.example` | Config template | API keys and settings template |
| `.gitignore` | Git exclusions | Ignores secrets, cache, database |
| `README.md` | Documentation | Full project documentation |
| `QUICKSTART.md` | Quick guide | 5-minute setup instructions |
| `setup.sh` | Setup script | Automated environment setup |

### Config Module (`config/`)

#### `settings.py`
```python
# Contains:
- API keys loading from .env
- Model configurations
- Database paths
- Default parameters
- Pricing information
- Validation functions
```

**Key Variables:**
- `OPENAI_API_KEY`, `GROQ_API_KEY`
- `OPENAI_MODEL`, `GROQ_MODEL`
- `DATABASE_PATH`
- `MAX_TOKENS`, `TEMPERATURE`
- `PRICING` (cost per 1M tokens)

### Core Module (`core/`)

#### `ai_providers.py`
```python
# Classes:
- AIProvider (base class)
- OpenAIProvider
- GroqProvider

# Functions:
- get_provider(name) -> AIProvider
- get_all_providers() -> dict
```

**Features:**
- Unified interface for multiple AI providers
- Automatic token counting
- Cost calculation
- Response time tracking

#### `document_parser.py`
```python
# Class:
- DocumentParser

# Methods:
- parse_file(path) -> (content, type)
- parse_pdf(path) -> str
- parse_txt(path) -> str
- parse_docx(path) -> str
- validate_content(content) -> bool
- get_content_stats(content) -> dict
```

**Supported Formats:**
- PDF (via PyPDF2)
- TXT (plain text)
- DOCX (via python-docx)

#### `generator.py`
```python
# Class:
- StudyMaterialGenerator

# Methods:
- generate_flashcards(content, count)
- generate_quiz(content, count)
- generate_summary(content, length)
- generate_study_guide(content)
```

**Features:**
- Structured JSON output
- Error handling
- Metric tracking
- Quality validation

#### `benchmarking.py`
```python
# Class:
- BenchmarkRunner

# Methods:
- run_comprehensive_benchmark(content, doc_id)
- generate_comparison_report(doc_id)
```

**Benchmarks:**
- Response time
- Token usage
- Cost analysis
- Quality scoring
- Provider comparison

### Database Module (`database/`)

#### `db_manager.py`
```python
# Class:
- DatabaseManager

# Tables:
- documents
- study_materials
- benchmarks
- sessions

# Methods:
- save_document(filename, content, type)
- save_study_material(doc_id, type, content, provider, model)
- save_benchmark(doc_id, provider, metrics)
- get_document(doc_id)
- get_study_materials(doc_id)
- get_benchmarks(doc_id)
- get_all_documents()
- delete_document(doc_id)
```

**Schema:**
```sql
documents: id, filename, content, file_type, created_at
study_materials: id, document_id, material_type, content, provider, model, created_at
benchmarks: id, document_id, provider, model, material_type, response_time, token_usage, cost, quality_score, metadata, created_at
```

### Utils Module (`utils/`)

#### `concept_mapper.py`
```python
# Class:
- ConceptMapper

# Methods:
- extract_concepts(content) -> dict
- create_network_graph(concepts) -> plotly.Figure
- generate_text_summary(concepts) -> str
```

**Features:**
- AI-powered concept extraction
- NetworkX graph creation
- Interactive Plotly visualization
- Relationship mapping

#### `scoring.py`
```python
# Class:
- CrossAPIScorer

# Methods:
- calculate_composite_score(benchmark)
- compare_providers(benchmarks)
- generate_winner_by_category(benchmarks)
- calculate_consistency_score(benchmarks)
- generate_recommendation(benchmarks)
```

**Metrics:**
- Composite score (weighted)
- Category winners
- Consistency analysis
- Recommendations

## Data Flow

### CLI Generation Flow
```
User Input → Document Parser → Content
                                   ↓
AI Provider ← Generator ← Validated Content
     ↓
Response + Metrics
     ↓
Database Storage (optional)
     ↓
Console Display
```

### Benchmark Flow
```
Content → Multiple Providers (parallel)
              ↓
         Results + Metrics
              ↓
         Database Storage
              ↓
      Scoring & Analysis
              ↓
     Comparison Report
```

### Streamlit Flow
```
User Upload → Parser → Content
                          ↓
              Provider Selection
                          ↓
              Generation
                          ↓
         Real-time Display
                          ↓
         Database Storage
                          ↓
         Analytics Dashboard
```

## Module Dependencies

```
studyai.py
├── config.settings
├── core.document_parser
├── core.ai_providers
├── core.generator
├── core.benchmarking
├── database.db_manager
├── utils.concept_mapper
└── utils.scoring

streamlit_app.py
├── config.settings
├── core.* (all core modules)
├── database.db_manager
└── utils.* (all utils modules)
```

## Environment Variables

Required in `.env`:
```bash
# API Keys (Required)
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...

# Models (Optional - has defaults)
OPENAI_MODEL=gpt-3.5-turbo
GROQ_MODEL=llama-3.1-70b-versatile

# Paths (Optional - has defaults)
DATABASE_PATH=data/studyai.db

# Generation Settings (Optional)
MAX_TOKENS=2000
TEMPERATURE=0.7
DEBUG=False
```

## Database Schema

### Tables

**documents**
- Stores uploaded/input documents
- Primary source content

**study_materials**
- Generated flashcards, quizzes, summaries
- Links to source document
- Tracks provider and model used

**benchmarks**
- Performance metrics
- Cost tracking
- Quality scores
- Comparison data

**sessions** (future use)
- User session tracking
- Batch operations

## Output Files

Generated files go to `output/` directory:

```
output/
├── flashcards_20250120_143052.json
├── quiz_20250120_143052.json
├── summary_20250120_143052.txt
└── concept_map_biology.html
```

## Extending the Project

### Adding a New AI Provider

1. Create provider class in `core/ai_providers.py`:
```python
class NewProvider(AIProvider):
    def __init__(self, model):
        super().__init__('newprovider', model)
        self.client = NewProviderClient(api_key=NEW_API_KEY)
    
    def generate(self, prompt, system_prompt):
        # Implementation
        pass
```

2. Update `get_provider()` function
3. Add to `config/settings.py` PROVIDERS and PRICING
4. Update `.env.example`

### Adding a New Study Tool

1. Add method to `core/generator.py`:
```python
def generate_mind_map(self, content):
    # Implementation
    pass
```

2. Add CLI command in `studyai.py`
3. Add UI component in `streamlit_app.py`
4. Update database schema if needed

### Adding New File Format

1. Add parser method in `core/document_parser.py`:
```python
@staticmethod
def parse_xlsx(file_path):
    # Implementation
    pass
```

2. Update `parse_file()` method
3. Add to SUPPORTED_EXTENSIONS in settings

## Performance Considerations

- **Caching**: Consider adding response caching for repeated content
- **Batch Processing**: Process multiple documents in parallel
- **Database Indexing**: Add indexes for frequently queried columns
- **Memory Management**: Stream large PDFs instead of loading entirely
- **Rate Limiting**: Implement rate limiting for API calls

## Security Notes

- API keys stored in `.env` (git-ignored)
- No sensitive data in database
- All data stored locally
- No external data transmission except API calls
- Input validation on all file uploads

---

**This structure supports:**
- ✅ Easy maintenance and updates
- ✅ Clear separation of concerns
- ✅ Modular and extensible design
- ✅ Type hints and documentation
- ✅ Error handling throughout
- ✅ Scalability for future features
