"""
File: main.py
Author: Furkan Ercan
Date: January 6, 2024

Description: Main script to run SC decoding for Polar Codes

License:
  This file is licensed under the MIT License.
  See the LICENSE file for details.
"""

from src.core.sim import Simulation

def main():
    simulation = Simulation()
    simulation.run_simulation()

if __name__ == "__main__":
    main()
