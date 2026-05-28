import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from proof_system import ProofEngine, VerificationEngine

def test_all_theorems():
    engine = ProofEngine()
    verifier = VerificationEngine()
    
    for name in engine.proof_cache:
        proof = engine.prove(name)
        ok = verifier.verify(proof)
        assert ok, f"FAILED: {name}"
        print(f"PASSED: {name} (depth={proof.depth})")
    
    # 测试未知定理应返回unproven
    unknown = engine.prove("fake_conjecture_xyz")
    assert unknown.status == "unproven"
    print("PASSED: unknown theorem correctly unproven")
    
    print("\nAll tests passed.")

if __name__ == "__main__":
    test_all_theorems()
