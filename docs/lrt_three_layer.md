# LRT 三层复杂度定义（lrt-three-layer-v1）

本次修改保留所有旧字段与原公式，新增带 `_Eff`、`_D`、`_P` 后缀的严格研究接口。
三层接口与通用分析、GUI、CSV、指标目录及公式契约共同维护；旧字段继续使用原有入口。

## Geometry

只接受已建立证据的 Halcyon/Ethos 28/29 对、10 mm 叶宽、5 mm 错位结构。
D=MLCX1、P=MLCX2；Eff 为交集。交集左右边为两层左右边的 max/min，负交集闭合。
固定 jaw 参与面积和周长裁剪；P 最外侧两个 10 mm 叶条带各裁剪为 5 mm。
近端和远端实体条带数不同；Eff 的 56 个 5 mm 条带是虚拟几何条带。

CMW 必须有限、从 0 起、非递减、末值正。ControlPointIndex 若提供，必须完整并依次为 0..N−1；不自动重排。
首个 CP 不能缺层位置，后续省略的位置按 DICOM 继承。无效输入输出 None 和原因，不改用均匀权重。
新接口不使用旧程序可变 MU 缓存。零 MU 射野排除；负/缺失/非有限 MU 使计划新字段整体不可用。

设间隔权重 $d_i=u_{i+1}-u_i$，CP 中心权重：

$$
c_0=d_0/2,\qquad c_i=(d_{i-1}+d_i)/2,\qquad c_{N-1}=d_{N-2}/2.
$$

$\langle x\rangle_c=\sum_i c_i x_i/\sum_i c_i$。每个射野按此计算，计划再按射野 MU 平均。
三层调用同一套 13 项核函数。各指标保留其物理掩膜：面积/PI/PM 使用 jaw 裁剪；ALG/SLG/MAD/SAS/NL 使用正 raw gap 与 Y jaw 重叠，X jaw 不裁剪叶隙。
SAS 阈值严格小于 5/10/20 mm，空 CP 不进入 gap/SAS/MAD 均值；NL、PA、PI 的空 CP 为 0。
MCSv 使用相邻 AAV 均值乘相邻 LSV 均值，再按间隔 MU 平均。AAV 分母是每条带的 bank 极值包络，不能称为实际多边形并集。
LSV 两个 bank 相乘，活动叶条带压缩后计算相邻差；常量 bank 为 1。LT 为间隔 MU 平均位移和；LTmean 为总轨迹位移除以运动叶片数。
Eff 运动量描述有效边界，不代表实体叶片运动。NL 是活动叶片对数，Eff 为虚拟叶条带数。

PI 与 PM 的原计算已在 `pi5`、`pm5` 中存在，本次公开为规范字段：

$$
PI=\left\langle\frac{P_i^2}{4\pi A_i}\right\rangle_c,\qquad
PM=1-\frac{\langle A_i\rangle_c}{U},\quad U=\sum_j\max_i A_{ij}.
$$

零面积 PI 为 0；U=0 时 PM 为 0。PM 是逐条带最大面积归一化的面积调制量，不是相邻 CP 运动量，U 也不是真实几何并集。
因此恒宽平移可以有 PM=0 且 LT>0。原代码 `_union_area` 名称存在误导；本次保留函数与结果，只在契约中写明实际计算。

PR 从原 `ethos-report-v2` 有限半影条带公式推广。令 $t=2.8$ mm、$s=2.3$ mm，开放间隙 $g>0.5+10^{-8}$ mm。
每条带高 $h_j$，开放区间 $O_j=[l_j,r_j]$，叶尖内核 $K_j=[l_j+t,r_j-t]$（负宽为空）。内核面积为：

$$
C_i=\sum_j(h_j-2s)|K_j|+s\sum_j\left(|K_j\cap O_{j-1}|+|K_j\cap O_{j+1}|\right),\quad
PR=\left\langle1-\frac{C_i}{A_{\mathrm{open},i}}\right\rangle_c.
$$

只计实际接触的上下邻条带。空 CP 的 PR=0；全束低于开放阈值时 PR=None。
高度小于 4.6 mm 的部分条带不在这个解析公式支持域内，PR=None 并报告原因。
Eff 使用 5 mm 条带；D/P 使用实际 10 mm 和 jaw 裁剪后的 5 mm 边缘条带。
这不是“周长×厚度”或形态学腐蚀，也不把 D/P 的 PR 当作实测半影宽度。
D/P 沿用同一名义 t/s 参数，以可比较的几何边界负担定义使用；厂家没有分别输出这两个指标。

## Delivery

`MU` 为总 MU；`MU_per_CP` 为总 MU/治疗控制点总数，包含首末端点。
旧 `mucp` 实际为 $100\,\mathrm{mean}(\Delta MU)/MU_{beam}$，单位 %；保持可读和数值不变，不自动映射到 MU_per_CP。
新接口把它从新的递送候选中替换为有明确绝对单位的 MU_per_CP，旧模型仍读取旧 `mucp`。

## Reference

`PR_System` 是旧 `ethos_penumbra_ratio` 的明确兼容引用；该旧字段实际是由 DICOM 重建的系统报告口径值，不能写成从报告读取的实值。
`PR_Ethos_observed_pct` 才是本次从 PDF 原文独立读取的报告实值，单独保存在配对核验表。
本次没有把旧模型中的 PR 替换为新指标。`PR_Eff` 在报告支持域内与旧重建应仅有浮点求和差。

三层各 16 项 = 原有 13 项 + PI + PM + PR。加递送 2 项、系统参考 1 项，共 **51 个输出字段**。
默认候选池是 **50 项（16×3+2）**：PR_System 单独保留为参考，避免把与 PR_Eff 同定义的值重复入模。
`select_candidates(..., include_system_reference=True)` 显式返回 51 项，供需要旧 PR 参照的分析使用。
旧 48 项候选及历史冻结模型保留原入口；`ethos_sas10` 与 `ethos_one_minus_mcs` 不进入新候选池。

## Compatibility

旧字段逐字保持原算法，新字段共同采用同一核函数和严格输入规则；这不是所有新字段均为旧字段数值别名的承诺。
原生层 LSV/AAV/MCSv、LT 和多射野 SLG 等在旧实现中有不同汇总路径；本次用逐字段映射差异表明确量化。
不得将新字段悄悄覆盖旧列后重新运行论文模型。

运行：

```powershell
python -m pytest tests/test_lrt_three_layer.py -q
# Copy docs/lrt_manifest.example.json to reports/local_manifest.json,
# then replace its path, beam number and SHA-256 with local inputs.
python tools/lrt_export.py --manifest reports/local_manifest.json --output reports/recomputed
python tools/lrt_compare.py reports/baseline_core.json reports/modified_core.json --output reports/regression.json
python tools/validate_lrt_pr.py ORIGINAL_BATCH_RESULTS_JSON --output reports/pr_validation_new
```

PR 一致性程序检查当前 RP/PDF SHA-256、逐野唯一 MU 和总 MU，独立提取 PDF 复杂度页，输出三列 PR、Pearson/Spearman、偏差、SD、MAE、RMSE、相对误差和 Bland–Altman 图。
PDF/RP 标签不一致的既有问题继续在来源表记录；该核验不是对厂商所有版本的普遍等价证明。

输入清单的每条记录指定 `case`、`beam`、RTPLAN 文件的绝对 `path` 和 `sha256`，见 [清单示例](lrt_manifest.example.json)。`baseline_core.json` 应在修改前由 `lrt_snapshot.py` 冻结；`modified_core.json` 为修改后在同一清单上的快照。比较工具逐项核对旧字段及输入哈希，不把新字段代入旧模型。

原始 RTPLAN、PDF、含病例信息的清单、逐野矩阵及队列报告留在本地，`reports/` 默认忽略。仓库维护合成几何测试和复算工具。

逐指标公式、名称、单位及边界条件见 [完整指标目录](metric_definitions_all.md)、[公式契约](metric_formula_contracts.md) 和 [逐键公式索引](metric_math_index.md)。
