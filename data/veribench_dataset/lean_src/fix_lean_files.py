#!/usr/bin/env python3
import os
import re

def fix_lean_file(filepath):
    """Fix common Lean compilation issues in a file."""
    print(f"Fixing {filepath}")
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Fix 1: Replace 'simp' with 'native_decide' in examples
    content = re.sub(r'example\s*:[^:=]*:=\s*by\s+unfold[^;]*simp[^;]*', 
                     lambda m: m.group(0).replace('simp', 'native_decide').split('unfold')[0] + 'native_decide', 
                     content)
    content = re.sub(r'example\s*:[^:=]*:=\s*by\s+simp\s*$', 
                     lambda m: m.group(0).replace('simp', 'native_decide'), 
                     content, flags=re.MULTILINE)
    
    # Fix 2: Replace simple proofs with native_decide
    content = re.sub(r'example\s*:[^:=]*:=\s*by\s+unfold[^;]*$', 
                     lambda m: m.group(0).replace('unfold', 'native_decide').split('unfold')[0] + 'native_decide', 
                     content, flags=re.MULTILINE)
    
    # Fix 3: Fix missing := in definitions
    content = re.sub(r'def\s+Post\s*\([^)]*\)\s*:\s*Prop\s*:', 'def Post (n : Nat) (f : Nat → Nat) : Prop :=', content)
    
    with open(filepath, 'w') as f:
        f.write(content)

# Fix the remaining files
files_to_fix = [
    'veribench/easy_set/curated_examples/11_MyFirstChar.lean',
    'veribench/easy_set/curated_examples/15_MyRepeatString.lean', 
    'veribench/easy_set/curated_examples/18_MyFibonacci.lean',
    'veribench/easy_set/curated_examples/13_MyUppercase.lean',
    'veribench/easy_set/curated_examples/9_MyOddSumParity.lean',
    'veribench/easy_set/curated_examples/10_MyEvenSumParity.lean',
    'veribench/easy_set/curated_examples/8_myReverse.lean'
]

for file in files_to_fix:
    if os.path.exists(file):
        fix_lean_file(file)
    else:
        print(f"File not found: {file}")
