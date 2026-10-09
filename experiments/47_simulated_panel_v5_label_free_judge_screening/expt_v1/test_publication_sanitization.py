"""Private parser diagnostics must never appear in public aggregate evidence."""
import copy
import json
import unittest
from probe_publication_evidence import public_reason_counts


class PublicationSanitizationTests(unittest.TestCase):
    def test_private_responses_are_counted_without_publication_or_mutation(self):
        secret='PRIVATE_VERDICT_CANARY_47'
        cells=[
            {'acceptance_reason':'Invalid TC judge response: '+json.dumps({'reason':secret})},
            {'acceptance_reason':'Unexpected error: '+secret},
            {'acceptance_reason':secret},
            {'acceptance_reason':'MISSING_RESPONSE_BYTES'},
            {'acceptance_reason':'equal_delivered_prompt_hash'},
        ]
        original=copy.deepcopy(cells)
        result=public_reason_counts(cells)
        self.assertNotIn(secret,json.dumps(result))
        self.assertEqual(sum(result.values()),len(cells))
        self.assertEqual(result['FROZEN_PARSER_INVALID_RESPONSE'],1)
        self.assertEqual(result['UNCLASSIFIED_PRIVATE_REASON'],2)
        self.assertEqual(result['MISSING_RESPONSE_BYTES'],1)
        self.assertEqual(cells,original)


if __name__=='__main__':unittest.main()
