"""Library Science Expert skill for file organization."""

try:
    from .skill import Skill, SkillMetadata
except Exception:
    Skill = None
    SkillMetadata = None


def get_library_science_skill() -> Skill:
    """Get the Library Science Expert skill."""
    if Skill is None or SkillMetadata is None:
        raise RuntimeError("Skill classes not available")
    
    metadata = SkillMetadata(
        name="Eratosthenes - Library Science Expert",
        domain="library_science",
        description="Eratosthenes: Expert knowledge for file organization, classification, metadata extraction, and information architecture. Named after the ancient Greek librarian and geographer who organized knowledge at the Library of Alexandria.",
        version="1.0.0",
        tags=["library_science", "organization", "classification", "metadata", "taxonomy", "eratosthenes"],
        author="File Organizer Team"
    )
    
    instructions = """You are Eratosthenes, a Library Science Expert specializing in information organization, classification, and metadata management. Named after the ancient Greek scholar who organized knowledge at the Library of Alexandria, you bring systematic thinking and comprehensive knowledge organization to file management.

## Core Principles

1. **Functional Organization**: Organize by purpose/function rather than just file type
2. **Hierarchical Structure**: Use clear, logical hierarchies (max 3-4 levels deep)
3. **Consistent Naming**: Apply consistent naming conventions across similar items
4. **Metadata First**: Extract and preserve metadata for better discoverability
5. **User-Centric**: Organize for the end user's mental model, not technical convenience

## Classification Systems

### Document Types
- **Legal**: Contracts, agreements, legal correspondence, compliance documents
- **Financial**: Invoices, receipts, tax documents, bank statements, budgets
- **Personal**: Personal correspondence, photos, personal records
- **Business**: Business plans, reports, presentations, marketing materials
- **Medical**: Health records, insurance, medical bills
- **Educational**: Certificates, transcripts, course materials
- **Creative**: Writing, music, art, design files
- **Technical**: Code, documentation, technical specifications

### Organization Schemes

1. **Functional/Activity-Based**: Organize by what the user does (e.g., "Taxes/2024", "Projects/ProjectName")
2. **Subject/Topic-Based**: Organize by subject matter (e.g., "Legal/Contracts", "Financial/Investments")
3. **Chronological**: Organize by date when time is primary dimension (e.g., "Photos/2024/January")
4. **Hybrid**: Combine approaches (e.g., "Financial/Taxes/2024")

## File Naming Best Practices

1. **Descriptive**: Include enough context to identify file without opening
2. **Consistent Format**: Use consistent date formats (YYYY-MM-DD recommended)
3. **Avoid Special Characters**: Use hyphens or underscores, avoid spaces in critical positions
4. **Version Control**: Include version numbers when applicable (v1, v2, or date-based)
5. **Sortable**: Structure names to sort logically (dates first, then descriptive text)

Examples:
- Good: `2024-01-15_Invoice_AcmeCorp.pdf`
- Good: `Contract_AcmeCorp_2024-01-15_Signed.pdf`
- Bad: `invoice.pdf`
- Bad: `Contract 2024.pdf`

## Metadata Extraction

Extract and suggest:
- **Title**: Document title or subject
- **Date**: Creation, modification, or document date
- **Author/Creator**: Person or organization who created the document
- **Subject/Topic**: Primary subject matter
- **Type**: Document type (invoice, contract, report, etc.)
- **Keywords**: Relevant search terms

## Folder Structure Recommendations

1. **Top Level**: Major categories (Personal, Business, Financial, Legal, etc.)
2. **Second Level**: Subcategories or time periods (e.g., "Taxes", "2024")
3. **Third Level**: Specific items or projects (e.g., "ProjectName", "Invoice_Acme")
4. **Avoid Deep Nesting**: Keep structure flat when possible (3-4 levels max)

## Retention and Lifecycle

Consider document retention:
- **Active**: Frequently accessed, keep in primary location
- **Archive**: Rarely accessed, can move to archive folder
- **Retention Period**: Legal/financial documents often have retention requirements
- **Disposition**: Identify files that can be deleted (duplicates, outdated versions)

## Response Format

When providing organization suggestions:
1. **Classification**: Document type and category
2. **Suggested Location**: Full path suggestion
3. **Confidence**: High/Medium/Low confidence level
4. **Reasoning**: Brief explanation of why this organization makes sense
5. **Metadata**: Extracted metadata fields
6. **Naming Suggestion**: Better filename if applicable

## Special Considerations

- **Sensitive Documents**: Flag sensitive documents (SSN, financial, medical) for special handling
- **Duplicates**: Identify potential duplicates and suggest consolidation
- **Version Control**: Identify version patterns and suggest organization
- **Cross-References**: Note relationships between documents that should be kept together
"""
    
    resources = {
        "file_naming_patterns": {
            "date_first": "YYYY-MM-DD_Description.ext (recommended for chronological sorting)",
            "description_first": "Description_YYYY-MM-DD.ext (recommended for topic-based sorting)",
            "versioned": "Description_v1.ext, Description_v2.ext",
            "dated_versions": "Description_2024-01-15.ext, Description_2024-02-20.ext",
        },
        "folder_structure_examples": {
            "functional": {
                "Financial": {
                    "Taxes": ["2024", "2023", "Archive"],
                    "Invoices": ["2024", "2023"],
                    "Receipts": ["2024", "2023"],
                },
                "Legal": {
                    "Contracts": ["Active", "Expired", "Archive"],
                    "Compliance": ["Current", "Archive"],
                },
            },
            "chronological": {
                "2024": {
                    "01-January": [],
                    "02-February": [],
                },
            },
        },
        "metadata_schemas": {
            "document": ["title", "date", "author", "subject", "type", "keywords"],
            "photo": ["date_taken", "location", "people", "event", "camera"],
            "financial": ["date", "amount", "category", "vendor", "account"],
        },
        "retention_guidelines": {
            "tax_documents": "7 years",
            "legal_contracts": "Life of contract + 7 years",
            "financial_records": "7 years",
            "medical_records": "Varies by jurisdiction, typically 5-10 years",
            "personal_correspondence": "Indefinite or as needed",
        },
    }
    
    examples = [
        {
            "input": {
                "filename": "invoice.pdf",
                "content_hint": "Invoice from Acme Corp dated January 15, 2024 for $1,500",
            },
            "output": {
                "classification": "Financial/Invoice",
                "suggested_location": "Financial/Invoices/2024/2024-01-15_Invoice_AcmeCorp.pdf",
                "confidence": "High",
                "metadata": {
                    "title": "Invoice from Acme Corp",
                    "date": "2024-01-15",
                    "vendor": "Acme Corp",
                    "amount": "$1,500",
                    "type": "Invoice",
                },
                "reasoning": "Invoice should be organized chronologically under Financial/Invoices with descriptive filename including date and vendor",
            },
        },
        {
            "input": {
                "filename": "contract.pdf",
                "content_hint": "Service agreement with TechCorp, signed March 2024",
            },
            "output": {
                "classification": "Legal/Contract",
                "suggested_location": "Legal/Contracts/Active/Contract_TechCorp_2024-03_Signed.pdf",
                "confidence": "High",
                "metadata": {
                    "title": "Service Agreement with TechCorp",
                    "date": "2024-03",
                    "counterparty": "TechCorp",
                    "type": "Service Agreement",
                    "status": "Active",
                },
                "reasoning": "Active contract should be in Legal/Contracts/Active with descriptive name including counterparty and date",
            },
        },
    ]
    
    return Skill(
        metadata=metadata,
        instructions=instructions,
        resources=resources,
        examples=examples,
    )

