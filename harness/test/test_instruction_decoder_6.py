import os
import random
from pathlib import Path

import cocotb
from cocotb import start_soon
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, NextTimeStep, ReadOnly, RisingEdge, Timer
from cocotb_tools.runner import get_runner

@cocotb.test()
async def example_test(dut):
    pass

def test_instruction_decoder_6_runner():
    sim = os.getenv("SIM", "icarus")

    proj_path = Path(__file__).resolve().parent.parent

    sources = [proj_path / "sources/instruction_decoder_6.v"]

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="instruction_decoder_6",
        always=True,
    )

    runner.test(hdl_toplevel="instruction_decoder_6", test_module="test_instruction_decoder_6")
