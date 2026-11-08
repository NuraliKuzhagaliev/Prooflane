"""Repeatable CPU-only benchmark; no Docker, network or model requests."""
import argparse
import hashlib
import json
import platform
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from prooflane.analysis import canonical
from prooflane.intelligence import explore, targets_for
from prooflane.reconciliation import reconcile


def fixture(size=500):
    invoices = ['invoice_id,vendor,item_id,invoice_date,quantity,unit_price,notes']
    contracts = ['contract_id,vendor,item_id,valid_from,valid_to,contract_price']
    for n in range(size):
        invoices.append(f'I{n},V{n % 8},ITEM{n},2026-11-01,{10 + n % 20},{90 + n % 9}.25,synthetic')
        contracts.append(f'C{n},V{n % 8},ITEM{n},2026-01-01,2026-12-31,72.00')
    return '\n'.join(invoices) + '\n', '\n'.join(contracts) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label', required=True)
    parser.add_argument('--samples', type=int, default=9)
    args = parser.parse_args()
    inv, con = fixture()
    source = reconcile(inv, con)
    csv = source['canonical_csv']
    targets = targets_for(csv, source['bindings'])
    bounds = [{'target': f'contract:C{n}', 'low': '65.00', 'high': '85.00'} for n in range(24)]
    work = {'match_500x500': lambda: reconcile(inv, con),
            'explore_500x12': lambda: explore(csv, targets, bounds[:12]),
            'explore_500x24': lambda: explore(csv, targets, bounds)}
    report = {'label': args.label, 'python': sys.version, 'platform': platform.platform(),
              'scope': 'CPU only, synthetic500 invoices/500 contracts, same fixture, no model or network',
              'fixture_sha256': hashlib.sha256((inv + con).encode()).hexdigest(), 'samples': args.samples,
              'warmups': 2, 'results': {}}
    for name, fn in work.items():
        for _ in range(2):
            fn()
        times = []
        for _ in range(args.samples):
            start = time.perf_counter()
            result = fn()
            times.append((time.perf_counter() - start) * 1000)
        report['results'][name] = {'median_ms': statistics.median(times), 'min_ms': min(times),
                                    'max_ms': max(times), 'samples_ms': times,
                                    'result_sha256': hashlib.sha256(canonical(result).encode()).hexdigest()}
    out = ROOT / 'artifacts' / 'transformation-20261108' / ('performance-' + args.label + '.json')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({name: round(value['median_ms'], 3) for name, value in report['results'].items()}))


if __name__ == '__main__':
    main()
