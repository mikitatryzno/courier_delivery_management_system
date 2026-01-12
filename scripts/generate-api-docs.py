#!/usr/bin/env python3
"""Generate API documentation files."""

import json
import yaml
import requests
from pathlib import Path

def generate_openapi_files():
    """Generate OpenAPI specification files."""
    
    # API base URL
    base_url = "http://localhost:8000"
    
    try:
        # Fetch OpenAPI JSON
        response = requests.get(f"{base_url}/api/openapi.json")
        response.raise_for_status()
        openapi_spec = response.json()
        
        # Create docs directory
        docs_dir = Path("docs/api")
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Save JSON format
        with open(docs_dir / "openapi.json", "w") as f:
            json.dump(openapi_spec, f, indent=2)
        
        # Save YAML format
        with open(docs_dir / "openapi.yaml", "w") as f:
            yaml.dump(openapi_spec, f, default_flow_style=False, sort_keys=False)
        
        print("✅ OpenAPI specification files generated successfully!")
        print(f"📁 Files saved to: {docs_dir}")
        print("📄 openapi.json - JSON format")
        print("📄 openapi.yaml - YAML format")
        
        # Generate endpoint summary
        generate_endpoint_summary(openapi_spec, docs_dir)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching OpenAPI spec: {e}")
        print("💡 Make sure the API server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error generating files: {e}")

def generate_endpoint_summary(openapi_spec, docs_dir):
    """Generate endpoint summary markdown."""
    
    endpoints = []
    
    for path, methods in openapi_spec.get("paths", {}).items():
        for method, details in methods.items():
            if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                endpoints.append({
                    "method": method.upper(),
                    "path": path,
                    "summary": details.get("summary", ""),
                    "description": details.get("description", ""),
                    "tags": details.get("tags", [])
                })
    
    # Group by tags
    grouped_endpoints = {}
    for endpoint in endpoints:
        tag = endpoint["tags"][0] if endpoint["tags"] else "Other"
        if tag not in grouped_endpoints:
            grouped_endpoints[tag] = []
        grouped_endpoints[tag].append(endpoint)
    
    # Generate markdown
    markdown_content = "# API Endpoints Summary\n\n"
    markdown_content += f"Generated from OpenAPI specification v{openapi_spec.get('info', {}).get('version', 'unknown')}\n\n"
    
    for tag, tag_endpoints in grouped_endpoints.items():
        markdown_content += f"## {tag.title()}\n\n"
        
        for endpoint in tag_endpoints:
            markdown_content += f"### {endpoint['method']} {endpoint['path']}\n\n"
            if endpoint['summary']:
                markdown_content += f"**Summary:** {endpoint['summary']}\n\n"
            if endpoint['description']:
                markdown_content += f"**Description:** {endpoint['description']}\n\n"
            markdown_content += "---\n\n"
    
    # Save markdown file
    with open(docs_dir / "endpoints.md", "w") as f:
        f.write(markdown_content)
    
    print("📄 endpoints.md - Endpoint summary")

if __name__ == "__main__":
    generate_openapi_files()