import os
import argparse

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(CURR_DIR, "../data/input")
OUTPUT_DIR = os.path.join(CURR_DIR, "../data/output")
RESULT_DIR = os.path.join(CURR_DIR, "../data/result")

parser = argparse.ArgumentParser(description="Quantum Circuit Extractor")
parser.add_argument("--benchmark", type=str, default=None, help="Benchmark name to extract")
args = parser.parse_args()
benchmark = args.benchmark

def get_benchmark(_s: str) -> str:
    return [os.path.join(INPUT_DIR, f) for f in os.listdir(INPUT_DIR) if f.endswith(".v") and _s in f][0]

ALL_INPUTS = [f for f in os.listdir(INPUT_DIR) if f.endswith(".v") and (not benchmark or benchmark in f)]
BMARKS = [(
    f.replace(".v", ""),
    os.path.join(INPUT_DIR, f), 
    os.path.join(OUTPUT_DIR, f.replace(".v", ".json")),
    os.path.join(RESULT_DIR, f.replace(".v", ".json"))
) for f in ALL_INPUTS]