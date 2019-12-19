from pyyaml import safe_load

with open("vars/output_params.yaml", "r", encoding='utf-8') as handle:
    safe_load(data, handle)