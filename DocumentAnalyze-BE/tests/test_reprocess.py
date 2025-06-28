# test_reprocess.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.reprocess_service import reprocess_document

# Replace with an existing document ID from your DB
doc_id = 28

# Call the function
reprocess_document(doc_id)
