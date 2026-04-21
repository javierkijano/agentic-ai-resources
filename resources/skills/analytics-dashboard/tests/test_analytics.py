import sys
import os
import shutil
from pathlib import Path

# Setup paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../core/logic')))
from tracker import EventTracker
from reporter import ActivityReporter

def test_full_flow():
    repo_root = Path("./test_repo_analytics")
    if repo_root.exists():
        shutil.rmtree(repo_root)
    repo_root.mkdir()
    
    try:
        tracker = EventTracker(repo_root, agent_id="gemini-cli", env="test")
        
        # Log some events
        tracker.log_event("analyze_repo", status="success")
        tracker.log_event("fix_bug", status="success", metadata={"file": "curator.py"})
        tracker.log_event("invalid_cmd", status="error")
        
        reporter = ActivityReporter(repo_root)
        summary = reporter.generate_summary()
        
        print("Generated Summary:\n")
        print(summary)
        
        assert "Total Events recorded" in summary
        assert "3" in summary
        assert "SUCCESS: 2" in summary
        assert "ERROR: 1" in summary
        assert "gemini-cli: 3" in summary
        
        print("\nAnalytics flow test passed!")
        
    finally:
        if repo_root.exists():
            shutil.rmtree(repo_root)

if __name__ == "__main__":
    test_full_flow()
