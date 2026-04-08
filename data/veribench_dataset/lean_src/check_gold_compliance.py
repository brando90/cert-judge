#!/usr/bin/env python3

import os
import re

def check_gold_compliance(file_path):
    """Check if a file follows the gold reference format"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # Check 1: Header should start with "/-!" and contain "VeriBench – Gold Example"
        if not content.startswith('/-!'):
            issues.append("Missing /-! header start")
        
        if "VeriBench – Gold Example" not in content[:500]:
            issues.append("Missing 'VeriBench – Gold Example' in header")
        
        # Check 2: Should have file order specification
        if "File order:" not in content[:1000]:
            issues.append("Missing 'File order:' specification")
        
        # Check 3: Should have the 7-step structure
        required_steps = [
            "1. Implementation",
            "2. Unit tests (positive, edge, positive/negative test suite)",
            "3. Pre‑condition prop",
            "4. Exhaustive property prop and their theorems", 
            "5. Post‑condition prop (same order as property props)",
            "6. Correctness theorem `Pre → Post`",
            "7. Imperative i. implementation, ii. tests"
        ]
        
        for step in required_steps:
            if step not in content[:1000]:
                issues.append(f"Missing step: {step}")
        
        # Check 4: Should have proper sections
        required_sections = [
            "/-!\n# Tests\n-/",
            "/-!\n# Tests: Edge Cases\n-/", 
            "/-!\n# Positive / Negative Test‑Suite\n-/",
            "/-!\n# Pre‑Condition\n-/",
            "/-!\n# Property Theorems\n-/",
            "/-!\n# Post‑Condition  (conjunction of all desired properties)\n-/",
            "/-!\n# Correctness Theorem\n-/",
            "/-!\n# Imperative Implementation\n-/",
            "/-!\n# Imperative Tests\n-/",
            "/-!\n# Imperative Tests: Edge Cases\n-/",
            "/-!\n# Positive / Negative Test‑Suite\n-/"
        ]
        
        section_count = 0
        for section in required_sections:
            if section in content:
                section_count += 1
        
        if section_count < 8:  # Should have most sections
            issues.append(f"Missing proper sections (found {section_count} of {len(required_sections)})")
        
        # Check 5: Should have Pre, Post_prop, correctness_thm
        if "def Pre " not in content:
            issues.append("Missing 'def Pre'")
        if "def Post_prop " not in content:
            issues.append("Missing 'def Post_prop'")
        if "theorem correctness_thm " not in content:
            issues.append("Missing 'theorem correctness_thm'")
        
        return issues
        
    except Exception as e:
        return [f"Error reading file: {e}"]

def main():
    print("Checking gold reference compliance for all VeriBench files...")
    
    # Find all .lean files
    lean_files = []
    for root, dirs, files in os.walk('veribench'):
        for file in files:
            if file.endswith('.lean'):
                lean_files.append(os.path.join(root, file))
    
    lean_files.sort()
    print(f"Found {len(lean_files)} Lean files")
    
    compliant_files = []
    non_compliant_files = []
    
    for file_path in lean_files:
        issues = check_gold_compliance(file_path)
        if not issues:
            compliant_files.append(file_path)
            print(f"✅ {file_path}")
        else:
            non_compliant_files.append((file_path, issues))
            print(f"❌ {file_path}")
            for issue in issues[:3]:  # Show first 3 issues
                print(f"    - {issue}")
    
    print(f"\n📊 COMPLIANCE SUMMARY:")
    print(f"✅ Compliant: {len(compliant_files)} files")
    print(f"❌ Non-compliant: {len(non_compliant_files)} files")
    print(f"📈 Compliance rate: {len(compliant_files)}/{len(lean_files)} = {len(compliant_files)/len(lean_files)*100:.1f}%")
    
    if non_compliant_files:
        print(f"\n❌ NON-COMPLIANT FILES:")
        for file_path, issues in non_compliant_files[:10]:  # Show first 10
            print(f"  {file_path}: {len(issues)} issues")

if __name__ == "__main__":
    main()
