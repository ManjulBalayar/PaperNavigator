"""
Simple Reference Parser - Standalone version
Works from any directory
"""

import json
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Dict, Optional


def parse_author(author_elem) -> Optional[Dict]:
    """Parse an author element"""
    persName = author_elem.find('persName')
    if not persName:
        return None
    
    # Get all forenames (first, middle)
    forenames = persName.find_all('forename')
    forename_text = ' '.join([f.text for f in forenames]) if forenames else ''
    
    # Get surname
    surname = persName.find('surname')
    surname_text = surname.text if surname else ''
    
    if not forename_text and not surname_text:
        return None
    
    return {
        'forename': forename_text,
        'surname': surname_text,
        'full_name': f"{forename_text} {surname_text}".strip()
    }


def parse_grobid_xml(xml_path: str) -> Dict:
    """Parse GROBID XML and return main paper + references"""
    
    with open(xml_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'xml')
    
    # ========== MAIN PAPER ==========
    main_paper = {}
    
    # Title
    title_elem = soup.find('title', {'level': 'a', 'type': 'main'})
    main_paper['title'] = title_elem.text.strip() if title_elem else "Unknown"
    
    # Authors
    authors = []
    source_desc = soup.find('sourceDesc')
    if source_desc:
        for author_elem in source_desc.find_all('author', recursive=False):
            author = parse_author(author_elem)
            if author:
                authors.append(author)
    main_paper['authors'] = authors
    
    # Year
    date_elem = soup.find('date', {'type': 'published'})
    main_paper['year'] = date_elem.get('when', '').split('-')[0] if date_elem else None
    
    # arXiv
    arxiv_elem = soup.find('idno', {'type': 'arXiv'})
    main_paper['arxiv'] = arxiv_elem.text if arxiv_elem else None
    
    # DOI
    doi_elem = soup.find('idno', {'type': 'DOI'})
    main_paper['doi'] = doi_elem.text if doi_elem else None
    
    # Abstract
    abstract_elem = soup.find('abstract')
    main_paper['abstract'] = abstract_elem.get_text(strip=True) if abstract_elem else None
    
    # ========== REFERENCES ==========
    references = []
    
    for biblStruct in soup.find_all('biblStruct'):
        # Skip if not a reference
        grobid_id = biblStruct.get('xml:id', '')
        if not grobid_id.startswith('b'):
            continue
        
        ref = {}
        
        # Title
        title_elem = biblStruct.find('title', {'level': 'a'})
        if not title_elem:
            title_elem = biblStruct.find('title', {'level': 'm'})
        ref['title'] = title_elem.text.strip() if title_elem else "No title"
        
        # Authors
        ref_authors = []
        for author_elem in biblStruct.find_all('author'):
            author = parse_author(author_elem)
            if author:
                ref_authors.append(author)
        ref['authors'] = ref_authors
        
        # Year
        date_elem = biblStruct.find('date', {'type': 'published'})
        ref['year'] = None
        if date_elem:
            when = date_elem.get('when', '')
            if when:
                ref['year'] = when.split('-')[0]
        
        # DOI
        doi_elem = biblStruct.find('idno', {'type': 'DOI'})
        ref['doi'] = doi_elem.text if doi_elem else None
        
        # arXiv
        arxiv_elem = biblStruct.find('idno', {'type': 'arXiv'})
        ref['arxiv'] = arxiv_elem.text if arxiv_elem else None
        
        # Venue
        ref['venue'] = None
        monogr = biblStruct.find('monogr')
        if monogr:
            venue_elem = monogr.find('title')
            if venue_elem:
                ref['venue'] = venue_elem.text.strip()
        
        # Pages
        ref['pages'] = None
        page_elem = biblStruct.find('biblScope', {'unit': 'page'})
        if page_elem:
            from_page = page_elem.get('from', '')
            to_page = page_elem.get('to', '')
            if from_page and to_page:
                ref['pages'] = f"{from_page}-{to_page}"
            elif from_page:
                ref['pages'] = from_page
        
        # Volume
        volume_elem = biblStruct.find('biblScope', {'unit': 'volume'})
        ref['volume'] = volume_elem.text.strip() if volume_elem else None
        
        # GROBID ID
        ref['grobid_id'] = grobid_id
        
        # Placeholders for Semantic Scholar
        ref['paper_id'] = None
        ref['citation_count'] = None
        ref['full_abstract'] = None
        
        references.append(ref)
    
    return {
        'main_paper': main_paper,
        'references': references
    }


if __name__ == '__main__':
    import sys
    
    # Check if XML path provided as argument
    if len(sys.argv) > 1:
        xml_path = sys.argv[1]
    else:
        # Look in current directory
        xml_files = list(Path('.').glob('*.xml'))
        if xml_files:
            xml_path = str(xml_files[0])
        else:
            # Look in ../../data/outputs
            data_dir = Path(__file__).parent.parent.parent / 'data' / 'outputs'
            xml_files = list(data_dir.glob('*.xml'))
            if xml_files:
                xml_path = str(xml_files[0])
            else:
                print("Error: No XML files found!")
                print("Usage: python simple_parser.py [path/to/file.xml]")
                exit(1)
    
    print(f"Parsing: {Path(xml_path).name}")
    
    # Parse
    data = parse_grobid_xml(xml_path)
    
    # Print summary
    main_paper = data['main_paper']
    references = data['references']
    
    print("\n" + "="*80)
    print("MAIN PAPER")
    print("="*80)
    print(f"Title: {main_paper['title']}")
    
    if main_paper['authors']:
        author_names = [a['full_name'] for a in main_paper['authors']]
        print(f"Authors: {', '.join(author_names[:5])}")
        if len(author_names) > 5:
            print(f"         + {len(author_names) - 5} more")
    
    print(f"Year: {main_paper['year']}")
    print(f"arXiv: {main_paper['arxiv']}")
    
    print("\n" + "="*80)
    print(f"REFERENCES: {len(references)} found")
    print("="*80)
    
    for i, ref in enumerate(references[:5], 1):
        print(f"\n[{i}] {ref['title']}")
        if ref['authors']:
            author_names = [a['full_name'] for a in ref['authors']]
            if len(author_names) > 3:
                print(f"    Authors: {', '.join(author_names[:3])} + {len(author_names)-3} more")
            else:
                print(f"    Authors: {', '.join(author_names)}")
        print(f"    Year: {ref['year']}")
        if ref['arxiv']:
            print(f"    arXiv: {ref['arxiv']}")
    
    if len(references) > 5:
        print(f"\n... and {len(references) - 5} more")
    
    # Save to JSON
    output_path = Path(xml_path).parent / 'parsed_references.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*80)
    print(f"Saved to {output_path}")
    print(f"   Main paper + {len(references)} references")
    print("="*80)
