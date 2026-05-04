#!/usr/bin/env python3
"""
SHACL Validation Tool for Gimie

This script validates RDF instance data against SHACL shapes to ensure 
that the data model is consistent with the ontology definition.

It can be used to detect when changes to models.py require updates to:
1. The SHACL ontology shapes
2. Example instance data

Usage:
    python validate_shacl.py [--shapes SHAPES_FILE] [--data DATA_FILE] [--verbose]

Examples:
    # Validate default files
    python validate_shacl.py
    
    # Validate specific files
    python validate_shacl.py --shapes custom_shapes.ttl --data custom_data.ttl
    
    # Verbose output with detailed validation report
    python validate_shacl.py --verbose

Exit codes:
    0: Validation successful (data conforms to shapes)
    1: Validation failed (data does not conform to shapes)
    2: Error (missing files, parse errors, etc.)
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, Tuple

try:
    import pyshacl
    from rdflib import Graph
except ImportError:
    print("Error: Required packages not installed.")
    print("Please install them with: pip install pyshacl rdflib")
    sys.exit(2)


def load_graph(file_path: Path, format_hint: Optional[str] = None) -> Graph:
    """
    Load an RDF graph from a file.
    
    Args:
        file_path: Path to the RDF file
        format_hint: Optional format hint (turtle, nt, xml, etc.)
    
    Returns:
        Loaded RDF graph
    
    Raises:
        FileNotFoundError: If the file doesn't exist
        Exception: If parsing fails
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    graph = Graph()
    
    # Auto-detect format if not provided
    if format_hint is None:
        if file_path.suffix.lower() in ['.ttl', '.turtle']:
            format_hint = 'turtle'
        elif file_path.suffix.lower() in ['.nt']:
            format_hint = 'nt'
        elif file_path.suffix.lower() in ['.xml', '.rdf']:
            format_hint = 'xml'
        elif file_path.suffix.lower() in ['.jsonld']:
            format_hint = 'json-ld'
        else:
            format_hint = 'turtle'  # Default
    
    try:
        graph.parse(file_path, format=format_hint)
        return graph
    except Exception as e:
        raise Exception(f"Failed to parse {file_path}: {e}")


def validate_with_shacl(data_graph: Graph, shapes_graph: Graph, verbose: bool = False) -> Tuple[bool, str]:
    """
    Validate data graph against SHACL shapes.
    
    Args:
        data_graph: RDF graph containing the data to validate
        shapes_graph: RDF graph containing SHACL shapes
        verbose: Whether to include detailed validation report
    
    Returns:
        Tuple of (is_valid, report_text)
    """
    try:
        # Run SHACL validation
        conforms, results_graph, results_text = pyshacl.validate(
            data_graph=data_graph,
            shacl_graph=shapes_graph,
            inference='rdfs',
            debug=verbose,
            serialize_report_graph='turtle'
        )
        
        if verbose or not conforms:
            # Include results graph in the report for detailed analysis
            report = f"Validation Results:\n"
            report += f"Conforms: {conforms}\n\n"
            
            if results_text:
                report += f"Validation Report:\n{results_text}\n"
            
            if not conforms and results_graph:
                report += f"\nDetailed Results (Turtle):\n"
                if hasattr(results_graph, 'serialize'):
                    report += results_graph.serialize(format='turtle')
                else:
                    report += str(results_graph)
            
            return conforms, report
        else:
            return conforms, "Validation passed successfully!"
            
    except Exception as e:
        return False, f"SHACL validation failed with error: {e}"


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Validate RDF data against SHACL shapes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split("Usage:")[1] if "Usage:" in __doc__ else ""
    )
    
    parser.add_argument(
        '--shapes', '-s',
        type=Path,
        default=Path('gimie/shacl/gimie_shacl.ttl'),
        help='Path to SHACL shapes file (default: gimie/shacl/gimie_shacl.ttl)'
    )
    
    parser.add_argument(
        '--data', '-d',
        type=Path,
        required=True,
        help='Path to RDF data file to validate'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output with detailed validation reports'
    )
    
    args = parser.parse_args()
    
    # Check if we're running from the correct directory
    current_dir = Path.cwd()
    gitroot = current_dir
    
    # Try to find the git root
    while gitroot.parent != gitroot:
        if (gitroot / '.git').exists():
            break
        gitroot = gitroot.parent
    else:
        if not (current_dir / '.git').exists():
            print("Warning: Not running from git repository root. Some paths may be incorrect.")
    
    # Resolve paths relative to git root or current directory
    shapes_file = args.shapes if args.shapes.is_absolute() else gitroot / args.shapes
    data_file = args.data if args.data.is_absolute() else gitroot / args.data
    
    print(f"SHACL Validation Tool")
    print(f"====================")
    print(f"Shapes file: {shapes_file}")
    print(f"Data file:   {data_file}")
    print(f"Verbose:     {args.verbose}")
    print()
    
    try:
        # Load SHACL shapes
        print("Loading SHACL shapes...")
        shapes_graph = load_graph(shapes_file)
        print(f"✓ Loaded {len(shapes_graph)} triples from shapes file")
        
        # Load data
        print("Loading RDF data...")
        data_graph = load_graph(data_file)
        print(f"✓ Loaded {len(data_graph)} triples from data file")
        
        # Run validation
        print("\nRunning SHACL validation...")
        is_valid, report = validate_with_shacl(data_graph, shapes_graph, args.verbose)
        
        # Print results
        print("\nValidation Results:")
        print("==================")
        if is_valid:
            print("✅ VALIDATION PASSED")
            print("The instance data conforms to the SHACL shapes.")
        else:
            print("❌ VALIDATION FAILED")
            print("The instance data does NOT conform to the SHACL shapes.")
        
        print("\nReport:")
        print("-------")
        print(report)
        
        # Exit with appropriate code
        sys.exit(0 if is_valid else 1)
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("\nMake sure you're running this script from the repository root,")
        print("or provide correct paths using --shapes and --data arguments.")
        sys.exit(2)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(2)


if __name__ == '__main__':
    main()