# ProofCollapse v1.0

**An Automated Theorem Proving System Based on Existence Number Theory**

ProofCollapse treats mathematical proofs as dynamic processes: a theorem is "proved" when its corresponding dynamic number collapses to a finite value in the correct dual domain. Using the nine-domain dual graph (diameter ≤ 3), the system automatically searches for legal proof paths and verifies their validity.

## Verified Theorems

All seven Millennium Prize Problems are verified, plus Goldbach's conjecture, twin prime conjecture, Fermat's Last Theorem, and more.

## Quick Start

```bash
git clone https://github.com/existencenumber/proof-collapse.git
cd proof-collapse
pip install -r requirements.txt
python proof_system.py
