"""
tests/test_resource_profiler.py
===============================
Automated Unit Tests สำหรับโมดูล HardwareProfiler
"""

import time
import pytest
from src.llm.resource_profiler import HardwareProfiler, ResourceProfileResult


def test_hardware_profiler_lifecycle():
    """ทดสอบวงจรการทำงาน Start -> Stop และการคำนวณสถิติ"""
    profiler = HardwareProfiler(sample_interval_sec=0.02)
    profiler.start()
    
    # จำลองการทำงานเล็กน้อย
    time.sleep(0.1)
    
    res = profiler.stop()
    assert isinstance(res, ResourceProfileResult)
    assert res.duration_sec >= 0.08
    assert res.samples_count >= 2
    assert res.baseline_ram_mb > 0
    assert res.peak_ram_mb >= res.baseline_ram_mb
    
    d = res.to_dict()
    assert "cpu" in d
    assert "ram" in d
    assert "gpu" in d
    assert d["ram"]["baseline_ram_mb"] > 0


def test_hardware_profiler_context_manager():
    """ทดสอบการใช้งานผ่าน with statement (Context Manager)"""
    with HardwareProfiler(sample_interval_sec=0.02) as profiler:
        time.sleep(0.05)
    
    res = profiler.stop()
    assert res.duration_sec > 0
    assert res.samples_count >= 1


def test_hardware_profiler_ssd_safety():
    """ทดสอบการตรวจวัด Disk I/O และระบบป้องกัน SSD Spike"""
    # กำหนด threshold ต่ำมากเพื่อทดสอบการ trigger ปลอดภัย
    profiler = HardwareProfiler(sample_interval_sec=0.02, max_safe_disk_write_mb_s=0.00001)
    profiler.start()
    time.sleep(0.05)
    res = profiler.stop()
    
    d = res.to_dict()
    assert "disk_io" in d
    assert "avg_read_mb_s" in d["disk_io"]
    assert "avg_write_mb_s" in d["disk_io"]
    assert "safety_circuit_triggered" in d["disk_io"]
