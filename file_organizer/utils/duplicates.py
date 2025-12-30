"""
Duplicate file detection utility.
"""

import hashlib
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
from difflib import SequenceMatcher


class DuplicateFinder:
    """
    Find duplicate files, similar names, and version patterns in a directory tree.
    """
    
    def __init__(self, root_path: Path, hash_large_files: bool = False, 
                 max_file_size_mb: float = 50, skip_dirs: Optional[List[str]] = None):
        """
        Initialize duplicate finder.
        
        Args:
            root_path: Root directory to analyze
            hash_large_files: If True, hash large files (default: False for performance)
            max_file_size_mb: Maximum file size in MB to hash (default: 50)
            skip_dirs: List of directory names to skip
        """
        self.root_path = Path(root_path).resolve()
        self.hash_large_files = hash_large_files
        self.max_file_size_mb = max_file_size_mb
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024
        self.skip_dirs = skip_dirs or ["00-Index"]
        
        self.duplicates_by_hash = defaultdict(list)
        self.duplicates_by_name = defaultdict(list)
        self.file_count = 0
        self.processed_count = 0
        self.results = {
            'exact_duplicates': [],
            'name_duplicates': [],
            'similar_names': [],
            'version_files': [],
            'large_files': [],
            'old_files': [],
            'summary': {}
        }
    
    def calculate_file_hash(self, file_path: Path, chunk_size: int = 8192) -> Optional[str]:
        """
        Calculate MD5 hash of a file.
        
        Args:
            file_path: Path to file
            chunk_size: Chunk size for reading file
            
        Returns:
            MD5 hash string or None if file couldn't be hashed
        """
        try:
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size_bytes and not self.hash_large_files:
                return None  # Skip hashing large files for performance
            
            hash_md5 = hashlib.md5()
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (IOError, PermissionError, OSError):
            return None
    
    def get_file_info(self, file_path: Path) -> Optional[Dict]:
        """Get file information."""
        try:
            stat = file_path.stat()
            return {
                'path': str(file_path.relative_to(self.root_path)),
                'name': file_path.name,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            }
        except (OSError, PermissionError):
            return None
    
    def find_version_patterns(self, filename: str) -> List[tuple]:
        """Identify version patterns in filenames."""
        patterns = []
        
        # Pattern: filename (1).ext, filename (2).ext
        match = re.search(r'\((\d+)\)', filename)
        if match:
            patterns.append(('numbered', int(match.group(1)), match.group(0)))
        
        # Pattern: filename_1.ext, filename_2.ext
        match = re.search(r'_(\d+)(?:\.[^.]+)?$', filename)
        if match:
            patterns.append(('underscore', int(match.group(1)), match.group(0)))
        
        # Pattern: filename - Copy.ext, filename - Copy (1).ext
        if ' - Copy' in filename or ' copy' in filename.lower():
            patterns.append(('copy', None, 'Copy'))
        
        # Pattern: filename_duplicate_N.ext
        match = re.search(r'_duplicate_(\d+)', filename)
        if match:
            patterns.append(('duplicate', int(match.group(1)), match.group(0)))
        
        # Pattern: filename_v1.ext, filename_v2.ext
        match = re.search(r'[vV](\d+)', filename)
        if match:
            patterns.append(('versioned', int(match.group(1)), match.group(0)))
        
        # Pattern: filename.old, filename.bak
        if filename.endswith('.old') or filename.endswith('.bak'):
            patterns.append(('backup', None, 'backup'))
        
        return patterns
    
    def similarity_ratio(self, name1: str, name2: str) -> float:
        """Calculate similarity ratio between two filenames."""
        base1 = Path(name1).stem.lower()
        base2 = Path(name2).stem.lower()
        return SequenceMatcher(None, base1, base2).ratio()
    
    def format_size(self, size_bytes: float) -> str:
        """Convert bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def scan_directory(self, folder_path: Path, max_depth: int = 10, current_depth: int = 0, 
                      progress_callback: Optional[callable] = None):
        """Recursively scan directory for files."""
        if current_depth >= max_depth:
            return
        
        if folder_path.name.startswith('.'):
            return
        
        if folder_path.name in self.skip_dirs:
            return
        
        # Skip _by_type_ folders to avoid noise
        if '_by_type_' in folder_path.name:
            return
        
        try:
            items = list(folder_path.iterdir())
            for item in items:
                if item.name.startswith('.'):
                    continue
                
                if item.is_file():
                    self.file_count += 1
                    if progress_callback and self.file_count % 100 == 0:
                        progress_callback(self.file_count)
                    
                    file_info = self.get_file_info(item)
                    if not file_info:
                        continue
                    
                    self.processed_count += 1
                    
                    # Only hash files that might be duplicates (smaller files or if enabled)
                    file_size = file_info['size']
                    if file_size <= self.max_file_size_bytes or self.hash_large_files:
                        file_hash = self.calculate_file_hash(item)
                        if file_hash:
                            self.duplicates_by_hash[file_hash].append(file_info)
                    
                    # Group by base name (without version numbers)
                    base_name = re.sub(r'[\(\s_-]*(?:copy|duplicate|v\d+|\d+)[\)\s_-]*', '', 
                                      Path(item.stem).stem.lower())
                    self.duplicates_by_name[base_name].append(file_info)
                    
                    # Find version patterns
                    version_patterns = self.find_version_patterns(item.name)
                    if version_patterns:
                        self.results['version_files'].append({
                            **file_info,
                            'patterns': version_patterns
                        })
                    
                    # Track large files (>100MB)
                    if file_size > 100 * 1024 * 1024:
                        self.results['large_files'].append(file_info)
                    
                    # Track old files (not modified in 5+ years)
                    modified_date = datetime.fromisoformat(file_info['modified'])
                    years_old = (datetime.now() - modified_date).days / 365.25
                    if years_old > 5:
                        self.results['old_files'].append({
                            **file_info,
                            'years_old': round(years_old, 1)
                        })
                
                elif item.is_dir():
                    self.scan_directory(item, max_depth, current_depth + 1, progress_callback)
        
        except (PermissionError, OSError) as e:
            print(f"Warning: Could not access {folder_path}: {e}")
    
    def analyze_duplicates(self):
        """Analyze duplicate files."""
        # Exact duplicates (same hash)
        for file_hash, files in self.duplicates_by_hash.items():
            if len(files) > 1:
                self.results['exact_duplicates'].append({
                    'hash': file_hash,
                    'count': len(files),
                    'size': files[0]['size'],
                    'files': files
                })
        
        # Name-based duplicates (same base name)
        for base_name, files in self.duplicates_by_name.items():
            if len(files) > 1:
                # Group by similar names
                unique_names = {}
                for file_info in files:
                    name_key = Path(file_info['name']).stem.lower()
                    if name_key not in unique_names:
                        unique_names[name_key] = []
                    unique_names[name_key].append(file_info)
                
                if len(unique_names) > 1:
                    self.results['name_duplicates'].append({
                        'base_name': base_name,
                        'count': len(files),
                        'variants': unique_names
                    })
    
    def find_similar_names(self, threshold: float = 0.8, max_comparisons: int = 10000):
        """Find files with similar names."""
        # Collect all unique files
        all_files = []
        seen_paths = set()
        for file_hash, files in self.duplicates_by_hash.items():
            for file_info in files:
                if file_info['path'] not in seen_paths:
                    all_files.append(file_info)
                    seen_paths.add(file_info['path'])
        
        # If too many files, only compare within name-based groups
        if len(all_files) > 200:
            # Group by base name first
            name_groups = defaultdict(list)
            for file_info in all_files:
                base_name = re.sub(r'[\(\s_-]*(?:copy|duplicate|v\d+|\d+)[\)\s_-]*', '', 
                                  Path(file_info['name']).stem.lower())
                name_groups[base_name].append(file_info)
            
            # Only compare within groups
            comparisons = 0
            for base_name, files in name_groups.items():
                if len(files) > 1 and comparisons < max_comparisons:
                    for i, file1 in enumerate(files):
                        for file2 in files[i+1:]:
                            if comparisons >= max_comparisons:
                                break
                            comparisons += 1
                            similarity = self.similarity_ratio(file1['name'], file2['name'])
                            if similarity >= threshold and file1['path'] != file2['path']:
                                self.results['similar_names'].append({
                                    'file1': file1,
                                    'file2': file2,
                                    'similarity': round(similarity, 2)
                                })
                        if comparisons >= max_comparisons:
                            break
        else:
            # Small set, compare all pairs
            for i, file1 in enumerate(all_files):
                for file2 in all_files[i+1:]:
                    similarity = self.similarity_ratio(file1['name'], file2['name'])
                    if similarity >= threshold and file1['path'] != file2['path']:
                        # Check if not already in exact duplicates
                        is_duplicate = False
                        for dup_group in self.results['exact_duplicates']:
                            if (file1['path'] in [f['path'] for f in dup_group['files']] and
                                file2['path'] in [f['path'] for f in dup_group['files']]):
                                is_duplicate = True
                                break
                        
                        if not is_duplicate:
                            self.results['similar_names'].append({
                                'file1': file1,
                                'file2': file2,
                                'similarity': round(similarity, 2)
                            })
    
    def generate_report(self) -> str:
        """Generate a human-readable report."""
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("FILE VERSION ANALYSIS REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # Summary
        report_lines.append("SUMMARY")
        report_lines.append("-" * 80)
        report_lines.append(f"Exact Duplicates (same content): {len(self.results['exact_duplicates'])} groups")
        report_lines.append(f"Name Duplicates (similar names): {len(self.results['name_duplicates'])} groups")
        report_lines.append(f"Similar Names (>80% similarity): {len(self.results['similar_names'])} pairs")
        report_lines.append(f"Files with Version Patterns: {len(self.results['version_files'])}")
        report_lines.append(f"Large Files (>100MB): {len(self.results['large_files'])}")
        report_lines.append(f"Old Files (5+ years): {len(self.results['old_files'])}")
        report_lines.append("")
        
        # Exact Duplicates
        if self.results['exact_duplicates']:
            report_lines.append("EXACT DUPLICATES (Same Content)")
            report_lines.append("-" * 80)
            for i, dup_group in enumerate(self.results['exact_duplicates'][:20], 1):
                report_lines.append(f"\nGroup {i}: {dup_group['count']} identical files ({self.format_size(dup_group['size'])})")
                for file_info in dup_group['files']:
                    report_lines.append(f"  - {file_info['path']}")
                    report_lines.append(f"    Modified: {file_info['modified']}")
            if len(self.results['exact_duplicates']) > 20:
                report_lines.append(f"\n... and {len(self.results['exact_duplicates']) - 20} more groups")
            report_lines.append("")
        
        # Version Files
        if self.results['version_files']:
            report_lines.append("FILES WITH VERSION PATTERNS")
            report_lines.append("-" * 80)
            for file_info in self.results['version_files'][:30]:
                patterns_str = ', '.join([f"{p[0]}:{p[2]}" for p in file_info['patterns']])
                report_lines.append(f"  {file_info['path']}")
                report_lines.append(f"    Patterns: {patterns_str}")
            if len(self.results['version_files']) > 30:
                report_lines.append(f"\n... and {len(self.results['version_files']) - 30} more files")
            report_lines.append("")
        
        # Large Files
        if self.results['large_files']:
            report_lines.append("LARGE FILES (>100MB)")
            report_lines.append("-" * 80)
            sorted_large = sorted(self.results['large_files'], key=lambda x: x['size'], reverse=True)
            for file_info in sorted_large[:20]:
                report_lines.append(f"  {self.format_size(file_info['size']):>10} - {file_info['path']}")
            if len(self.results['large_files']) > 20:
                report_lines.append(f"\n... and {len(self.results['large_files']) - 20} more files")
            report_lines.append("")
        
        # Old Files
        if self.results['old_files']:
            report_lines.append("OLD FILES (Not Modified in 5+ Years)")
            report_lines.append("-" * 80)
            sorted_old = sorted(self.results['old_files'], key=lambda x: x['years_old'], reverse=True)
            for file_info in sorted_old[:20]:
                report_lines.append(f"  {file_info['years_old']:>5.1f} years - {file_info['path']}")
            if len(self.results['old_files']) > 20:
                report_lines.append(f"\n... and {len(self.results['old_files']) - 20} more files")
            report_lines.append("")
        
        return "\n".join(report_lines)
    
    def analyze(self, output_json: Optional[Path] = None, output_report: Optional[Path] = None) -> Dict:
        """
        Run the complete analysis.
        
        Args:
            output_json: Optional path to save JSON results
            output_report: Optional path to save text report
            
        Returns:
            Dictionary with analysis results
        """
        print(f"Scanning: {self.root_path}")
        print(f"Max file size for hashing: {self.max_file_size_mb}MB (larger files skipped unless hash_large_files is used)")
        
        def progress_callback(count):
            print(f"  Processed {count} files...", end='\r')
        
        self.scan_directory(self.root_path, progress_callback=progress_callback)
        print(f"\n  Found {self.file_count} files, processed {self.processed_count}")
        
        print("Analyzing duplicates...")
        self.analyze_duplicates()
        
        print("Finding similar file names...")
        self.find_similar_names()
        
        # Generate summary
        self.results['summary'] = {
            'total_exact_duplicates': len(self.results['exact_duplicates']),
            'total_name_duplicates': len(self.results['name_duplicates']),
            'total_similar_names': len(self.results['similar_names']),
            'total_version_files': len(self.results['version_files']),
            'total_large_files': len(self.results['large_files']),
            'total_old_files': len(self.results['old_files']),
            'total_files_scanned': self.file_count,
            'analysis_date': datetime.now().isoformat(),
            'analyzed_path': str(self.root_path)
        }
        
        # Save JSON results
        if output_json:
            print(f"Saving results to {output_json}...")
            with open(output_json, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2)
        
        # Generate and save report
        if output_report:
            print(f"Generating report...")
            report = self.generate_report()
            with open(output_report, 'w', encoding='utf-8') as f:
                f.write(report)
        
        print("\nAnalysis complete!")
        if output_json:
            print(f"Results saved to: {output_json}")
        if output_report:
            print(f"Report saved to: {output_report}")
        
        return self.results
    
    def export_csv(self, output_path: Path, duplicate_type: str = 'exact'):
        """
        Export duplicate information to CSV format.
        
        Args:
            output_path: Path to save CSV file
            duplicate_type: Type of duplicates to export ('exact', 'name', 'similar')
        """
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if duplicate_type == 'exact':
                writer.writerow(['Group', 'Hash', 'Count', 'Size', 'File Path', 'Modified Date'])
                for i, dup_group in enumerate(self.results['exact_duplicates'], 1):
                    for file_info in dup_group['files']:
                        writer.writerow([
                            i, dup_group['hash'], dup_group['count'],
                            dup_group['size'], file_info['path'], file_info['modified']
                        ])
            elif duplicate_type == 'name':
                writer.writerow(['Base Name', 'Count', 'Variant', 'File Path', 'Size', 'Modified Date'])
                for dup_group in self.results['name_duplicates']:
                    for variant_name, files in dup_group['variants'].items():
                        for file_info in files:
                            writer.writerow([
                                dup_group['base_name'], dup_group['count'], variant_name,
                                file_info['path'], file_info['size'], file_info['modified']
                            ])
            elif duplicate_type == 'similar':
                writer.writerow(['File 1', 'File 2', 'Similarity', 'Size 1', 'Size 2'])
                for pair in self.results['similar_names']:
                    writer.writerow([
                        pair['file1']['path'], pair['file2']['path'], pair['similarity'],
                        pair['file1']['size'], pair['file2']['size']
                    ])

