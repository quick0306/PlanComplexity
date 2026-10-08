# Aurora 物理孔径指标：当前定义

所有 Aurora 家族（V2/V3/legacy/V4）的可编辑 LaTeX 公式见 [Aurora 全平台说明](aurora_guide.md)。

当前版本：`aurora-v4-physical-aperture-open-only`（2026-10-08）。本文替代原候选指标草案，导出键使用小写 snake_case。实现依据为 `aurora_svmat_lab/aperture_metrics.py`；逐项定义见[指标目录](metric_definitions_aurora.md)和[公式契约](metric_formula_contracts.md)，历史见[迁移记录](aurora_v4_migration.md)。

## 几何与采样

每层 `LeafPositionBoundaries` 有 N+1 个严格递增边界，位置数组有 2N 个数，前后分别为 A/B 两组叶片位置。MLCX1 和 MLCX2 是两层独立 MLC，不是同一层的左右边界。

在两层共同 Y 覆盖内，用边界位置的并集划分子条带。每条带求两层 X 开口交集，再按 X/Y jaws 裁剪。面积 `A=sum_s(h_s*g_s)`，单位 mm²。周长 P 是这些矩形并集的外露边界总长度，单位 mm，包含不连通区域边界，不重复计共享内边。

仅接受相邻控制点区间的正 `ΔCMW`，使用末端 i+1 几何。CMW 必须起始为零、有限、非递减、最终值为正。零 MU 射束不贡献样本。端点采样不是连续交付重建，闭合端点不等于整个区间全程闭合。

## 开放孔径条件权重

令 O 为正权重、面积大于零的端点集合。七项统一使用：

```text
w_i = delta_CMW_i / final_CMW_beam * BeamMeterset_beam
OpenMUmean(f) = sum_(i in O)(w_i*f_i) / sum_(i in O)(w_i)
```

完全闭合样本不进入分子和分母。排除后对所有保留样本统一归一化，不分别重新平衡射束。若任一射束缺少 MU，所有有贡献射束先按各自全部正区间归一化为单位相对总权重，再排除闭合样本，并提示回退。

“不计闭合叶片”表示 SAS、LSV 仅用正间隙条带；开放区域与闭合区域相邻形成的真实边界仍计入周长。

## 七项公式

| 导出键 | 开放端点的量与汇总 | 单位 |
| --- | --- | --- |
| `mean_ba` | `OpenMUmean(A_i)` | mm² |
| `mean_bi` | `OpenMUmean(P_i²/(4πA_i))` | 无量纲 |
| `mean_ca` | `OpenMUmean(P_i/A_i)`，不是 circularity | mm⁻¹ |
| `mean_sas5` | `OpenMUmean(count(0<g<5)/count(g>0))` | 无量纲 |
| `mean_sas10` | `OpenMUmean(count(0<g<10)/count(g>0))` | 无量纲 |
| `mean_mcs_aurora` | `OpenMUmean(AAV_i*LSV_i)` | 无量纲 |
| `mcs_complexity_aurora` | `1-mean_mcs_aurora` | 无量纲 |

SAS 阈值严格小于 5/10 mm，等于阈值不计入分子。开放物理子条带等计数，既非面积加权，也非原始单层叶对数。子条带由两层边界并集确定。

每个射束分别定义面积包络：

```text
U_beam = sum_s max_positive_weight_endpoints(h_i,s*g_i,s)
AAV_i = A_i/U_beam
```

闭合端点条带面积为零，不改变包络。包络包含实际 Y-jaw 裁剪，不能替换为整束最大总面积或银行极值包络。

取按 Y 排列、移除零间隙后的正间隙序列。n≤1 时 LSV=1；否则：

```text
LSV_i = 1 - sum_(j=1..n-1)|g_(j+1)-g_j| / ((n-1)*max(g))
```

代码将 LSV 限制在 [0,1]。这是 Aurora 间隙序列改编指标，不是原始 McNiven 银行序列 MCS。

## 缺失与排除

| 情况 | 当前结果 |
| --- | --- |
| 同时存在闭合正权重端点和开放端点 | 排除闭合端点，七项继续计算；警告记录排除数量及权重比例。 |
| 所有正权重端点闭合 | 七项均为 None；`AURORA_V4_NO_OPEN_APERTURE`。 |
| 无正交付权重 | 七项均为 None；`AURORA_V4_UNAVAILABLE`。 |
| 缺少/非法边界、jaws、叶片位置、CMW，或含歧义 MU | 七项均为 None 并提示；不静默丢弃非法射束。 |
| 缺少 BeamMeterset | 使用全射束相对权重回退；`AURORA_V4_RELATIVE_WEIGHTS`。 |

七项字段始终保留，不可用值在 CSV 为空。排除比例对应当前权重方案；相对回退时不能称为真实 MU 比例。

## 版本比较与其他指标

Aurora 共 77 项：V2 21、V3 40、legacy 9、V4 7。其余 70 项研究代理定义保持原样，原开口宽度代理不是真实面积。

旧单位行高算法、`aurora-v4-physical-aperture` 初版与当前 open-only 版本不能直接混合七项结果。叶片宽度、双层交集、周长、射束权重和闭合口径均影响结果，差异不是通用的十倍换算。研究批次应统一版本复算并保存输入哈希、公式版本和代码提交。

实际计划的验证见[迁移记录](aurora_v4_migration.md)。这些检查针对实现和数值，不建立临床阈值或厂商等价性。
