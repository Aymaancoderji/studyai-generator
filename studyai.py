#!/usr/bin/env python3
"""
StudyAI CLI Tool - Generate study materials using AI
"""

import click
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from config.settings import validate_config
from core.document_parser import DocumentParser
from core.ai_providers import get_provider, get_all_providers
from core.generator import StudyMaterialGenerator
from core.benchmarking import BenchmarkRunner
from database.db_manager import DatabaseManager
from utils.concept_mapper import ConceptMapper
from utils.scoring import CrossAPIScorer

console = Console()

@click.group()
def cli():
    """StudyAI: AI-Powered Study Tools Generator"""
    try:
        validate_config()
    except ValueError as e:
        console.print(Panel.fit(
        "[bold cyan]StudyAI Generator[/bold cyan]\n"
        f"Input: {input}\n"
        f"Output: {output}\n"
        f"Provider: {provider}",
        title="Configuration"
    ))
    
    # Parse input file
    try:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Parsing document...", total=None)
            content, file_type = DocumentParser.parse_file(input)
            progress.update(task, completed=True)
        
        console.print(f"[green]✓[/green] Parsed {file_type.upper()} file successfully")
        
        # Get content stats
        stats = DocumentParser.get_content_stats(content)
        console.print(f"  Words: {stats['word_count']} | Characters: {stats['character_count']}")
        
    except Exception as e:
        console.print(f"[bold red]Error parsing file:[/bold red] {e}")
        return
    
    # Save to database if requested
    db = DatabaseManager() if save else None
    doc_id = None
    
    if save:
        doc_id = db.save_document(Path(input).name, content, file_type)
        console.print(f"[green]✓[/green] Saved to database (ID: {doc_id})")
    
    # Run benchmark mode
    if benchmark or provider == 'all':
        console.print("\n[bold yellow]Running Benchmark Comparison...[/bold yellow]\n")
        
        runner = BenchmarkRunner(db)
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Benchmarking providers...", total=None)
            results = runner.run_comprehensive_benchmark(content, doc_id)
            progress.update(task, completed=True)
        
        # Display results
        display_benchmark_results(results, output)
        
        # Generate comparison report
        if doc_id:
            report = runner.generate_comparison_report(doc_id)
            display_comparison_report(report)
        
        return
    
    # Single provider mode
    try:
        ai_provider = get_provider(provider)
        generator = StudyMaterialGenerator(ai_provider)
        
        console.print(f"\n[bold yellow]Generating {output} with {provider.title()}...[/bold yellow]\n")
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Generating...", total=None)
            
            if output == 'flashcards':
                result = generator.generate_flashcards(content, count)
                display_flashcards(result)
            elif output == 'quiz':
                result = generator.generate_quiz(content, count)
                display_quiz(result)
            elif output == 'summary':
                result = generator.generate_summary(content)
                display_summary(result)
            elif output == 'all':
                flashcards = generator.generate_flashcards(content, count)
                quiz = generator.generate_quiz(content, count // 2)
                summary = generator.generate_summary(content)
                
                display_flashcards(flashcards)
                display_quiz(quiz)
                display_summary(summary)
                
                result = {'flashcards': flashcards, 'quiz': quiz, 'summary': summary}
            
            progress.update(task, completed=True)
        
        # Save to database
        if save and doc_id:
            if output == 'all':
                db.save_study_material(doc_id, 'flashcards', flashcards, provider, ai_provider.model)
                db.save_study_material(doc_id, 'quiz', quiz, provider, ai_provider.model)
                db.save_study_material(doc_id, 'summary', summary, provider, ai_provider.model)
            else:
                db.save_study_material(doc_id, output, result, provider, ai_provider.model)
            
            console.print(f"\n[green]✓[/green] Saved study materials to database")
        
        # Display metrics
        if 'metrics' in result:
            display_metrics(result['metrics'])
        
        console.print(f"\n[bold green]✓ Generated {output} successfully![/bold green]")
        
    except Exception as e:
        console.print(f"[bold red]Error generating content:[/bold red] {e}")

@cli.command()
@click.option('--doc-id', '-d', type=int, help='Document ID to analyze')
def benchmark(doc_id):
    """View benchmark comparison reports."""
    
    db = DatabaseManager()
    benchmarks = db.get_benchmarks(doc_id)
    
    if not benchmarks:
        console.print("[yellow]No benchmark data available.[/yellow]")
        return
    
    console.print(Panel.fit(
        "[bold cyan]Benchmark Analysis[/bold cyan]",
        title="StudyAI"
    ))
    
    # Create comparison DataFrame
    df = CrossAPIScorer.compare_providers(benchmarks)
    
    # Display table
    table = Table(title="Provider Comparison", show_header=True, header_style="bold cyan")
    
    for col in df.columns:
        table.add_column(col)
    
    for _, row in df.iterrows():
        table.add_row(*[str(val) for val in row])
    
    console.print(table)
    
    # Category winners
    winners = CrossAPIScorer.generate_winner_by_category(benchmarks)
    
    console.print("\n[bold]Category Winners:[/bold]")
    for category, data in winners.items():
        console.print(f"  {category}: [green]{data['provider']}[/green] ({data['value']})")
    
    # Recommendation
    recommendation = CrossAPIScorer.generate_recommendation(benchmarks)
    console.print(f"\n{recommendation}")

@cli.command()
@click.option('--input', '-i', required=True, help='Input file path')
@click.option('--provider', '-p', default='groq', help='AI provider to use')
@click.option('--output', '-o', help='Output file path (HTML)')
def concept_map(input, provider, output):
    """Generate a visual concept map from content."""
    
    console.print(Panel.fit(
        "[bold cyan]Concept Map Generator[/bold cyan]",
        title="StudyAI"
    ))
    
    # Parse document
    try:
        content, file_type = DocumentParser.parse_file(input)
        console.print(f"[green]✓[/green] Parsed {file_type.upper()} file")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return
    
    # Extract concepts
    try:
        ai_provider = get_provider(provider)
        mapper = ConceptMapper(ai_provider)
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Extracting concepts...", total=None)
            concepts_data = mapper.extract_concepts(content)
            progress.update(task, completed=True)
        
        if 'error' in concepts_data:
            console.print(f"[bold red]Error extracting concepts:[/bold red] {concepts_data['error']}")
            return
        
        console.print(f"[green]✓[/green] Extracted {len(concepts_data.get('concepts', []))} concepts")
        
        # Generate text summary
        summary = mapper.generate_text_summary(concepts_data)
        console.print(f"\n{summary}")
        
        # Create visualization
        fig = mapper.create_network_graph(concepts_data)
        
        # Save to file
        if output:
            output_path = Path(output)
        else:
            output_path = Path('output') / f"concept_map_{Path(input).stem}.html"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.write_html(str(output_path))
        
        console.print(f"\n[green]✓[/green] Saved concept map to: [cyan]{output_path}[/cyan]")
        console.print("[yellow]Tip:[/yellow] Open the HTML file in your browser to view the interactive concept map")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@cli.command()
def list():
    """List all documents in the database."""
    
    db = DatabaseManager()
    documents = db.get_all_documents()
    
    if not documents:
        console.print("[yellow]No documents found in database.[/yellow]")
        return
    
    table = Table(title="Saved Documents", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="cyan")
    table.add_column("Filename", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Preview")
    table.add_column("Created")
    
    for doc in documents:
        table.add_row(
            str(doc['id']),
            doc['filename'],
            doc['file_type'].upper(),
            doc['content'][:50] + "...",
            doc['created_at']
        )
    
    console.print(table)

def display_flashcards(result: dict):
    """Display flashcards in a formatted table."""
    if 'error' in result or 'flashcards' not in result:
        console.print(f"[bold red]Error generating flashcards[/bold red]")
        return
    
    flashcards = result['flashcards']
    
    console.print(f"\n[bold cyan]Generated {len(flashcards)} Flashcards:[/bold cyan]\n")
    
    for i, card in enumerate(flashcards[:10], 1):  # Show first 10
        console.print(Panel(
            f"[bold]Q:[/bold] {card.get('question', 'N/A')}\n\n"
            f"[bold]A:[/bold] {card.get('answer', 'N/A')}\n\n"
            f"[dim]Topic: {card.get('topic', 'N/A')} | "
            f"Difficulty: {card.get('difficulty', 'N/A')}[/dim]",
            title=f"Flashcard {i}",
            border_style="cyan"
        ))
    
    if len(flashcards) > 10:
        console.print(f"\n[dim]... and {len(flashcards) - 10} more flashcards[/dim]")

def display_quiz(result: dict):
    """Display quiz questions."""
    if 'error' in result or 'quiz' not in result:
        console.print(f"[bold red]Error generating quiz[/bold red]")
        return
    
    quiz = result['quiz']
    
    console.print(f"\n[bold cyan]Generated {len(quiz)} Quiz Questions:[/bold cyan]\n")
    
    for i, q in enumerate(quiz[:5], 1):  # Show first 5
        options_text = "\n".join([f"  {chr(65+j)}. {opt}" for j, opt in enumerate(q.get('options', []))])
        correct_letter = chr(65 + q.get('correct_answer', 0))
        
        console.print(Panel(
            f"[bold]{q.get('question', 'N/A')}[/bold]\n\n"
            f"{options_text}\n\n"
            f"[green]Correct Answer: {correct_letter}[/green]\n"
            f"[dim]{q.get('explanation', 'N/A')}[/dim]",
            title=f"Question {i}",
            border_style="green"
        ))
    
    if len(quiz) > 5:
        console.print(f"\n[dim]... and {len(quiz) - 5} more questions[/dim]")

def display_summary(result: dict):
    """Display summary."""
    if 'error' in result or 'summary' not in result:
        console.print(f"[bold red]Error generating summary[/bold red]")
        return
    
    console.print(Panel(
        f"[bold]Summary:[/bold]\n\n{result.get('summary', 'N/A')}\n\n"
        f"[bold]Key Points:[/bold]\n" + 
        "\n".join([f"• {point}" for point in result.get('key_points', [])]),
        title="Content Summary",
        border_style="yellow"
    ))

def display_metrics(metrics: dict):
    """Display generation metrics."""
    table = Table(title="Generation Metrics", show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Provider", metrics.get('provider', 'N/A').title())
    table.add_row("Model", metrics.get('model', 'N/A'))
    table.add_row("Response Time", f"{metrics.get('response_time', 0):.3f}s")
    table.add_row("Token Usage", str(metrics.get('token_usage', 0)))
    table.add_row("Cost", f"${metrics.get('cost', 0):.6f}")
    
    console.print("\n")
    console.print(table)

def display_benchmark_results(results: dict, output_type: str):
    """Display benchmark comparison results."""
    
    for material_type in ['flashcards', 'quiz', 'summary']:
        if material_type not in results:
            continue
        
        if output_type != 'all' and material_type != output_type:
            continue
        
        console.print(f"\n[bold cyan]Benchmark: {material_type.title()}[/bold cyan]")
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Provider", style="cyan")
        table.add_column("Response Time", style="yellow")
        table.add_column("Tokens", style="blue")
        table.add_column("Cost", style="green")
        
        for provider, result in results[material_type].items():
            if 'error' in result:
                table.add_row(provider.title(), "[red]Error[/red]", "-", "-")
            elif 'metrics' in result:
                m = result['metrics']
                table.add_row(
                    provider.title(),
                    f"{m.get('response_time', 0):.3f}s",
                    str(m.get('token_usage', 0)),
                    f"${m.get('cost', 0):.6f}"
                )
        
        console.print(table)

def display_comparison_report(report: dict):
    """Display comprehensive comparison report."""
    
    console.print("\n[bold cyan]Summary Statistics:[/bold cyan]")
    
    summary = report.get('summary', {})
    table = Table(show_header=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Total Requests", str(summary.get('total_requests', 0)))
    table.add_row("Total Cost", f"${summary.get('total_cost', 0):.4f}")
    table.add_row("Avg Response Time", f"{summary.get('avg_response_time', 0):.3f}s")
    table.add_row("Total Tokens", str(summary.get('total_tokens', 0)))
    table.add_row("Avg Quality Score", f"{summary.get('avg_quality_score', 0):.2f}/10")
    
    console.print(table)

if __name__ == '__main__':
    cli()f"[bold red]Configuration Error:[/bold red] {e}")
        console.print("\n[yellow]Please set up your .env file with API keys.[/yellow]")
        console.print("Copy .env.example to .env and add your keys.")
        exit(1)

@cli.command()
@click.option('--input', '-i', required=True, help='Input file path (PDF, TXT, DOCX)')
@click.option('--output', '-o', default='flashcards', 
              type=click.Choice(['flashcards', 'quiz', 'summary', 'all']),
              help='Type of study material to generate')
@click.option('--provider', '-p', default='groq',
              type=click.Choice(['openai', 'groq', 'all']),
              help='AI provider to use')
@click.option('--count', '-c', default=20, help='Number of flashcards/questions to generate')
@click.option('--benchmark', '-b', is_flag=True, help='Run benchmark comparison')
@click.option('--save', '-s', is_flag=True, help='Save to database')
def generate(input, output, provider, count, benchmark, save):
    """Generate study materials from input file."""
    
    console.print(
