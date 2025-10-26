# 🚀 Quick Start Guide

Get StudyAI running in 5 minutes!

## Step 1: Get Your API Keys

### Groq API Key (Already Have It!)

### OpenAI API Key (Optional but Recommended)
1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

## Step 2: Setup

### Option A: Using Setup Script (Recommended)
```bash
chmod +x setup.sh
./setup.sh
```

### Option B: Manual Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p data output temp config core database utils

# Create module files
touch config/__init__.py core/__init__.py database/__init__.py utils/__init__.py

# Setup environment
cp .env.example .env
```

## Step 3: Configure API Keys

Edit the `.env` file:
```bash
nano .env  # or use any text editor
```

Add your keys:
```
OPENAI_API_KEY=sk-your-openai-key-here
GROQ_API_KEY=inputopenaikey
```

Save and exit.

## Step 4: Test It Out!

### Try the CLI (Fastest Test)

Create a sample text file:
```bash
echo "Photosynthesis is the process by which plants convert light energy into chemical energy. It occurs in chloroplasts and produces glucose and oxygen." > sample.txt
```

Generate flashcards:
```bash
python studyai.py generate --input sample.txt --output flashcards --count 5
```

Expected output:
```
✓ Parsed TXT file successfully
  Words: 25 | Characters: 156

Generating flashcards with Groq...

Generated 5 Flashcards:

╭─ Flashcard 1 ─────────────────╮
│ Q: What is photosynthesis?    │
│                               │
│ A: The process by which...    │
│                               │
│ Topic: Biology | Difficulty...│
╰───────────────────────────────╯
```

### Try the Dashboard

```bash
streamlit run streamlit_app.py
```

Your browser will open to `http://localhost:8501`

## Step 5: Explore Features

### Generate Different Materials

**Quiz:**
```bash
python studyai.py generate --input sample.txt --output quiz --count 3
```

**Summary:**
```bash
python studyai.py generate --input sample.txt --output summary
```

**Everything:**
```bash
python studyai.py generate --input sample.txt --output all --save
```

### Compare AI Providers

```bash
python studyai.py generate --input sample.txt --output flashcards --benchmark
```

This will show you side-by-side comparison of OpenAI vs Groq!

### View Benchmarks

```bash
python studyai.py benchmark
```

### Create Concept Maps

```bash
python studyai.py concept-map --input sample.txt
```

Opens an interactive HTML visualization!

## Common Commands Reference

```bash
# CLI Help
python studyai.py --help
python studyai.py generate --help

# Generate with specific provider
python studyai.py generate -i file.pdf -o flashcards -p groq

# Save to database
python studyai.py generate -i file.pdf -o all --save

# List saved documents
python studyai.py list

# View benchmarks for document
python studyai.py benchmark --doc-id 1

# Create concept map
python studyai.py concept-map -i file.pdf -o concept.html
```

## Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "API key not found" error
Check your `.env` file has the correct format (no quotes, no spaces)

### "File not found" error
Make sure you're in the studyai directory and the file path is correct

### Database errors
```bash
rm data/studyai.db  # Delete and recreate
```

## Next Steps

1. ✅ Try uploading your own PDF/DOCX files
2. ✅ Experiment with different AI providers
3. ✅ Check out the Streamlit dashboard
4. ✅ Run benchmarks to compare performance
5. ✅ Create concept maps from your study materials

## Need Help?

- Check README.md for detailed documentation
- Review .env.example for configuration options
- Make sure all dependencies are installed
- Verify API keys are valid and have credits

---

**You're all set! Start generating study materials! 🎓✨**
