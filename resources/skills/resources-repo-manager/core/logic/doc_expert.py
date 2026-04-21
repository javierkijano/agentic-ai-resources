import os
import pathlib

class DocExpert:
    def __init__(self, repo_root):
        self.repo_root = pathlib.Path(repo_root)
        self.docs_dir = self.repo_root / "docs"

    def list_docs(self):
        docs = ["AGENTS.md"]
        if self.docs_dir.exists():
            for f in os.listdir(self.docs_dir):
                if f.endswith(".md"):
                    docs.append(f"docs/{f}")
        return docs

    def read_doc(self, doc_path):
        target = self.repo_root / doc_path
        if target.exists():
            return target.read_text()
        return f"Error: Document {doc_path} not found."

    def search_in_docs(self, query):
        results = []
        query = query.lower()
        for doc in self.list_docs():
            content = self.read_doc(doc)
            if query in content.lower():
                results.append(doc)
        return results
