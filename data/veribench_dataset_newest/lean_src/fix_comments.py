#!/usr/bin/env python3

import os
import re
import subprocess

# List of all files that failed compilation
failed_files = [
    "veribench/cs_set/LCS.lean",
    "veribench/cs_set/Merge_sort.lean", 
    "veribench/cs_set/Edit_distance.lean",
    "veribench/cs_set/Heap_sort.lean",
    "veribench/cs_set/Quick_sort.lean",
    "veribench/cs_set/Binary_search.lean",
    "veribench/easy_set/30_longest_valid_parentheses.lean",
    "veribench/easy_set/23_is_prime.lean",
    "veribench/easy_set/33_MyMinimum.lean",
    "veribench/easy_set/25_longest_palindromic_substring.lean",
    "veribench/easy_set/29_longest_common_prefix.lean",
    "veribench/easy_set/38_reverse_words.lean",
    "veribench/easy_set/31_count_even_digits.lean",
    "veribench/easy_set/09_MyOddSumParity.lean",
    "veribench/easy_set/32_divisible_by_seven_and_eight_count.lean",
    "veribench/easy_set/36_remove_digits.lean",
    "veribench/easy_set/34_perfect_square_or_add_five.lean",
    "veribench/easy_set/26_longest_common_subsequence.lean",
    "veribench/easy_set/21_is_palindrome.lean",
    "veribench/easy_set/37_remove_first_five_letters.lean",
    "veribench/easy_set/24_matrix_multiply.lean",
    "veribench/easy_set/35_quadruple_abs_difference_plus_three.lean",
    "veribench/easy_set/28_length_of_longest_substring.lean",
    "veribench/security_6585/10_serverSideRequestForgery.lean",
    "veribench/security_6585/5_unsafeFormatString.lean",
    "veribench/security_6585/7_unsafeCommandExecution.lean",
    "veribench/security_6585/3_unsafeLinkedList.lean",
    "veribench/security_6585/9_pathTraversal.lean",
    "veribench/security_6585/1_unsafeMultiply.lean",
    "veribench/security_6585/2_unsafeMemoryAccess.lean",
    "veribench/security_6585/8_crossSiteScripting.lean",
    "veribench/security_6585/4_unsafeCounter.lean",
    "veribench/security_6585/6_unsafeSQLQuery.lean",
    "veribench/humaneval_lean/humaneval_49.lean",
    "veribench/humaneval_lean/humaneval_33.lean",
    "veribench/humaneval_lean/humaneval_5.lean",
    "veribench/humaneval_lean/humaneval_27.lean",
    "veribench/humaneval_lean/humaneval_16.lean",
    "veribench/humaneval_lean/humaneval_9.lean",
    "veribench/humaneval_lean/humaneval_13__gcd.lean",
    "veribench/humaneval_lean/humaneval_23.lean",
    "veribench/humaneval_lean/humaneval_41.lean",
    "veribench/humaneval_lean/humaneval_26.lean",
    "veribench/humaneval_lean/humaneval_17.lean",
    "veribench/humaneval_lean/humaneval_22.lean",
    "veribench/humaneval_lean/humaneval_36.lean",
    "veribench/humaneval_lean/humaneval_32.lean",
    "veribench/humaneval_lean/humaneval_24.lean",
    "veribench/humaneval_lean/humaneval_20.lean",
    "veribench/humaneval_lean/humaneval_38.lean",
    "veribench/humaneval_lean/humaneval_34.lean",
    "veribench/humaneval_lean/humaneval_2.lean",
    "veribench/humaneval_lean/humaneval_30.lean",
    "veribench/humaneval_lean/humaneval_28.lean",
    "veribench/humaneval_lean/humaneval_35.lean",
    "veribench/humaneval_lean/humaneval_3.lean",
    "veribench/humaneval_lean/humaneval_31.lean",
    "veribench/humaneval_lean/humaneval_0_hasCloseElements.lean",
    "veribench/humaneval_lean/humaneval_29.lean",
    "veribench/humaneval_lean/humaneval_25.lean",
    "veribench/humaneval_lean/humaneval_10.lean",
    "veribench/humaneval_lean/humaneval_21.lean",
    "veribench/humaneval_lean/humaneval_39.lean"
]

def fix_comment_blocks(file_path):
    """Fix malformed comment blocks in a Lean file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to find malformed comment blocks like:
        # /--
        # **Equivalence**: ...
        # -/
        # /-!
        # Replace with just /-!
        
        # This regex finds the pattern where we have a comment ending with -/ followed immediately by /-!
        pattern = r'/--\s*\*\*[^*]*\*\*[^-]*-/\s*/-!'
        replacement = '/-!'
        
        new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        # Also handle cases where there might be other malformed comment patterns
        # Look for -/ followed immediately by /-! and replace with just /-!
        pattern2 = r'-/\s*/-!'
        new_content = re.sub(pattern2, '/-!', new_content)
        
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ Fixed {file_path}")
            return True
        else:
            print(f"⚠️  No changes needed for {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    print("Fixing malformed comment blocks in failed compilation files...")
    
    fixed_count = 0
    for file_path in failed_files:
        if os.path.exists(file_path):
            if fix_comment_blocks(file_path):
                fixed_count += 1
        else:
            print(f"❌ File not found: {file_path}")
    
    print(f"\nFixed {fixed_count} files out of {len(failed_files)} failed files")
    
    # Test compilation of a few fixed files
    print("\nTesting compilation of a few fixed files...")
    test_files = failed_files[:3]  # Test first 3 files
    
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"Testing {file_path}...")
            result = subprocess.run(['lake', 'lean', file_path], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {file_path} compiles successfully")
            else:
                print(f"❌ {file_path} still has compilation errors")
                print(f"Error: {result.stderr[:200]}...")

if __name__ == "__main__":
    main()
