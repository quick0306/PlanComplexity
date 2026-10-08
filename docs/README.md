# 项目文档索引

以当前代码为准，核对日期 2026-10-08。入口从[中文使用说明](user_guide.md)开始。当前模式版本是 VMAT/IMRT、CyberKnife 的 `geometry-v4`，TOMO 的 `tomo-v3`，Aurora V4 的 `aurora-v4-physical-aperture-open-only`。

## 当前使用与定义

| 内容 | 文档 |
| --- | --- |
| 安装、GUI、CLI、CSV、空值及版本比较 | [使用说明](user_guide.md)、[项目 README](../README.md) |
| 全指标、分平台定义 | [全部](metric_definitions_all.md)、[VMAT/IMRT](metric_definitions_vmat_imrt.md)、[TOMO](metric_definitions_tomo.md)、[CyberKnife](metric_definitions_cyberknife_mlc.md)、[Aurora](metric_definitions_aurora.md) |
| 公式、单位、采样、掩码、归一化、缺失规则 | [逐项公式契约](metric_formula_contracts.md) |
| Aurora 七项物理几何及开放条件均值 | [当前定义](aurora_aperture_metrics.md)、[版本迁移](aurora_v4_migration.md)、[DeepPlan 兼容](deepplan_aurora_compatibility.md) |
| TOMO 与 Ethos 专属输入/算法边界 | [TOMO](tomo_input_contract.md)、[Ethos](ethos_report_profile.md) |
| 精度与基线、发布及回退 | [精度说明](precision_motion_validation.md)、[参考包](reference_pack_v1.md)、[部署回退](deployment_rollback.md)、[临床前提](clinical_implementation_sop.md) |
| 可下载 PDF | [项目简介](../output/pdf/plancomplexity_app_summary.pdf)、[Aurora 公式](../output/pdf/aurora_metric_formulas.pdf) |

定义 Markdown 和本地 CSV 来自 `metric_definition_catalog.py`；公式契约来自 `metric_formula_contracts.py`；Aurora PDF 复用目录与注释；项目简介 PDF 从当前版本常量和目录生成。修改定义源后必须重新生成，避免手工修改导出文档后被覆盖。命令见[使用说明](user_guide.md)。

## 历史、研究与计划

[hybrid-v2](hybrid_v2_metrics.md)、[geometry-v3](geometry_v3_metrics.md)和[精度迁移](precision_motion_validation.md)保留原迁移与验证日期。历史测试数量不代表当前测试数量。[Aurora 旧比较表](aurora_rtplans_comparison.md)保留未锁定当前公式的旧数据，不应作为当前物理面积或 V4 基线。

[研究目录](research/README.md)保留研究问题、证据和迁移来源；`superpowers/plans/`、`superpowers/specs/` 保留历史实施计划/设计。提出过的功能不等于已经实现，历史命令不作为当前操作指引。原始 `reference_text/` 文献及 UCoMX 原版手册属于外部资料，不是本程序现版手册。

[指标完整性审计](metric_surface_audit_20261008.md)记录恢复阶段发现的问题；[本次文档同步记录](documentation_sync_20261008.md)列出完整审阅清单、未改写的证据和验证方法。历史基线、哈希和 `run_reports/validation/` 快照不因文档更新而重写。
