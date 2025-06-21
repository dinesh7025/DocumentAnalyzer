# agents/router_agent.py

def route_document(doc_type):
    """Returns the system to route the document to based on its type."""
    routing_map = {
        "invoice": "ERP",
        "contract": "DMS",
        "resume": "Email",
        "report": "File Share"
    }

    cleaned_type = doc_type.strip().lower()
    result = routing_map.get(cleaned_type, "Unknown")

    return result

