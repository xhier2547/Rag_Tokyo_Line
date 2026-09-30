"""
src/llm/resource_profiler.py
============================
โมดูลสำหรับตรวจวัดการใช้ทรัพยากรของระบบ (Hardware Profiler)
รองรับการวัดผลแบบ Real-time ขนาดเบาขนานไปกับการรันโมเดล (Inference Profiling):
1. System RAM & Process Memory (RSS, Peak Memory) ผ่าน psutil
2. CPU Load (% System และ % Process)
3. GPU VRAM (Used MB, Allocated Delta MB, Peak VRAM) และ GPU Utilization % ผ่าน nvidia-smi
"""

import os
import sys
import time
import threading
import subprocess
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

try:
    import psutil
except ImportError:
    psutil = None

logger = logging.getLogger(__name__)


@dataclass
class HardwareSnapshot:
    """ข้อมูลสแนปช็อตทรัพยากร ณ เสี้ยววินาทีใดเสี้ยววินาทีหนึ่ง"""
    timestamp: float
    cpu_percent: float
    ram_used_mb: float
    ram_percent: float
    process_ram_mb: float
    gpu_vram_used_mb: Optional[float] = None
    gpu_util_percent: Optional[float] = None
    disk_read_mb_s: float = 0.0
    disk_write_mb_s: float = 0.0


@dataclass
class ResourceProfileResult:
    """ผลการสรุปเมตริกการใช้ทรัพยากรตลอดช่วงการทำงาน"""
    duration_sec: float = 0.0
    
    # SSD / Disk Protection
    avg_disk_read_mb_s: float = 0.0
    avg_disk_write_mb_s: float = 0.0
    peak_disk_write_mb_s: float = 0.0
    disk_safety_triggered: bool = False
    
    # CPU
    avg_cpu_percent: float = 0.0
    peak_cpu_percent: float = 0.0
    
    # System RAM
    baseline_ram_mb: float = 0.0
    peak_ram_mb: float = 0.0
    avg_ram_mb: float = 0.0
    ram_percent: float = 0.0
    
    # Process RAM
    baseline_process_ram_mb: float = 0.0
    peak_process_ram_mb: float = 0.0
    delta_process_ram_mb: float = 0.0
    
    # GPU / VRAM
    gpu_available: bool = False
    gpu_name: Optional[str] = None
    baseline_vram_mb: Optional[float] = None
    peak_vram_mb: Optional[float] = None
    delta_vram_mb: Optional[float] = None
    total_vram_mb: Optional[float] = None
    avg_gpu_util_percent: Optional[float] = None
    peak_gpu_util_percent: Optional[float] = None
    
    samples_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """แปลงผลลัพธ์เป็น Dictionary สำหรับบันทึก JSON"""
        return {
            "duration_sec": round(self.duration_sec, 3),
            "disk_io": {
                "avg_read_mb_s": round(self.avg_disk_read_mb_s, 2),
                "avg_write_mb_s": round(self.avg_disk_write_mb_s, 2),
                "peak_write_mb_s": round(self.peak_disk_write_mb_s, 2),
                "safety_circuit_triggered": self.disk_safety_triggered
            },
            "cpu": {
                "avg_cpu_percent": round(self.avg_cpu_percent, 1),
                "peak_cpu_percent": round(self.peak_cpu_percent, 1)
            },
            "ram": {
                "baseline_ram_mb": round(self.baseline_ram_mb, 1),
                "avg_ram_mb": round(self.avg_ram_mb, 1),
                "peak_ram_mb": round(self.peak_ram_mb, 1),
                "ram_percent": round(self.ram_percent, 1),
                "process_rss_peak_mb": round(self.peak_process_ram_mb, 1),
                "process_rss_delta_mb": round(self.delta_process_ram_mb, 1)
            },
            "gpu": {
                "available": self.gpu_available,
                "name": self.gpu_name,
                "total_vram_mb": round(self.total_vram_mb, 1) if self.total_vram_mb else None,
                "baseline_vram_mb": round(self.baseline_vram_mb, 1) if self.baseline_vram_mb else None,
                "peak_vram_mb": round(self.peak_vram_mb, 1) if self.peak_vram_mb else None,
                "delta_vram_mb": round(self.delta_vram_mb, 1) if self.delta_vram_mb else None,
                "avg_gpu_util_percent": round(self.avg_gpu_util_percent, 1) if self.avg_gpu_util_percent is not None else None,
                "peak_gpu_util_percent": round(self.peak_gpu_util_percent, 1) if self.peak_gpu_util_percent is not None else None
            },
            "samples_count": self.samples_count
        }


class HardwareProfiler:
    """
    Context manager สำหรับวัดทรัพยากรเบื้องหลัง (Background Polling Thread)
    ความถี่สุ่มตรวจเริ่มต้น 50ms โดยไม่กิน CPU ของระบบ
    """

    def __init__(self, sample_interval_sec: float = 0.15, max_safe_disk_write_mb_s: float = 40.0):
        self.sample_interval = sample_interval_sec
        self.max_safe_disk_write_mb_s = max_safe_disk_write_mb_s
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._snapshots: List[HardwareSnapshot] = []
        self._start_time: float = 0.0
        self._end_time: float = 0.0
        self._gpu_info = self._detect_gpu()
        self._current_process = psutil.Process() if psutil else None
        self._last_disk_io = psutil.disk_io_counters() if psutil else None
        self._last_disk_time = time.time()
        self._safety_triggered = False

    @staticmethod
    def _detect_gpu() -> Dict[str, Any]:
        """ตรวจสอบและดึงข้อมูล GPU เบื้องต้นผ่าน nvidia-smi"""
        try:
            cmd = ["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"]
            out = subprocess.check_output(cmd, encoding="utf-8", timeout=2).strip()
            if out:
                parts = [p.strip() for p in out.split(",")]
                return {
                    "available": True,
                    "name": parts[0],
                    "total_vram_mb": float(parts[1]) if len(parts) > 1 else None
                }
        except Exception:
            pass
        return {"available": False, "name": None, "total_vram_mb": None}

    def _query_live_gpu(self) -> tuple[Optional[float], Optional[float]]:
        """ดึง VRAM Used (MB) และ GPU Utilization (%) ณ ปัจจุบัน"""
        if not self._gpu_info["available"]:
            return None, None
        try:
            cmd = ["nvidia-smi", "--query-gpu=memory.used,utilization.gpu", "--format=csv,noheader,nounits"]
            out = subprocess.check_output(cmd, encoding="utf-8", timeout=1.5).strip()
            if out:
                parts = [p.strip() for p in out.split(",")]
                vram_used = float(parts[0])
                gpu_util = float(parts[1])
                return vram_used, gpu_util
        except Exception:
            pass
        return None, None

    def _query_disk_io(self) -> tuple[float, float]:
        """คำนวณอัตรา Read/Write ของ SSD ปัจจุบัน (MB/s) เพื่อป้องกัน Disk Thrashing"""
        if not psutil:
            return 0.0, 0.0
        try:
            now = time.time()
            curr_io = psutil.disk_io_counters()
            dt = max(0.001, now - self._last_disk_time)
            if self._last_disk_io and curr_io:
                read_mb_s = ((curr_io.read_bytes - self._last_disk_io.read_bytes) / (1024 * 1024)) / dt
                write_mb_s = ((curr_io.write_bytes - self._last_disk_io.write_bytes) / (1024 * 1024)) / dt
            else:
                read_mb_s, write_mb_s = 0.0, 0.0
            self._last_disk_io = curr_io
            self._last_disk_time = now
            
            if write_mb_s > self.max_safe_disk_write_mb_s:
                self._safety_triggered = True
                logger.warning(f"[SSD SAFETY CIRCUIT] Disk write spike detected: {write_mb_s:.1f} MB/s > limit {self.max_safe_disk_write_mb_s} MB/s")
                
            return max(0.0, read_mb_s), max(0.0, write_mb_s)
        except Exception:
            return 0.0, 0.0

    def _sample_loop(self):
        """ลูปเบื้องหลังสำหรับบันทึกสแนปช็อตทรัพยากรตามช่วงเวลาที่กำหนดอย่างปลอดภัย"""
        while self._running:
            try:
                cpu = psutil.cpu_percent(interval=None) if psutil else 0.0
                vmem = psutil.virtual_memory() if psutil else None
                ram_used = (vmem.used / (1024 * 1024)) if vmem else 0.0
                ram_pct = vmem.percent if vmem else 0.0
                
                # Process RAM
                proc_ram = 0.0
                if self._current_process:
                    try:
                        proc_ram = self._current_process.memory_info().rss / (1024 * 1024)
                    except Exception:
                        pass
                
                vram_used, gpu_util = self._query_live_gpu()
                disk_read, disk_write = self._query_disk_io()

                snap = HardwareSnapshot(
                    timestamp=time.time(),
                    cpu_percent=cpu,
                    ram_used_mb=ram_used,
                    ram_percent=ram_pct,
                    process_ram_mb=proc_ram,
                    gpu_vram_used_mb=vram_used,
                    gpu_util_percent=gpu_util,
                    disk_read_mb_s=disk_read,
                    disk_write_mb_s=disk_write
                )
                self._snapshots.append(snap)
            except Exception as e:
                logger.debug(f"[HardwareProfiler] Sample error: {e}")
            
            time.sleep(self.sample_interval)

    def start(self):
        """เริ่มต้นการบันทึกข้อมูลทรัพยากร"""
        self._snapshots.clear()
        self._running = True
        self._safety_triggered = False
        self._start_time = time.time()
        self._last_disk_time = self._start_time
        if psutil:
            self._last_disk_io = psutil.disk_io_counters()
        
        # เก็บ snapshot แรกทันที
        self._sample_once()
        
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()

    def _sample_once(self):
        """เก็บ snapshot เดียวแบบ synchronous"""
        cpu = psutil.cpu_percent(interval=None) if psutil else 0.0
        vmem = psutil.virtual_memory() if psutil else None
        ram_used = (vmem.used / (1024 * 1024)) if vmem else 0.0
        ram_pct = vmem.percent if vmem else 0.0
        proc_ram = 0.0
        if self._current_process:
            try:
                proc_ram = self._current_process.memory_info().rss / (1024 * 1024)
            except Exception:
                pass
        vram_used, gpu_util = self._query_live_gpu()
        disk_read, disk_write = self._query_disk_io()
        self._snapshots.append(HardwareSnapshot(
            timestamp=time.time(),
            cpu_percent=cpu,
            ram_used_mb=ram_used,
            ram_percent=ram_pct,
            process_ram_mb=proc_ram,
            gpu_vram_used_mb=vram_used,
            gpu_util_percent=gpu_util,
            disk_read_mb_s=disk_read,
            disk_write_mb_s=disk_write
        ))

    def stop(self) -> ResourceProfileResult:
        """หยุดการบันทึกและคำนวณผลสรุปสถิติทรัพยากร"""
        self._running = False
        self._end_time = time.time()
        if self._thread:
            self._thread.join(timeout=1.0)
            
        # เก็บ snapshot ปิดท้าย
        self._sample_once()

        duration = max(0.001, self._end_time - self._start_time)
        if not self._snapshots:
            return ResourceProfileResult(duration_sec=duration)

        cpus = [s.cpu_percent for s in self._snapshots if s.cpu_percent > 0]
        rams = [s.ram_used_mb for s in self._snapshots]
        proc_rams = [s.process_ram_mb for s in self._snapshots]
        vrams = [s.gpu_vram_used_mb for s in self._snapshots if s.gpu_vram_used_mb is not None]
        gpu_utils = [s.gpu_util_percent for s in self._snapshots if s.gpu_util_percent is not None]
        disk_reads = [s.disk_read_mb_s for s in self._snapshots]
        disk_writes = [s.disk_write_mb_s for s in self._snapshots]

        baseline_ram = rams[0] if rams else 0.0
        peak_ram = max(rams) if rams else 0.0
        avg_ram = sum(rams) / len(rams) if rams else 0.0

        baseline_proc = proc_rams[0] if proc_rams else 0.0
        peak_proc = max(proc_rams) if proc_rams else 0.0
        delta_proc = max(0.0, peak_proc - baseline_proc)

        baseline_vram = vrams[0] if vrams else None
        peak_vram = max(vrams) if vrams else None
        delta_vram = max(0.0, peak_vram - baseline_vram) if (peak_vram is not None and baseline_vram is not None) else None

        avg_disk_read = sum(disk_reads) / len(disk_reads) if disk_reads else 0.0
        avg_disk_write = sum(disk_writes) / len(disk_writes) if disk_writes else 0.0
        peak_disk_write = max(disk_writes) if disk_writes else 0.0

        return ResourceProfileResult(
            duration_sec=duration,
            avg_disk_read_mb_s=avg_disk_read,
            avg_disk_write_mb_s=avg_disk_write,
            peak_disk_write_mb_s=peak_disk_write,
            disk_safety_triggered=self._safety_triggered,
            avg_cpu_percent=sum(cpus) / len(cpus) if cpus else 0.0,
            peak_cpu_percent=max(cpus) if cpus else 0.0,
            baseline_ram_mb=baseline_ram,
            peak_ram_mb=peak_ram,
            avg_ram_mb=avg_ram,
            ram_percent=self._snapshots[-1].ram_percent if self._snapshots else 0.0,
            baseline_process_ram_mb=baseline_proc,
            peak_process_ram_mb=peak_proc,
            delta_process_ram_mb=delta_proc,
            gpu_available=self._gpu_info["available"],
            gpu_name=self._gpu_info["name"],
            baseline_vram_mb=baseline_vram,
            peak_vram_mb=peak_vram,
            delta_vram_mb=delta_vram,
            total_vram_mb=self._gpu_info["total_vram_mb"],
            avg_gpu_util_percent=sum(gpu_utils) / len(gpu_utils) if gpu_utils else None,
            peak_gpu_util_percent=max(gpu_utils) if gpu_utils else None,
            samples_count=len(self._snapshots)
        )

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
