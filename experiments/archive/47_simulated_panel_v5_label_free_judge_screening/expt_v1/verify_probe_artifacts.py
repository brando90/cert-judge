"""Read-only replay gate for the complete frozen probe outcome and cache chain.

Replay uses only recorded compiler answers. It cannot compile, create probes, or
write owner artifacts. Missing cache evidence fails rather than invoking Lean.
"""
import ast
from collections import defaultdict
from pathlib import Path
import sys

from e47_adapter import REPO, VENDOR, module, sha, verify_dependencies

BUILDER_SHA256 = 'abcd091d68d43b09bd274003cea983f4c16263d6bc892e610bc1be4fbaaff738'
PROBE_RUN_ID = 'cj-e47-probes-10-08-2026-a1'
FUNCTIONS = {'make_row', 'build_one', 'receipt_public', 'compile_reason', 'counts'}


def load_transforms():
    verify_dependencies()
    sys.path.insert(0, str(REPO/'py_src'))
    return module('e47_readonly_probe_transform', VENDOR/'probes.py')


class MissingCompileEvidence(RuntimeError):
    """Must not be swallowed by the frozen mutation search's ValueError handler."""


def unique(rows, key):
    result = {}
    for row in rows:
        value = key(row)
        if value in result:
            raise ValueError('duplicate probe identity '+str(value))
        result[value] = row
    return result


def without_reuse(value):
    if isinstance(value, dict):
        return {k: without_reuse(v) for k, v in value.items() if k != 'reused'}
    if isinstance(value, list):
        return [without_reuse(v) for v in value]
    return value


class RecordedCompiler:
    def __init__(self, cache_rows, environment):
        self.records = {}
        self.used = set()
        for row in cache_rows:
            if row.get('environment') != environment:
                continue
            if (not isinstance(row.get('ok'), bool) or row.get('ok') != (row.get('returncode') == 0)
                    or not all(k in row for k in ('sha256', 'returncode', 'output_sha256', 'finished_utc', 'output'))):
                raise ValueError('invalid terminal compilation evidence')
            digest = row['sha256']
            if digest in self.records and without_reuse(row) != without_reuse(self.records[digest]):
                raise ValueError('conflicting terminal compilation evidence '+digest)
            self.records[digest] = row

    def compile(self, text):
        digest = sha(text.encode())
        if digest not in self.records:
            raise MissingCompileEvidence('no terminal compilation in pinned environment '+digest)
        self.used.add(digest)
        return {**self.records[digest], 'reused': True}


def frozen_builder_functions(builder_bytes, transforms, artifact):
    if sha(builder_bytes) != BUILDER_SHA256:
        raise ValueError('probe builder differs from verified frozen schema')
    tree = ast.parse(builder_bytes)
    definitions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in FUNCTIONS]
    if {node.name for node in definitions} != FUNCTIONS:
        raise ValueError('frozen probe schema functions missing')
    # Evaluate only pure builder functions, with the file writer replaced by an
    # in-memory record. Do not import/execute the owner's main or Compiler.
    tree = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0), *definitions], type_ignores=[])
    namespace = {'P': transforms, 'private_artifact': artifact}
    exec(compile(ast.fix_missing_locations(tree), '<verified-frozen-probe-builder>', 'exec'), namespace)
    return namespace


def verify_transformed_artifacts(source, manifest, cache_rows, environment, expt, builder_path):
    """Check all expected rows, including unavailable levels, and actual bytes."""
    transforms = load_transforms()
    transform_hash = sha((VENDOR/'probes.py').read_bytes())
    if manifest.get('run_id') != PROBE_RUN_ID or manifest.get('frozen_transform', {}).get('sha256') != transform_hash:
        raise ValueError('probe manifest transform/run identity differs')
    if manifest['frozen_transform'].get('kinds') != {'ident': 0, 'blank': 0, 'ms_gold': 4, 'ms_cand': 3, 'bm_gold': 4}:
        raise ValueError('probe kinds differ from frozen builder')
    expected_artifacts = {}

    def artifact(kind, key, level, code):
        name = f'private/probes_worker/artifacts/{kind}/{key}__L{level}.lean'
        data = code.encode('utf-8')
        record = {'kind': kind, 'key': key, 'level': level, 'sha256': sha(data), 'private_relpath': name}
        identity = (kind, key, level)
        if identity in expected_artifacts:
            raise ValueError('duplicate replay artifact')
        expected_artifacts[identity] = (record, data)
        return record

    builder = frozen_builder_functions(Path(builder_path).read_bytes(), transforms, artifact)
    compiler = RecordedCompiler(cache_rows, environment)
    expt = Path(expt).resolve()
    inputs = expt/'private/probes_worker/input_bytes'

    def source_code(path, digest):
        if path.is_symlink() or not path.resolve().is_relative_to(inputs.resolve()):
            raise ValueError('unsafe probe input path')
        data = path.read_bytes()
        if sha(data) != digest:
            raise ValueError('probe source bytes differ')
        return data.decode('utf-8', errors='replace')

    references = unique(source['references'], lambda r: r['task'])
    candidates = unique(source['candidates'], lambda r: r['item'])
    by_task = defaultdict(list)
    for row in candidates.values():
        candidate = dict(row)
        if not row['blank'] and row['source_status'] == 'verified':
            candidate['code'] = source_code(inputs/'candidates'/row['group']/(row['harbor']+'.lean'), row['actual_sha256'])
        by_task[row['task']].append(candidate)
    if set(references) != set(by_task):
        raise ValueError('probe reference/candidate task universe differs')
    expected = []
    for task in sorted(references):
        reference = dict(references[task])
        reference['code'] = source_code(inputs/'references'/(reference['harbor']+'.lean'), reference['actual_sha256'])
        rows, _ = builder['build_one'](task, reference, sorted(by_task[task], key=lambda r: r['item']), compiler)
        expected.extend(rows)
    observed = unique(manifest['rows'], lambda r: r['probe_id'])
    wanted = unique(expected, lambda r: r['probe_id'])
    if set(observed) != set(wanted):
        raise ValueError('incomplete or extra frozen probe outcomes: missing=%d extra=%d' %
                         (len(set(wanted)-set(observed)), len(set(observed)-set(wanted))))
    for key, row in wanted.items():
        if without_reuse(observed[key]) != without_reuse(row):
            raise ValueError('probe outcome/terminal cache chain differs '+key)
    if manifest.get('counts') != builder['counts'](expected):
        raise ValueError('probe outcome counts differ')
    actual_artifacts = unique(manifest['private_artifacts'], lambda r: (r['kind'], r['key'], r['level']))
    if set(actual_artifacts) != set(expected_artifacts):
        raise ValueError('incomplete or extra materialized probe artifacts')
    for identity, (record, data) in expected_artifacts.items():
        if actual_artifacts[identity] != record:
            raise ValueError('probe artifact identity differs '+str(identity))
        path = expt/record['private_relpath']
        if path.is_symlink() or not path.resolve().is_relative_to((expt/'private/probes_worker/artifacts').resolve()):
            raise ValueError('unsafe materialized artifact path')
        if path.read_bytes() != data:
            raise ValueError('materialized probe artifact bytes differ '+str(identity))
    return {'builder_sha256': BUILDER_SHA256, 'transform_sha256': transform_hash,
            'expected_rows': len(wanted), 'verified_artifacts': len(expected_artifacts),
            'terminal_cache_hashes_used': len(compiler.used), 'compiler_calls': 0,
            'new_probe_files_written': 0, 'unavailable_rows': sum(not r['valid'] for r in expected)}
