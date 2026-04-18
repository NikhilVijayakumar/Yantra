"""
Dakini - Paper Config Generator Script

Auto-detects modules from src/ directory and generates paper_config.yaml
"""

from pathlib import Path
import yaml
from datetime import datetime
from typing import List, Dict, Any

def detect_modules(src_path: Path) -> List[Dict[str, Any]]:
    """
    Recursively scan src directory and detect modules.
    
    Returns list of module configurations.
    """
    modules = []
    
    # helper for recursive scan
    for path in src_path.rglob('*'):
        if not path.is_dir():
            continue
            
        # Skip hidden, cache, and test dirs
        if path.name.startswith('.') or path.name.startswith('_') or path.name in ['__pycache__', 'tests', 'test']:
            continue
            
        # Check if it has at least 1 Python file (excluding __init__.py)
        py_files = [f for f in path.glob('*.py') if f.name != '__init__.py']
        if len(py_files) < 1:
            continue
            
        # Detect priority and focus areas
        priority, focus_areas = analyze_module(path, py_files)
        
        # Scan documentation for additional insights
        doc_insights = scan_documentation(path.name)
        if doc_insights['focus_areas']:
            focus_areas.extend(doc_insights['focus_areas'])
            focus_areas = list(set(focus_areas)) # dedupe
        
        # Extract description from docstring
        description = extract_description(path)
        
        modules.append({
            'name': path.name,
            'path': str(path),
            'doc_path': doc_insights['doc_path'],
            'description': description,
            'priority': priority,
            'include_in_final': priority in ['critical', 'high', 'medium'], # Auto-include medium too if it has code
            'focus_areas': focus_areas
        })
    
    return modules


def analyze_module(module_dir: Path, py_files: List[Path]) -> tuple[str, List[str]]:
    """Analyze module to determine priority and focus areas."""
    priority = 'medium'
    focus_areas = []
    
    file_names = [f.name for f in py_files]
    
    # Critical indicators
    if any(name in file_names for name in ['core.py', 'engine.py', 'repository.py']):
        priority = 'critical'
    
    # High priority indicators
    elif any(name in file_names for name in ['manager.py', 'processor.py', 'service.py']):
        priority = 'high'
    
    # Medium priority indicators
    elif any(name in file_names for name in ['factory.py', 'builder.py', 'adapter.py']):
        priority = 'medium'
    
    # Low priority indicators
    elif any(name in file_names for name in ['utils.py', 'helpers.py', 'common.py']):
        priority = 'low'
    
    # Detect focus areas by scanning file content
    for py_file in py_files[:3]:  # Check first 3 files
        try:
            content = py_file.read_text()
            
            if 'Repository' in content and 'repository_pattern' not in focus_areas:
                focus_areas.append('repository_pattern')
            if 'Protocol' in content and 'clean_architecture' not in focus_areas:
                focus_areas.append('clean_architecture')
            if 'Builder' in content and 'builder_pattern' not in focus_areas:
                focus_areas.append('builder_pattern')
            if 'Factory' in content and 'factory_pattern' not in focus_areas:
                focus_areas.append('factory_pattern')
        except Exception:
            pass
    
    return priority, focus_areas or ['general_implementation']


def scan_documentation(module_name: str) -> dict:
    """Scan docs/features/{module_name} for insights."""
    docs_path = Path(f"docs/features/{module_name}")
    insights = {
        'focus_areas': [],
        'doc_path': None
    }
    
    if not docs_path.exists():
        return insights
        
    insights['doc_path'] = str(docs_path)
    
    # scan all md files
    for md_file in docs_path.rglob("*.md"):
        try:
            content = md_file.read_text().lower()
            if "protocol" in content:
                insights['focus_areas'].append("protocol_based_design")
            if "mlflow" in content:
                insights['focus_areas'].append("mlflow_integration")
            if "dvc" in content:
                insights['focus_areas'].append("data_versioning_dvc")
            if "evidently" in content:
                insights['focus_areas'].append("evidently_monitoring")
            if "prefect" in content:
                insights['focus_areas'].append("prefect_orchestration")
            if "test strategy" in content:
                insights['focus_areas'].append("testing_strategy")
        except:
            pass
            
    return insights

def extract_description(module_dir: Path) -> str:
    """Extract module description from __init__.py or first .py file."""
    init_file = module_dir / '__init__.py'
    
    if init_file.exists():
        try:
            content = init_file.read_text()
            # Extract first docstring
            if '"""' in content:
                start = content.find('"""') + 3
                end = content.find('"""', start)
                if end > start:
                    return content[start:end].strip().split('\n')[0]
        except Exception:
            pass
    
    # Fallback to module name
    return f"{module_dir.name.replace('_', ' ').title()} module"


def generate_config(modules: List[Dict[str, Any]], output_path: Path) -> None:
    """Generate paper_config.yaml from detected modules."""
    
    config = {
        '# Paper Generation Configuration': None,
        '# Auto-generated by Dakini on': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'generation': {
            'mode': 'modular',
            'auto_detect_modules': True,
            'depth': 'comprehensive'
        },
        'modules': modules,
        'exclusions': {
            'skip_test_files': True,
            'skip_example_files': True,
            'skip_init_files': True
        },
        'output': {
            'base_dir': 'docs/paper',
            'modules_dir': '${base_dir}/modules',
            'cross_module_dir': '${base_dir}/cross_module',
            'final_draft': '${base_dir}/drafts/FINAL_JOURNAL_REPORT.md',
            'appendix_dir': '${base_dir}/appendix'
        },
        'analysis': {
            'mathematics': {
                'min_algorithms_per_module': 1,
                'include_edge_cases': True,
                'include_complexity_analysis': True,
                'variable_mapping': 'required'
            },
            'architecture': {
                'min_diagrams_per_module': 2,
                'diagram_types': ['class_diagram', 'sequence_diagram', 'component_diagram'],
                'include_dependency_analysis': True
            },
            'gaps': {
                'severity_levels': ['critical', 'moderate', 'minor'],
                'include_remediation_plan': True,
                'estimate_effort': True
            }
        },
        'quality': {
            'min_latex_equations': len(modules) * 2,
            'min_diagrams': len(modules) * 2,
            'min_identified_gaps': len(modules) * 3,
            'min_code_references': 50
        },
        'verification': {
            'cross_check_variable_names': True,
            'verify_all_code_references': True,
            'validate_diagram_accuracy': True,
            'check_gap_uniqueness': True
        }
    }
    
    # Write to file
    with output_path.open('w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    print(f"✅ Generated {output_path}")
    print(f"📦 Detected {len(modules)} modules:")
    for priority in ['critical', 'high', 'medium', 'low']:
        count = sum(1 for m in modules if m['priority'] == priority)
        if count > 0:
            print(f"   - {count} {priority} priority")


if __name__ == '__main__':
    # Default paths
    src_path = Path('src/nikhil/yantra')
    output_path = Path('.agent/paper_config.yaml')
    
    if not src_path.exists():
        print(f"❌ Source path not found: {src_path}")
        exit(1)
    
    # Detect modules
    modules = detect_modules(src_path)
    
    if not modules:
        print("⚠️ No modules detected!")
        exit(1)
    
    # Generate config
    generate_config(modules, output_path)
