#!/usr/bin/env python3
"""
Quick demo script to explore Eratosthenes AI functionality.
"""

import os
from pathlib import Path
from file_organizer.ai import get_ai_suggestion, AIProvider, get_provider_status
from file_organizer.ai.skills.library_science import get_library_science_skill
from file_organizer.utils.ai_advisory import classify_document, extract_metadata, suggest_filename

def main():
    print("=" * 70)
    print("ERATOSTHENES - Knowledge/Content Management Agent Demo")
    print("=" * 70)
    print()
    
    # Check provider status
    print("📡 AI Provider Status:")
    status = get_provider_status()
    for provider, info in status.items():
        if info.get("available") or info.get("healthy"):
            print(f"  ✓ {provider}: Available")
        else:
            print(f"  ✗ {provider}: Not available")
    print()
    
    # Show Eratosthenes skill info
    skill = get_library_science_skill()
    print("📚 Eratosthenes Skill Information:")
    print(f"  Name: {skill.metadata.name}")
    print(f"  Domain: {skill.metadata.domain}")
    print(f"  Version: {skill.metadata.version}")
    print(f"  Tags: {', '.join(skill.metadata.tags)}")
    print()
    
    # Test 1: Document Classification
    print("=" * 70)
    print("TEST 1: Document Classification")
    print("=" * 70)
    
    test_file = Path("04-Financial/Invoices & Receipts/Amazon Invoice.pdf")
    if test_file.exists():
        print(f"\nClassifying: {test_file}")
        result = classify_document(test_file, provider="ollama")
        if result.get("success"):
            classification = result.get("classification", {})
            print("\nClassification Result:")
            for key, value in classification.items():
                if key != "raw_response":
                    print(f"  {key}: {value}")
        else:
            print(f"Error: {result.get('error')}")
    else:
        print(f"Test file not found: {test_file}")
    print()
    
    # Test 2: Metadata Extraction
    print("=" * 70)
    print("TEST 2: Metadata Extraction")
    print("=" * 70)
    
    if test_file.exists():
        print(f"\nExtracting metadata from: {test_file}")
        result = extract_metadata(test_file, provider="ollama")
        if result.get("success"):
            metadata = result.get("metadata", {})
            print("\nExtracted Metadata:")
            for key, value in metadata.items():
                if key != "raw_response":
                    print(f"  {key}: {value}")
        else:
            print(f"Error: {result.get('error')}")
    print()
    
    # Test 3: Filename Suggestion
    print("=" * 70)
    print("TEST 3: Filename Suggestion")
    print("=" * 70)
    
    print("\nSuggesting better filename for: invoice.pdf")
    result = suggest_filename(
        Path("invoice.pdf"),
        content_hint="Invoice from Amazon dated January 15, 2024 for $150.00",
        provider="ollama"
    )
    if result.get("success"):
        suggestion = result.get("suggestion", {})
        print("\nFilename Suggestion:")
        for key, value in suggestion.items():
            if key != "raw_response":
                print(f"  {key}: {value}")
    else:
        print(f"Error: {result.get('error')}")
    print()
    
    # Test 4: Direct AI call with Eratosthenes skill
    print("=" * 70)
    print("TEST 4: Direct AI Call with Eratosthenes")
    print("=" * 70)
    
    payload = {
        "request": "suggest_organization",
        "domain": "library_science",
        "context": {
            "files": [
                {"name": "contract.pdf", "extension": ".pdf"},
                {"name": "invoice_2024.pdf", "extension": ".pdf"},
                {"name": "photo.jpg", "extension": ".jpg"},
            ]
        },
        "instructions": "Suggest how to organize these files following library science principles. Be concise."
    }
    
    print("\nRequesting organization suggestions...")
    result = get_ai_suggestion(payload, provider=AIProvider.OLLAMA, use_skills=True)
    
    if isinstance(result, dict) and result.get("ok"):
        print("\nEratosthenes Response:")
        print("-" * 70)
        print(result.get("text", "")[:600])
    else:
        print(f"Error: {result.get('error') if isinstance(result, dict) else str(result)[:200]}")
    
    print()
    print("=" * 70)
    print("Demo complete!")
    print("=" * 70)

if __name__ == "__main__":
    # Set model if available
    os.environ.setdefault("OLLAMA_MODEL", "llama3.1:latest")
    main()

