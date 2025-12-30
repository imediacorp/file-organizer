"""
Index generation utility for file trees.
"""

import os
import html
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict


class IndexGenerator:
    """
    Generate index files (Markdown and HTML) for a directory tree.
    """
    
    def __init__(self, root_path: Path, index_dir: Optional[Path] = None, skip_dirs: Optional[List[str]] = None):
        """
        Initialize index generator.
        
        Args:
            root_path: Root directory to index
            index_dir: Directory to save index files (default: root_path / "00-Index")
            skip_dirs: List of directory names to skip (default: ["00-Index"])
        """
        self.root_path = Path(root_path).resolve()
        self.index_dir = index_dir if index_dir else self.root_path / "00-Index"
        self.skip_dirs = skip_dirs or ["00-Index"]
        self.stats = {
            'total_files': 0,
            'total_dirs': 0,
            'file_types': defaultdict(int),
            'total_size': 0
        }
    
    def format_size(self, size_bytes: float) -> str:
        """Convert bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def get_file_info(self, file_path: Path) -> Optional[Dict]:
        """Get file information."""
        try:
            stat = file_path.stat()
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime)
            ext = file_path.suffix.lower() or 'no extension'
            return {
                'size': size,
                'modified': modified,
                'extension': ext
            }
        except (OSError, PermissionError):
            return None
    
    def scan_directory(self, path: Path, relative_path: str = "") -> Dict:
        """Recursively scan directory and build structure."""
        structure = {
            'name': path.name if relative_path else path.name,
            'path': relative_path,
            'files': [],
            'subdirs': {},
            'file_count': 0,
            'total_size': 0,
            'modified': None
        }
        
        try:
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
            
            for item in items:
                # Skip hidden files and system files
                if item.name.startswith('.'):
                    continue
                
                # Skip specified directories
                if item.name in self.skip_dirs:
                    continue
                
                if item.is_file():
                    info = self.get_file_info(item)
                    if info:
                        file_entry = {
                            'name': item.name,
                            'size': info['size'],
                            'modified': info['modified'],
                            'extension': info['extension']
                        }
                        structure['files'].append(file_entry)
                        structure['file_count'] += 1
                        structure['total_size'] += info['size']
                        self.stats['total_files'] += 1
                        self.stats['total_size'] += info['size']
                        self.stats['file_types'][info['extension']] += 1
                        
                        if not structure['modified'] or info['modified'] > structure['modified']:
                            structure['modified'] = info['modified']
                
                elif item.is_dir():
                    sub_relative = os.path.join(relative_path, item.name) if relative_path else item.name
                    sub_structure = self.scan_directory(item, sub_relative)
                    structure['subdirs'][item.name] = sub_structure
                    structure['file_count'] += sub_structure['file_count']
                    structure['total_size'] += sub_structure['total_size']
                    self.stats['total_dirs'] += 1
                    
                    if sub_structure['modified'] and (not structure['modified'] or sub_structure['modified'] > structure['modified']):
                        structure['modified'] = sub_structure['modified']
        
        except (PermissionError, OSError) as e:
            print(f"Warning: Could not access {path}: {e}")
        
        return structure
    
    def generate_markdown(self, structure: Dict, level: int = 0) -> List[str]:
        """Generate Markdown index."""
        lines = []
        indent = "  " * level
        
        # Directory header
        dir_name = structure['name']
        if level == 0:
            lines.append(f"# {dir_name} Index\n")
            lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
            lines.append("---\n")
        else:
            lines.append(f"{indent}- **{dir_name}/**")
            if structure['file_count'] > 0:
                lines[-1] += f" ({structure['file_count']} files, {self.format_size(structure['total_size'])})"
            lines[-1] += "\n"
        
        # Files in this directory
        if structure['files']:
            for file_info in sorted(structure['files'], key=lambda x: x['name'].lower()):
                file_name = file_info['name']
                file_size = self.format_size(file_info['size'])
                file_date = file_info['modified'].strftime('%Y-%m-%d')
                lines.append(f"{indent}  - `{file_name}` ({file_size}, {file_date})")
        
        # Subdirectories
        for subdir_name in sorted(structure['subdirs'].keys()):
            subdir_md = self.generate_markdown(structure['subdirs'][subdir_name], level + 1)
            lines.extend(subdir_md)
        
        return lines
    
    def _generate_tree_html(self, structure: Dict, level: int) -> List[str]:
        """Generate HTML tree structure recursively."""
        html_parts = []
        indent = "  " * level
        
        # Directory
        dir_name = html.escape(structure['name'])
        folder_id = f"folder_{id(structure)}"
        
        if level > 0:
            file_count = structure['file_count']
            total_size = self.format_size(structure['total_size'])
            html_parts.append(f'{indent}<div class="folder">\n')
            html_parts.append(f'{indent}  <div class="folder-name" onclick="toggleFolder(this)">{dir_name}/ <span style="color: #7f8c8d; font-size: 0.9em;">({file_count} files, {total_size})</span></div>\n')
            html_parts.append(f'{indent}  <div class="folder-content">\n')
        
        # Files
        for file_info in sorted(structure['files'], key=lambda x: x['name'].lower()):
            file_name = html.escape(file_info['name'])
            file_size = self.format_size(file_info['size'])
            file_date = file_info['modified'].strftime('%Y-%m-%d')
            file_ext = file_info['extension']
            html_parts.append(f'{indent}    <div class="file" data-extension="{file_ext}">{file_name}</div>\n')
            html_parts.append(f'{indent}    <div class="file-info">{file_size} • {file_date}</div>\n')
        
        # Subdirectories
        for subdir_name in sorted(structure['subdirs'].keys()):
            subdir_html = self._generate_tree_html(structure['subdirs'][subdir_name], level + 1)
            html_parts.extend(subdir_html)
        
        if level > 0:
            html_parts.append(f'{indent}  </div>\n')
            html_parts.append(f'{indent}</div>\n')
        
        return html_parts
    
    def generate_html(self, structure: Dict, title: Optional[str] = None) -> str:
        """Generate HTML index."""
        if title is None:
            title = f"{structure['name']} Index"
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .meta {{
            color: #7f8c8d;
            margin-bottom: 30px;
            font-size: 0.9em;
        }}
        
        .controls {{
            margin-bottom: 20px;
            padding: 15px;
            background: #ecf0f1;
            border-radius: 5px;
        }}
        
        .search-box {{
            width: 100%;
            padding: 10px;
            font-size: 16px;
            border: 2px solid #bdc3c7;
            border-radius: 5px;
            margin-bottom: 10px;
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: #3498db;
        }}
        
        .filter-buttons {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }}
        
        .filter-btn {{
            padding: 5px 15px;
            background: white;
            border: 1px solid #bdc3c7;
            border-radius: 3px;
            cursor: pointer;
            font-size: 14px;
        }}
        
        .filter-btn:hover {{
            background: #3498db;
            color: white;
            border-color: #3498db;
        }}
        
        .filter-btn.active {{
            background: #3498db;
            color: white;
            border-color: #3498db;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            color: #7f8c8d;
        }}
        
        .stat-value {{
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
        }}
        
        .tree {{
            font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
        }}
        
        .folder {{
            margin: 5px 0;
        }}
        
        .folder-name {{
            cursor: pointer;
            padding: 5px;
            border-radius: 3px;
            user-select: none;
        }}
        
        .folder-name:hover {{
            background: #ecf0f1;
        }}
        
        .folder-name::before {{
            content: '📁 ';
            margin-right: 5px;
        }}
        
        .folder-name.collapsed::before {{
            content: '📂 ';
        }}
        
        .folder-content {{
            margin-left: 20px;
            display: block;
        }}
        
        .folder-content.hidden {{
            display: none;
        }}
        
        .file {{
            margin: 3px 0;
            padding: 3px 5px;
            border-radius: 3px;
        }}
        
        .file:hover {{
            background: #ecf0f1;
        }}
        
        .file::before {{
            content: '📄 ';
            margin-right: 5px;
        }}
        
        .file-info {{
            color: #7f8c8d;
            font-size: 0.85em;
            margin-left: 25px;
        }}
        
        .hidden {{
            display: none;
        }}
        
        .theme-toggle {{
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 15px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }}
        
        .theme-toggle:hover {{
            background: #2980b9;
        }}
        
        body.dark {{
            background: #1a1a1a;
            color: #e0e0e0;
        }}
        
        body.dark .container {{
            background: #2d2d2d;
        }}
        
        body.dark .controls {{
            background: #3d3d3d;
        }}
        
        body.dark .search-box {{
            background: #3d3d3d;
            color: #e0e0e0;
            border-color: #555;
        }}
        
        body.dark .stat-card {{
            background: #3d3d3d;
        }}
        
        body.dark .folder-name:hover,
        body.dark .file:hover {{
            background: #3d3d3d;
        }}
    </style>
</head>
<body>
    <button class="theme-toggle" onclick="toggleTheme()">🌓 Toggle Theme</button>
    
    <div class="container">
        <h1>{title}</h1>
        <div class="meta">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">Total Files</div>
                <div class="stat-value">{self.stats['total_files']:,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Directories</div>
                <div class="stat-value">{self.stats['total_dirs']:,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Size</div>
                <div class="stat-value">{self.format_size(self.stats['total_size'])}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">File Types</div>
                <div class="stat-value">{len(self.stats['file_types'])}</div>
            </div>
        </div>
        
        <div class="controls">
            <input type="text" class="search-box" id="searchBox" placeholder="Search files and folders..." onkeyup="filterTree()">
            <div class="filter-buttons">
                <button class="filter-btn active" onclick="filterByType('all')">All</button>
"""
        
        # Add file type filter buttons
        for ext in sorted(self.stats['file_types'].keys(), key=lambda x: self.stats['file_types'][x], reverse=True)[:10]:
            ext_display = ext if ext != 'no extension' else 'no ext'
            count = self.stats['file_types'][ext]
            html_content += f'                <button class="filter-btn" onclick="filterByType(\'{ext}\')">{ext_display} ({count})</button>\n'
        
        html_content += """            </div>
        </div>
        
        <div class="tree" id="tree">
"""
        
        # Generate tree HTML
        html_content += "".join(self._generate_tree_html(structure, 0))
        
        html_content += """        </div>
    </div>
    
    <script>
        function toggleTheme() {
            document.body.classList.toggle('dark');
            localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
        }
        
        // Load saved theme
        if (localStorage.getItem('theme') === 'dark') {
            document.body.classList.add('dark');
        }
        
        function toggleFolder(element) {
            const content = element.nextElementSibling;
            if (content) {
                content.classList.toggle('hidden');
                element.classList.toggle('collapsed');
            }
        }
        
        function filterTree() {
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            const items = document.querySelectorAll('.folder, .file');
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.classList.remove('hidden');
                    // Show parent folders
                    let parent = item.parentElement;
                    while (parent && parent.classList.contains('folder-content')) {
                        parent.classList.remove('hidden');
                        const folderName = parent.previousElementSibling;
                        if (folderName) {
                            folderName.classList.remove('collapsed');
                        }
                        parent = parent.parentElement;
                    }
                } else {
                    item.classList.add('hidden');
                }
            });
        }
        
        function filterByType(type) {
            // Update button states
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            if (type === 'all') {
                document.querySelectorAll('.file').forEach(file => {
                    file.classList.remove('hidden');
                });
            } else {
                document.querySelectorAll('.file').forEach(file => {
                    const fileExt = file.getAttribute('data-extension');
                    if (fileExt === type) {
                        file.classList.remove('hidden');
                        // Show parent folders
                        let parent = file.parentElement;
                        while (parent && parent.classList.contains('folder-content')) {
                            parent.classList.remove('hidden');
                            const folderName = parent.previousElementSibling;
                            if (folderName) {
                                folderName.classList.remove('collapsed');
                            }
                            parent = parent.parentElement;
                        }
                    } else {
                        file.classList.add('hidden');
                    }
                });
            }
        }
    </script>
</body>
</html>"""
        
        return html_content
    
    def generate(self, output_markdown: Optional[Path] = None, output_html: Optional[Path] = None) -> Dict[str, Path]:
        """
        Generate both Markdown and HTML indexes.
        
        Args:
            output_markdown: Optional path for Markdown output (default: index_dir / "INDEX.md")
            output_html: Optional path for HTML output (default: index_dir / "index.html")
            
        Returns:
            Dictionary with paths to generated files
        """
        print("Scanning directory structure...")
        structure = self.scan_directory(self.root_path)
        
        # Create index directory
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate Markdown
        print("Generating Markdown index...")
        md_lines = self.generate_markdown(structure)
        
        # Add statistics section
        md_lines.append("\n---\n")
        md_lines.append("## Statistics\n\n")
        md_lines.append(f"- **Total Files:** {self.stats['total_files']:,}\n")
        md_lines.append(f"- **Total Directories:** {self.stats['total_dirs']:,}\n")
        md_lines.append(f"- **Total Size:** {self.format_size(self.stats['total_size'])}\n")
        md_lines.append("\n### File Types\n\n")
        
        for ext, count in sorted(self.stats['file_types'].items(), key=lambda x: x[1], reverse=True):
            ext_display = ext if ext != 'no extension' else '*no extension*'
            md_lines.append(f"- {ext_display}: {count:,} files\n")
        
        md_content = "".join(md_lines)
        
        # Determine output paths
        if output_markdown is None:
            output_markdown = self.index_dir / "INDEX.md"
        if output_html is None:
            output_html = self.index_dir / "index.html"
        
        # Write Markdown
        with open(output_markdown, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"Markdown index written to {output_markdown}")
        
        # Generate HTML
        print("Generating HTML index...")
        html_content = self.generate_html(structure)
        
        # Write HTML
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML index written to {output_html}")
        
        print("\nIndex generation complete!")
        
        return {
            'markdown': output_markdown,
            'html': output_html,
            'stats': self.stats.copy(),
        }

