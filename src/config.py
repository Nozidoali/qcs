import os
import argparse

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(CURR_DIR, "../data/input")
RESULT_DIR = os.path.join(CURR_DIR, "../data/result")

parser = argparse.ArgumentParser(description="Quantum Circuit Extractor")

args = parser.parse_args()

ALL_INPUTS = [f for f in os.listdir(INPUT_DIR) if f.endswith(".v")]

BMARKS = [(
    f.replace(".v", ""),
    os.path.join(INPUT_DIR, f), 
    os.path.join(RESULT_DIR, f.replace(".v", ".json"))
) for f in ALL_INPUTS]