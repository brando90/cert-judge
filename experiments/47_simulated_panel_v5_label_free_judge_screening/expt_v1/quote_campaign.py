"""Exact admitted counts/bytes and explicit historical-rate cost assumptions."""
import argparse
import tiktoken
from e47_adapter import ROOT,RESULTS,PRIVATE,VENDOR,read,write,sha

def quote(phase):
    out=RESULTS/phase;private=PRIVATE/phase;packs=read(out/'packs.json');units={u['config']:u for u in read(out/'panel.json')['units']}
    historical=read(VENDOR/'QUOTE.json');rates=historical['prices_usd_per_million'];enc=tiktoken.get_encoding('cl100k_base');counts={};rows=[]
    for model,pack in packs['packs'].items():
        for cfg,data in pack['per_config'].items():
            cells=data['cells']+data['smoke_cells'];unit=units[cfg];total_bytes=total_tokens=0
            for c in cells:
                h=c['prompt_sha256']
                if h not in counts:
                    blob=read(private/'cells'/cfg.replace('|','__')/(c['cell']+'.json'));text=blob['system']+'\n\n'+blob['user']
                    if sha(text.encode())!=h:raise ValueError('quote prompt mismatch')
                    counts[h]=(len(text.encode()),len(enc.encode(text,disallowed_special=())))
                b,t=counts[h];total_bytes+=b;total_tokens+=t
            input_rate,output_rate=rates[model];n=len(cells)
            if unit['pack_flavor']=='agent':
                expected=(4*(total_tokens+n*3000)*input_rate+n*2000*output_rate)/1e6
                bound=None;basis='Assume 4 full-prompt turns plus 3000 harness tokens/turn and 2000 output tokens total; frozen harness max_turns=20, no newly imposed output cap.'
            else:
                expected=(total_tokens*input_rate+n*(4000 if model=='opus55x' else 1500)*output_rate)/1e6
                bound=((total_bytes+1024*n)*input_rate*1.25+n*unit['max_tokens']*output_rate)/1e6
                basis='cl100k_base input-token proxy, 4000 Opus or 1500 Qwen output-token assumption; original max_tokens retained.'
            rows.append({'config':cfg,'main_calls':len(data['cells']),'distinct_smoke_calls':len(data['smoke_cells']),'total_calls':n,'prompt_utf8_bytes':total_bytes,'cl100k_base_tokens':total_tokens,'tokenizer_is_provider_exact':False,'usd_per_million_assumption':[input_rate,output_rate],'expected_usd':expected,'single_call_conservative_bound_usd':bound,'basis':basis})
    receipt={'phase':phase,'route':'Vals-funded Valkyrie','new_calls':sum(r['total_calls'] for r in rows),'expected_usd':sum(r['expected_usd'] for r in rows),'rows':rows,
             'rate_source':'Frozen E39 QUOTE.json; historical registry/assumptions, not a claim of current provider pricing. Actual Valkyrie charges are authoritative.',
             'rate_source_sha256':sha((VENDOR/'QUOTE.json').read_bytes()),'admission_manifest_sha256':sha((out/'admission_manifest.json').read_bytes()),'packs_sha256':sha((out/'packs.json').read_bytes()),'automatic_dollar_cap':None,
             'limitations':'Exact request count and prompt-byte/tokenizer-proxy lengths; billing remains an estimate. Terminus2 tool/output history has no defensible finite dollar upper bound from the recorded harness alone.'}
    write(out/'QUOTE.json',receipt);print({'phase':phase,'new_calls':receipt['new_calls'],'expected_usd':receipt['expected_usd']})

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--phase',required=True,choices=['criterion','probes']);quote(ap.parse_args().phase)
