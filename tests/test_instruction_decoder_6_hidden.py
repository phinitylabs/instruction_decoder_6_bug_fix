import cocotb
from cocotb.triggers import Timer
import os
import random
from pathlib import Path
from cocotb_tools.runner import get_runner

# ------------------------------------------------------------
# Helper: check outputs
# ------------------------------------------------------------
async def check_outputs(dut, exp, label=""):
    await Timer(1, units="ns")

    for signal, expected in exp.items():
        actual = int(getattr(dut, signal).value)
        assert actual == expected, (
            f"{label}: {signal} expected {expected}, got {actual}"
        )


# ------------------------------------------------------------
# Test 0 – Decoder disabled when ID != 110
# ------------------------------------------------------------
@cocotb.test()
async def test_id_disable(dut):

    dut.id.value = 0b000     # not 110
    dut.instr_in.value = 0
    dut.cc_in.value = 0
    dut.instr_en.value = 0

    await Timer(2, units='ns')

    expected = {
        "rst":0, "out_ce":0, "rsel":0, "rce":0, "cen":0,
        "stack_re":0, "pop":0, "stack_we":0,
        "a_mux_sel":2, "b_mux_sel":2,
        "oen":0, "pc_mux_sel":0, "inc":0,
        "src_sel":0, "push":0
    }

    await check_outputs(dut, expected, "ID != 110 → disabled")


# ------------------------------------------------------------
# Helper: run instruction with ID = 110
# ------------------------------------------------------------
async def run_instr(dut, instr, cc, en, expected, label):
    dut.id.value = 0b110
    dut.instr_in.value = instr
    dut.cc_in.value = cc
    dut.instr_en.value = en

    await Timer(2, units='ns')
    await check_outputs(dut, expected, label)


# ------------------------------------------------------------
# Instruction Tests
# ------------------------------------------------------------

# 1) Instruction Disable — 7'b0110101
@cocotb.test()
async def test_instruction_disable(dut):

    expected = {
        "rst":0, "out_ce":0, "rsel":0, "rce":0, "cen":0,
        "stack_re":0, "pop":0, "stack_we":0,
        "a_mux_sel":2, "b_mux_sel":2,
        "oen":1, "pc_mux_sel":0, "inc":0,
        "src_sel":0, "push":0
    }

    await run_instr(
        dut,
        instr=0b01101,
        cc=0,
        en=1,
        expected=expected,
        label="Instruction Disable"
    )


# 2) JSB R — 7'b1011000
@cocotb.test()
async def test_jsb_r(dut):

    expected = {
        "rst":0, "out_ce":0,
        "rsel":0, "rce":1, "cen":0,
        "stack_re":0, "pop":0,
        "a_mux_sel":1, "b_mux_sel":2,
        "oen":1, "pc_mux_sel":0, "inc":1,
        "src_sel":0, "push":1, "stack_we":1
    }

    await run_instr(
        dut,
        instr=0b10110,
        cc=0,
        en=0,
        expected=expected,
        label="JSB R (1011000)"
    )


# 3) JSB D — 7'b1011100
@cocotb.test()
async def test_jsb_d(dut):

    expected = {
        "rst":0, "out_ce":0,
        "rsel":0, "rce":1, "cen":0,
        "stack_re":0, "pop":0,
        "a_mux_sel":0, "b_mux_sel":2,
        "oen":1, "pc_mux_sel":0, "inc":1,
        "src_sel":0, "push":1, "stack_we":1
    }

    await run_instr(
        dut,
        instr=0b10111,
        cc=0,
        en=0,
        expected=expected,
        label="JSB D (1011100)"
    )


# 4) JSB 0 — 7'b1100000
@cocotb.test()
async def test_jsb_0(dut):

    expected = {
        "rst":0, "out_ce":0,
        "rsel":0, "rce":1, "cen":0,
        "stack_re":0, "pop":0,
        "a_mux_sel":2, "b_mux_sel":2,
        "oen":1, "pc_mux_sel":0, "inc":1,
        "src_sel":0, "push":1, "stack_we":1
    }

    await run_instr(
        dut,
        instr=0b11000,
        cc=0,
        en=0,
        expected=expected,
        label="JSB 0 (1100000)"
    )


# 5) JSB R + D — 7'b1100100
@cocotb.test()
async def test_jsb_r_plus_d(dut):

    expected = {
        "rst":0, "out_ce":0,
        "rsel":0, "rce":1, "cen":1,
        "stack_re":0, "pop":0,
        "a_mux_sel":0, "b_mux_sel":3,
        "oen":1, "pc_mux_sel":0, "inc":1,
        "src_sel":0, "push":1, "stack_we":1
    }

    await run_instr(
        dut,
        instr=0b11001,
        cc=0,
        en=0,
        expected=expected,
        label="JSB R + D (1100100)"
    )


# 6) JSB PC + D — 7'b1101000
@cocotb.test()
async def test_jsb_pc_plus_d(dut):

    expected = {
        "rst":0, "out_ce":0,
        "rsel":0, "rce":1, "cen":1,
        "stack_re":0, "pop":0,
        "a_mux_sel":0, "b_mux_sel":0,
        "oen":1, "pc_mux_sel":0, "inc":1,
        "src_sel":0, "push":1, "stack_we":1
    }

    await run_instr(
        dut,
        instr=0b11010,
        cc=0,
        en=0,
        expected=expected,
        label="JSB PC + D (1101000)"
    )

def test_instruction_decoder_6_hidden_runner():
    sim = os.getenv("SIM", "icarus")

    proj_path = Path(__file__).resolve().parent.parent

    sources = [proj_path / "sources/instruction_decoder_6.v"]

    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="instruction_decoder_6",
        always=True,
    )
    runner.test(hdl_toplevel="instruction_decoder_6", test_module="test_instruction_decoder_6_hidden")
