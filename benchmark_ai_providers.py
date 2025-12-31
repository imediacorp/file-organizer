#!/usr/bin/env python3
"""
Benchmark AI providers for response times.
Tests the same task across all available providers and compares performance.
"""

import time
import sys
from pathlib import Path
from typing import Dict, List, Any

try:
    from file_organizer.ai.unified_client import AIProvider, get_ai_suggestion, get_provider_status
    from file_organizer.utils.ai_advisory import classify_document
except ImportError as e:
    print(f"Error: Could not import AI modules: {e}")
    sys.exit(1)


def test_provider(
    provider_name: str,
    test_payload: Dict[str, Any],
    test_file: Path = None
) -> Dict[str, Any]:
    """Test a single provider and return timing and result info."""
    print(f"\n{'='*60}")
    print(f"Testing: {provider_name.upper()}")
    print(f"{'='*60}")
    
    start_time = time.time()
    result = None
    error = None
    
    try:
        if test_file:
            # Use classify_document for file-based test
            result = classify_document(test_file, provider=provider_name)
            success = result.get("success", False)
            if not success:
                error = result.get("error", "Unknown error")
        else:
            # Use direct AI suggestion
            result = get_ai_suggestion(
                test_payload,
                provider=provider_name,
                use_cache=False,  # Disable cache for fair comparison
                return_text=False
            )
            success = result.get("ok", False)
            if not success:
                error = result.get("error", "Unknown error")
        
        elapsed = time.time() - start_time
        
        return {
            "provider": provider_name,
            "success": success,
            "elapsed_seconds": elapsed,
            "error": error,
            "response_length": len(str(result).encode("utf-8")) if result else 0,
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "provider": provider_name,
            "success": False,
            "elapsed_seconds": elapsed,
            "error": str(e),
            "response_length": 0,
        }


def benchmark_providers(test_type: str = "simple", test_file: Path = None):
    """Benchmark all available providers."""
    
    print("\n" + "="*80)
    print("AI PROVIDER BENCHMARK")
    print("="*80)
    
    # Check provider status
    print("\nChecking provider availability...")
    status = get_provider_status()
    
    available_providers = []
    for provider_name, provider_status in status.items():
        if provider_status.get("available") or provider_status.get("configured"):
            available_providers.append(provider_name)
            print(f"  ✅ {provider_name}: Available")
        else:
            print(f"  ❌ {provider_name}: Not available")
    
    if not available_providers:
        print("\n❌ No providers available! Check your configuration.")
        return
    
    # Create test payload
    if test_type == "simple":
        test_payload = {
            "system_prompt": "You are a helpful assistant. Respond briefly.",
            "request": "Classify this document: 'Invoice_2024_Q1.pdf'. Provide a one-sentence classification.",
        }
    elif test_type == "file_organization":
        test_payload = {
            "system_prompt": "You are Eratosthenes, a Library Science Expert. Help organize files.",
            "request": "Suggest a folder structure for organizing these files:\n- Invoice_2024_Q1.pdf\n- Meeting_Notes_March.docx\n- Project_Proposal_2024.pdf\n- Receipt_Gas_Station.pdf",
            "instructions": "Provide a brief folder structure suggestion.",
        }
    else:
        test_payload = {
            "system_prompt": "You are a helpful assistant.",
            "request": "What is 2+2? Respond with just the number.",
        }
    
    # Test each provider
    results = []
    
    # Test AUTO mode first
    if "auto" not in [p.lower() for p in available_providers]:
        print("\nTesting AUTO mode (will select best available provider)...")
        result = test_provider("auto", test_payload, test_file)
        results.append(result)
    
    # Test individual providers
    for provider in available_providers:
        if provider.lower() != "auto":
            result = test_provider(provider, test_payload, test_file)
            results.append(result)
    
    # Display results
    print("\n" + "="*80)
    print("BENCHMARK RESULTS")
    print("="*80)
    
    # Sort by elapsed time
    results.sort(key=lambda x: x["elapsed_seconds"])
    
    print(f"\n{'Provider':<15} {'Status':<10} {'Time (s)':<12} {'Response Size':<15} {'Error'}")
    print("-" * 80)
    
    fastest = None
    for result in results:
        status_icon = "✅" if result["success"] else "❌"
        status_text = "Success" if result["success"] else "Failed"
        time_str = f"{result['elapsed_seconds']:.2f}s"
        
        if result["success"] and (fastest is None or result["elapsed_seconds"] < fastest["elapsed_seconds"]):
            fastest = result
        
        response_size = f"{result['response_length']} bytes" if result["success"] else "N/A"
        error_str = result.get("error", "")[:40] if result.get("error") else ""
        
        print(f"{result['provider']:<15} {status_icon} {status_text:<6} {time_str:<12} {response_size:<15} {error_str}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    successful = [r for r in results if r["success"]]
    if successful:
        avg_time = sum(r["elapsed_seconds"] for r in successful) / len(successful)
        fastest_provider = min(successful, key=lambda x: x["elapsed_seconds"])
        slowest_provider = max(successful, key=lambda x: x["elapsed_seconds"])
        
        print(f"\n✅ Successful providers: {len(successful)}/{len(results)}")
        print(f"⚡ Fastest: {fastest_provider['provider']} ({fastest_provider['elapsed_seconds']:.2f}s)")
        print(f"🐌 Slowest: {slowest_provider['provider']} ({slowest_provider['elapsed_seconds']:.2f}s)")
        print(f"📊 Average time: {avg_time:.2f}s")
        
        if len(successful) > 1:
            speedup = slowest_provider['elapsed_seconds'] / fastest_provider['elapsed_seconds']
            print(f"🚀 Speedup: {speedup:.2f}x faster ({fastest_provider['provider']} vs {slowest_provider['provider']})")
    else:
        print("\n❌ No providers succeeded. Check your configuration and network connection.")
    
    failed = [r for r in results if not r["success"]]
    if failed:
        print(f"\n❌ Failed providers: {len(failed)}")
        for result in failed:
            print(f"   - {result['provider']}: {result.get('error', 'Unknown error')}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Benchmark AI providers for response times"
    )
    parser.add_argument(
        "--test-type",
        choices=["simple", "file_organization", "math"],
        default="simple",
        help="Type of test to run"
    )
    parser.add_argument(
        "--file",
        type=Path,
        help="Test file for classification (optional)"
    )
    
    args = parser.parse_args()
    
    benchmark_providers(test_type=args.test_type, test_file=args.file)


if __name__ == "__main__":
    main()

