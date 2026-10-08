# PlanComplexity 使用说明

适用于 2026-10-08 当前实现。程序名为 PyUCoMX，支持 VMAT/IMRT、TOMO、CyberKnife MLC、Aurora SVMAT。完整定义见[指标目录](metric_definitions_all.md)和[公式契约](metric_formula_contracts.md)。

## 启动与分析

Windows 用户运行 `dist/PyUCoMX.exe`。源码用户安装 `requirements.txt` 中的依赖，再运行 `python ucomx.py`。

1. `Input Type` 选择 `Single RT Plan`（单文件）或 `Folder Batch`（文件夹）。
2. 使用 `Browse` 选择 RTPLAN 或目录；子目录需要勾选 `Recursive folder scan`。
3. `Mode` 通常选 `AUTO`。也可显式选择 `VMAT_IMRT`、`TOMO`、`CYBERKNIFE_MLC`、`AURORA`；手动模式不补足缺失的输入信息。
4. 点击 `Run Analysis`。在 `Plans` 选择计划，查看 `Metadata`、`Metrics`、`Metric Notes` 和 `Warnings / Notes`。
5. 点击 `Export Current Results` 导出当前结果集合，并非仅导出所选行。

`READY` 表示当前路径支持该计划，不保证每个指标都有数值。`UNSUPPORTED` 表示当前路径不能完成分析。空值表示不可用，不代表零，也不一定是字段遗漏；先查看警告。

## 模式与公式版本

| 模式 | 当前公式版本 | 边界 |
| --- | --- | --- |
| VMAT/IMRT | `geometry-v4` | 原生层、有效交集、stacked 及 Halcyon/Ethos 专属定义分别解读。 |
| TOMO | `tomo-v3` | 螺旋投影及叶片开放分数；当前螺旋读取器不支持固定角度。 |
| CyberKnife MLC | `geometry-v4` | 六项 MLC 指标；XML 分段路径和标准 MLC 回退定义不同。 |
| Aurora SVMAT | `aurora-v4-physical-aperture-open-only` | 77 项：V2 21、V3 40、legacy 9、物理孔径 V4 7。 |

Aurora 的版本字段标识七项 V4 定义；其余 70 项保留研究/代理定义，不能因此统称为物理孔径指标。

## Aurora 七项的当前口径

用真实叶片边界分别重建每层 A/B 叶片的开放区域，求双层交集并裁剪 X/Y jaws。采样为正 meterset 增量区间的末端控制点。

七项统一只保留面积 `A > 0` 的样本，计算 `sum_open(w*f)/sum_open(w)`。完全闭合样本从分子和分母排除，SAS、LSV 不计闭合叶片。

| 导出键 | 含义 | 单位 |
| --- | --- | --- |
| `mean_ba` | 条件平均面积 | mm² |
| `mean_bi` | 条件平均 `P²/(4πA)` | 无量纲 |
| `mean_ca` | 条件平均 `P/A`，不是圆度 | mm⁻¹ |
| `mean_sas5` / `mean_sas10` | 正间隙子条带中，严格小于 5/10 mm 的比例的条件平均 | 无量纲 |
| `mean_mcs_aurora` | 条件平均 `AAV × LSV`，Aurora 改编定义 | 无量纲 |
| `mcs_complexity_aurora` | `1 - mean_mcs_aurora` | 无量纲 |

权重为 `ΔCMW/final_CMW × BeamMeterset`。排除闭合样本后统一归一化，不重新将各射束变成等权。完整算法见[孔径指标说明](aurora_aperture_metrics.md)。

## 导出与版本比较

主程序导出 `results.csv` 时，同时生成 `results_columns.csv`，记录指标键、显示名和说明。主结果还含来源、模式、状态、版本、警告等；混合模式允许不适用的空列。总列数不是指标数。

独立 Aurora CLI 可分别导出计划、射束、轨迹 CSV，不生成主程序的列字典。计划和射束表有公式版本；计划表仅提供 warning_count，不包含主导出中的完整警告文本，应在 GUI/服务结果查看详情。轨迹表是控制点记录，不是 77 项指标表。

比较时按指标键对齐，核实输入身份，不仅凭计划名或文件名判断同一 DICOM。保留输入哈希、代码提交、公式版本和精度信息。旧代理几何、初版物理孔径、当前开放条件均值的七项不能直接混用，应统一版本复算。

VMAT/IMRT 和 CyberKnife 默认 API 保留历史舍入；验证调用 `analyze_plan_file(..., full_precision=True)`。TOMO、Aurora 路径返回浮点数；TOMO 众数保留其明确分箱规则。CSV 导出不会恢复之前舍入丢失的精度。

## Aurora 警告

| 警告标识 | 含义 |
| --- | --- |
| `AURORA_V4_CLOSED_SAMPLES_EXCLUDED` | 已排除闭合端点；记录数量和权重比例，通常仍有结果。 |
| `AURORA_V4_NO_OPEN_APERTURE` | 没有正权重开放端点，七项均不可用。 |
| `AURORA_V4_RELATIVE_WEIGHTS` | MU 缺失；所有贡献射束先按全部正区间归一化为单位相对总权重，再排除闭合样本。 |
| `AURORA_V4_UNAVAILABLE` | 缺少/非法几何、权重等；查看原因。七项不可用不等于其余 70 项也不可用。 |

闭合端点不证明整个区间全程闭合。当前指标是端点采样描述，未插值重建连续交付。相对权重回退时，排除比例不是实际 MU 比例。

## 命令行与复现

通用单文件分析只输出控制台信息，不提供 CSV 参数：

```bash
python main.py --input-file path/to/plan.dcm --verbose
```

独立 Aurora 计划、射束、轨迹导出：

```bash
python aurora_svmat_cli.py --input-file path/to/plan.dcm --output-csv aurora_plan.csv --beam-output-csv aurora_beams.csv --trajectory-output-csv aurora_trajectory.csv --verbose
```

Aurora 目录分析使用 `--input-dir path/to/plans`，该入口递归查找 `*.dcm`，没有 `--recursive` 参数。其他批处理入口见[根 README](../README.md)。

```bash
python -m pytest tests -q
python tools/export_metric_definitions.py
python -m metric_formula_contracts
python tools/export_aurora_formula_pdf.py
python tools/export_app_summary_pdf.py
```

Windows 安装 PyInstaller 后运行 `tools/build_windows_exe.ps1`，输出 `dist/PyUCoMX.exe`。确认构建成功退出，再检查窗口启动。源代码更新不会自动更新旧 exe。

本项目按研究用途发布。技术回归通过不等于临床验证；详见[部署回退](deployment_rollback.md)和[参考包](reference_pack_v1.md)。
