from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class AnalysisMode(str, Enum):
    AUTO = "AUTO"
    VMAT_IMRT = "VMAT_IMRT"
    TOMO = "TOMO"
    CYBERKNIFE_MLC = "CYBERKNIFE_MLC"
    AURORA = "AURORA"


@dataclass
class PlanAnalysisResult:
    source_path: str
    mode: AnalysisMode
    metadata: Dict[str, Any]
    metrics: Dict[str, Any]
    flattened_metrics: Dict[str, Any]
    supported: bool
    warnings: List[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "READY" if self.supported else "UNSUPPORTED"

    @property
    def reason_label(self) -> str:
        warning_text = " ".join(self.warnings).lower()
        if "xml" in warning_text and ("external" in warning_text or "beam-path" in warning_text):
            return "Missing external XML"
        if "mlc leaf geometry" in warning_text or "leaf-path geometry" in warning_text:
            return "Missing MLC geometry"
        if "aperture geometry is empty or incomplete" in warning_text:
            return "Incomplete aperture geometry"
        if "overrides detected mode" in warning_text:
            return "Mode override"
        if "missing axial trajectory" in warning_text:
            return "Missing axial trajectory"
        if "incompatible manufacturer/model" in warning_text:
            return "Incompatible manufacturer/model hints"
        if "unsupported plan geometry" in warning_text:
            return "Unsupported plan geometry"
        if self.supported:
            return "Ready"
        if self.warnings:
            return "Unsupported input"
        return ""
