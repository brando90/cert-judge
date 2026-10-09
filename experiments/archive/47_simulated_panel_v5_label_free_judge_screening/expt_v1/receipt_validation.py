"""Fail-closed receipt transport binding and repeat identity validation."""
import math

def transport_evidence(receipt,expected_hash,expected_instruction=None):
    delivered=receipt.get('prompt_sha256_delivered')
    if delivered is not None:
        return (delivered==expected_hash,'equal_delivered_prompt_hash' if delivered==expected_hash else 'DELIVERED_HASH_MISMATCH')
    served=receipt.get('instruction_sha256_served')
    if expected_instruction and served==expected_instruction:
        return True,'delivered_hash_unavailable; exact served instruction hash and frozen pack round-trip'
    return False,'DELIVERED_HASH_UNAVAILABLE_WITHOUT_ALTERNATIVE_EVIDENCE'

def accepted(receipt,expected_hash,expected_instruction=None):
    if receipt.get('http_status')==429:return False,'HTTP_429_INFRASTRUCTURE_FAILURE'
    if receipt.get('category',receipt.get('status')) not in ('COMPLETE','measured','deterministic'):
        return False,receipt.get('category',receipt.get('status','MISSING'))
    if receipt.get('status')=='deterministic':return True,'frozen_deterministic_rule'
    value=receipt.get('score')
    if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value) or not 0<=value<=1:
        return False,'INVALID_SCORE'
    return transport_evidence(receipt,expected_hash,expected_instruction)

def unique_repeats(rows):
    seen=set()
    for row in rows:
        r=row['repeat']
        if r in seen:raise ValueError('duplicate repeat index')
        seen.add(r)
    return True
