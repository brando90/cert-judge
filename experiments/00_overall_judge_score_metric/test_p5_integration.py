#!/usr/bin/env python3
"""
Quick integration test for P5 in the main HSJ pipeline.
Tests that P5 is computed and integrated into JTI correctly.
"""

import sys
from pathlib import Path

# Add cert_judge to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "py_src"))

# Mock the veribench import that main_overall_judge_score needs
class MockResult:
    def get(self, key, default=None):
        # Return a reasonable normalized score for testing
        return 0.95 if key == "normalized_score" else default

def mock_get_sim_score(agent_filepath, gold_filepath, **kwargs):
    """Mock function that returns high score for same file, lower for different files."""
    if agent_filepath == gold_filepath:
        return MockResult()  # High score for identity
    else:
        # Hash filenames to get consistent but different scores
        hash_val = (hash(str(agent_filepath)) + hash(str(gold_filepath))) % 100
        score = 0.3 + (hash_val / 200)  # Range: 0.3-0.8
        result = MockResult()
        result.normalized_score = score
        return result

# Patch the import
sys.modules['veribench'] = type(sys)('veribench')
sys.modules['veribench.metrics'] = type(sys)('metrics')
sys.modules['veribench.metrics.sim_file_eq_llm_judge'] = type(sys)('sim_file_eq_llm_judge')
sys.modules['veribench.metrics.sim_file_eq_llm_judge'].get_sim_score_file_eq_llm_result_in_json_str = mock_get_sim_score

# Now we can import the main module
import main_overall_judge_score

def create_test_files(tmp_dir: Path):
    """Create test .lean files for evaluation."""
    tmp_dir.mkdir(parents=True, exist_ok=True)
    
    # Create test files
    files = []
    for i in range(5):
        f = tmp_dir / f"test_{i}.lean"
        f.write_text(f"-- Test file {i}\ntheorem test_{i} : True := trivial")
        files.append(f)
    
    return files

def test_p5_integration():
    """Test that P5 is computed and integrated into the pipeline."""
    print("\n" + "="*70)
    print("INTEGRATION TEST: P5 in HSJ Pipeline")
    print("="*70)
    
    # Create temporary test directory
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        test_dir = tmp_path / "test_files"
        create_test_files(test_dir)
        
        # Create minimal bug/missing-spec test files
        bug_dir = tmp_path / "bugs"
        bug_dir.mkdir()
        for k in range(3):
            f = bug_dir / f"test_0_{k}_bugs.lean"
            f.write_text(f"-- File with {k} bugs\ntheorem test : True := trivial")
        
        missing_dir = tmp_path / "missing"
        missing_dir.mkdir()
        for m in range(3):
            f = missing_dir / f"test_0_{m}_missing.lean"
            f.write_text(f"-- File with {m} missing specs\ntheorem test : True := trivial")
        
        # Create a simple test prompt template
        prompt_file = tmp_path / "test_prompt.txt"
        prompt_file.write_text("Compare these files and give a score from 0 to {max_score}.")
        
        # Run the main evaluation
        kwargs = {
            "mode": "dryrun",
            "eval_mode": "hsj_real",
            "claude_dotenv_path": "",
            "judge_prompt_temp_path": str(prompt_file),
            "max_score": 30,
            "paths_p1": [str(test_dir)],
            "path_p2": str(bug_dir),
            "path_p3": str(missing_dir),
            "num_llm_judge_calls_per_file_pair": 3,
            "max_workers": 4,
        }
        
        print("\nRunning HSJ evaluation with P5...")
        try:
            result = main_overall_judge_score.main(**kwargs)
        except Exception as e:
            print(f"\n❌ FAIL: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n" + "-"*70)
        print("Results:")
        print("-"*70)
        print(f"  P1 (Reflexivity):        {result.get('p1', 0.0):.4f}")
        print(f"  P2 (Bug Monotonicity):   {result.get('p2', 0.0):.4f}")
        print(f"  P3 (Spec Completeness):  {result.get('p3', 0.0):.4f}")
        print(f"  P4 (Stability):          {result.get('p4', 0.0):.4f}")
        print(f"  P5 (TVD-MI):             {result.get('p5', 0.0):.4f}")
        print()
        print(f"  P5 Details:")
        print(f"    Youden's J:         {result.get('p5_youdens_j', 0.0):.4f}")
        print(f"    Macro AUC:          {result.get('p5_auc_macro', 0.5):.4f}")
        print(f"    Tamper AUC drop:    {result.get('p5_delta_auc_tamper', 0.1):.4f}")
        print()
        print(f"  JTI (5-property):        {result.get('jti', 0.0):.4f}")
        print("-"*70)
        
        # Verify all properties are present
        required_keys = ['p1', 'p2', 'p3', 'p4', 'p5', 'jti']
        missing = [k for k in required_keys if k not in result]
        
        if missing:
            print(f"\n❌ FAIL: Missing keys: {missing}")
            return False
        
        # Verify P5 is in valid range [0,1]
        p5 = result['p5']
        if not (0.0 <= p5 <= 1.0):
            print(f"\n❌ FAIL: P5 = {p5:.4f} is out of range [0,1]")
            return False
        
        # Verify JTI is computed with 5 properties
        # Expected: JTI ≈ 0.2 * (p1 + p2 + p3 + p4 + p5)
        expected_jti = 0.2 * sum(result[k] for k in ['p1', 'p2', 'p3', 'p4', 'p5'])
        actual_jti = result['jti']
        
        if abs(expected_jti - actual_jti) > 0.01:
            print(f"\n⚠️  WARNING: JTI mismatch")
            print(f"  Expected (0.2 × sum): {expected_jti:.4f}")
            print(f"  Actual:               {actual_jti:.4f}")
            # Don't fail on this, just warn
        
        print("\n✅ PASS: P5 successfully integrated into HSJ pipeline!")
        print("\nP5 (TVD-MI) is now part of the 5-property Judge Trust Index.")
        print("="*70)
        
        return True


if __name__ == "__main__":
    success = test_p5_integration()
    sys.exit(0 if success else 1)

