"""Exercise the installed service via real TCP, HTTP and gRPC without a simulator."""
import importlib.util
from pathlib import Path

def test_standalone_receiver_and_recorded_iq_replay():
    path=Path(__file__).resolve().parents[1]/"scripts/qualify_independence.py"
    spec=importlib.util.spec_from_file_location("qualify_df",path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result=module.qualify()
    assert result["status"]=="passed"
    assert result["lossless_archive_replayed_to_unmodified_skill"]
    assert not result["simulator_or_truth_available"]
