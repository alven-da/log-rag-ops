import re
import json
import hashlib
from typing import List, Dict, Any

class LogParser:
    def __init__(self):
        # Compiled regex for performance
        self.rules = [
            (re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'), '<IP>'),
            (re.compile(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'), '<UUID>'),
            (re.compile(r'0x[a-fA-F0-9]+'), '<HEX>'),
            (re.compile(r'\b\d{4,}\b'), '<NUM>'),
            (re.compile(r'\b\d+(?:ms|sec|s)\b'), '<TIME>'),
            # (re.compile(r'(?<=ms|sec|s)\b'), ''), # Remove time units after replacement
        ]

    def generate_template(self, message: str) -> str:
        """Transforms a raw log message into a generic template."""
        for pattern, replacement in self.rules:
            message = pattern.sub(replacement, message)
        return message

    def get_template_hash(self, template: str) -> str:
        """Creates a unique fingerprint for the log type."""
        return hashlib.md5(template.encode()).hexdigest()[:8]

    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        with open(file_path, 'r') as f:
            raw_logs = json.load(f)

        processed_docs = []
        for log in raw_logs:
            template = self.generate_template(log['message'])
            template_hash = self.get_template_hash(template)

            # Construct the 'Document' format for LangChain
            # We embed the template, but keep the original message for the LLM to read
            doc = {
                "page_content": f"Service: {log['service']} | Event: {template}",
                "metadata": {
                    **log, # Spread original fields (request_id, level, etc.)
                    "template_hash": template_hash,
                    "is_error": log['level'] == "ERROR"
                }
            }
            processed_docs.append(doc)
        
        return processed_docs

# Quick Test
if __name__ == "__main__":
    parser = LogParser()
    sample_docs = parser.parse_file('data/raw_logs/logs.json')
    
    print(f"✅ Processed {len(sample_docs)} logs.")
    print(f"Sample Template: {sample_docs[1]['page_content']}")
    print(f"Template Hash: {sample_docs[1]['metadata']['template_hash']}")