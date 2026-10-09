import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import artifact_paths as paths

class ArtifactRelocationTests(unittest.TestCase):
    def test_move_preserves_bytes_and_original_receipt_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);old=base/'active/expt_v1';new=base/'archive/expt_v1'
            recorded=old/'private/probes/packs/model/task/instruction.md'
            recorded.parent.mkdir(parents=True);recorded.write_bytes(b'frozen instruction\n')
            frozen=json.dumps({'pack':str(recorded.parent),'source_collection_path':str(recorded)}).encode()
            with patch.object(paths,'ORIGINAL_ROOT',old),patch.object(paths,'ROOT',old):
                self.assertEqual(paths.local_path(recorded),recorded)
            new.parent.mkdir();old.rename(new)
            with patch.object(paths,'ORIGINAL_ROOT',old),patch.object(paths,'ROOT',new):
                actual=paths.local_path(recorded)
                self.assertEqual(actual.read_bytes(),b'frozen instruction\n')
                self.assertEqual(paths.historical_path(actual),str(recorded))
                self.assertEqual(json.loads(frozen)['source_collection_path'],paths.historical_path(actual))
                self.assertEqual(paths.local_path(base/'other/receipt.json'),base/'other/receipt.json')
                with self.assertRaises(ValueError):paths.local_path(old/'../other/receipt.json')

if __name__=='__main__':unittest.main()
