from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AuroraPlanMetadata:
    source_path: str = ""
    plan_label: str = ""
    plan_name: str = ""
    manufacturer: str = ""
    manufacturer_model_name: str = ""
    treatment_machine_name: str = ""
    patient_id: str = ""
    study_instance_uid: str = ""
    series_instance_uid: str = ""
    sop_instance_uid: str = ""
    beam_count: int = 0
    notes: list[str] = field(default_factory=list)


@dataclass(slots=True)
class AuroraControlPoint:
    control_point_index: int = 0
    gantry_angle_deg: float = 0.0
    dose_rate_mu_per_min: float = 0.0
    cumulative_meterset_weight: float = 0.0
    isocenter_position_mm: tuple[float, float, float] = (0.0, 0.0, 0.0)
    axial_position_mm: float = 0.0
    jaw_x: tuple[float, float] = (0.0, 0.0)
    jaw_y: tuple[float, float] = (0.0, 0.0)
    mlc_x1_positions_mm: tuple[float, ...] = ()
    mlc_x2_positions_mm: tuple[float, ...] = ()
    private_wistech_4001_1004: dict[str, Any] = field(default_factory=dict)
    private_wistech_4001_1005: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AuroraBeam:
    beam_number: int = 0
    beam_name: str = ""
    treatment_machine_name: str = ""
    delivery_type: str = ""
    control_points: list[AuroraControlPoint] = field(default_factory=list)
    metrics: dict[str, float | None] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    trajectory_summary: dict[str, float | None] = field(default_factory=dict)


@dataclass(slots=True)
class AuroraMetricValue:
    metric_name: str = ""
    value: float | int | str | None = None
    unit: str = ""
    description: str = ""


@dataclass(slots=True)
class AuroraAnalysisResult:
    source_path: str = ""
    metadata: AuroraPlanMetadata = field(default_factory=AuroraPlanMetadata)
    beams: list[AuroraBeam] = field(default_factory=list)
    metrics: list[AuroraMetricValue] = field(default_factory=list)
    plan_metrics: dict[str, float | None] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    supported: bool = False
    reason: str = ""

    @property
    def status(self) -> str:
        return "READY" if self.supported else "UNSUPPORTED"
