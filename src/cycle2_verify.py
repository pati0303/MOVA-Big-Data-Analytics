"""Reproduce the frozen experiment without writing files, also after new commits.

Run: python src/cycle2_verify.py. Six fold fits are executed in memory.
The original run's base commit remains historical provenance and is not replaced.
"""
import json
import subprocess
from unittest.mock import patch
import cycle2_compare as experiment


def verify(root=experiment.ROOT):
    recorded=json.loads((root/'outputs/cycle2/run_manifest.json').read_text())
    subprocess.run(['git','merge-base','--is-ancestor',recorded['source_base_commit'],'HEAD'],
                   cwd=root,check=True,capture_output=True)
    checked=[]
    def compare(output_root,payloads):
        for name,payload in payloads.items():
            saved=(output_root/name).read_bytes()
            if name=='outputs/cycle2/run_manifest.json':
                current=json.loads(payload)
                original=json.loads(saved)
                # Only HEAD may change when the unchanged experiment is committed.
                current.pop('source_base_commit')
                original.pop('source_base_commit')
                experiment.require(current==original,'Reproduction manifest differs')
            else:
                experiment.require(saved==payload,'Reproduction differs: '+name)
            checked.append(name)
    with patch.object(experiment,'persist',side_effect=compare):
        experiment.main(root)
    experiment.require(len(checked)==11,'Unexpected artifact count')
    print('VERIFIED: all 10 experiment artifacts byte-identical; manifest unchanged except current HEAD provenance. No files written.')


if __name__=='__main__':verify()
