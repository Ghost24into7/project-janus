"""
System resource management.

Controls memory usage during
large document processing.

Responsibilities:

- Hardware inspection
- RAM monitoring
- Adaptive configuration
- Cleanup


Author:
    Myron

Python:
    3.12+
"""

from __future__ import annotations


import gc

import platform

from dataclasses import dataclass


import psutil


from core.logger import logger



@dataclass(slots=True)
class SystemProfile:
    """
    Hardware information.
    """

    total_ram_gb: float

    available_ram_gb: float

    cpu_count: int

    operating_system: str

    has_gpu: bool = False



@dataclass(slots=True)
class ProcessingLimits:
    """
    Dynamic pipeline limits.
    """

    max_parallel_pages: int

    rendering_dpi: int

    image_cache_enabled: bool

    aggressive_cleanup: bool



class MemoryManager:
    """
    Controls resource usage.
    """

    def __init__(self):

        self.profile = (
            self._detect_system()
        )


        self.limits = (
            self._calculate_limits()
        )


        logger.info(
            "Memory Manager initialized"
        )


        logger.info(
            "RAM %.2f GB",
            self.profile.total_ram_gb
        )



    def _detect_system(
        self,
    ) -> SystemProfile:
        """
        Detect hardware.
        """

        memory = psutil.virtual_memory()


        return SystemProfile(

            total_ram_gb=
            round(
                memory.total / (1024**3),
                2
            ),


            available_ram_gb=
            round(
                memory.available / (1024**3),
                2
            ),


            cpu_count=
            psutil.cpu_count(
                logical=True
            ),


            operating_system=
            platform.system(),

        )



    def _calculate_limits(
        self,
    ) -> ProcessingLimits:
        """
        Create safe limits.
        """

        ram = (
            self.profile.total_ram_gb
        )


        if ram <= 8:

            return ProcessingLimits(

                max_parallel_pages=1,

                rendering_dpi=150,

                image_cache_enabled=False,

                aggressive_cleanup=True,

            )


        elif ram <= 16:

            return ProcessingLimits(

                max_parallel_pages=1,

                rendering_dpi=200,

                image_cache_enabled=False,

                aggressive_cleanup=True,

            )


        else:

            return ProcessingLimits(

                max_parallel_pages=2,

                rendering_dpi=300,

                image_cache_enabled=True,

                aggressive_cleanup=False,

            )



    def is_memory_safe(
        self,
        minimum_free_gb: float = 1.5,
    ) -> bool:
        """
        Check available memory.
        """

        memory = psutil.virtual_memory()


        available = (
            memory.available
            /
            (1024**3)
        )


        logger.debug(
            "Available RAM %.2f GB",
            available,
        )


        return (
            available
            >
            minimum_free_gb
        )



    def cleanup(
        self,
    ) -> None:
        """
        Release unused memory.
        """

        gc.collect()


        logger.info(
            "Memory cleanup executed"
        )



    def get_limits(
        self,
    ) -> ProcessingLimits:

        return self.limits