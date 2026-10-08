# CyberKnife MLC：输入、使用与 LaTeX 指标说明

GUI 选择 `AUTO` 或 `CYBERKNIFE_MLC`。当前支持六项 MLC 指标，不覆盖 cone/Iris 准直器。Precision RTPLAN 若没有标准 MLC 几何，需要配套且可匹配的 XML 分段信息；缺辅助信息为不支持，不能导出六个零来表示。具体异常在 Warnings / Notes 中查看。

存在两条算法路径：XML 分段与标准 DICOM MLC 回退。导出比较必须保留输入来源、模式及完整指标键，仅看 `geometry-v4` 版本不足以证明两条路径数值可互换。见[逐项定义](metric_definitions_cyberknife_mlc.md)与[公式契约](metric_formula_contracts.md)。

## Metrics

XML 路径使用匹配到 `interval_key` 的分段。令分段 MU 为 $m_s$，计划归一化 MU 为 $M=\sum_s m_s$，$q_s=m_s/M$；A 为 jaw 裁剪后面积，P 为矩形并集周长，H 为水平暴露叶侧边界。$E_{k(s)}$ 是对应区间的 bank 包络归一化面积，不是几何并集：

$$
E_k=\sum_j(\max_{s\in k}R_{sj}-\min_{s\in k}L_{sj})_+\max_{s\in k}h_{sj}.
$$

bank LSV 使用范围归一化，见 [通用 MCS](vmat_imrt_guide.md#modulation)。分段直接贡献：

$$
\mathrm{MCS}=\sum_sq_s\frac{A_s}{E_{k(s)}}\mathrm{LSV}_s,\quad
\mathrm{EM}=\sum_sq_s\frac{H_s}{A_s},\quad
\mathrm{PI}=\sum_sq_s\frac{P_s^2}{4\pi A_s},
$$
$$
\mathrm{LG}=\sum_sq_s\operatorname{mean}_{j:g_{sj}>0}g_{sj},\quad
\mathrm{PM}=\sum_b\frac{M_b}{M}\left(1-\sum_{s\in b}\frac{m_sA_s}{M_bE_{k(s)}}\right).
$$

零面积比值取零，空开放集合 LG 取零；PM 只贡献射束 MU 和 E 都为正的射束。有效分段总 MU 非正时，现有计算函数六项返回零，这是旧退化回退，与缺 XML 导致不支持不同。LG 的间隙是裁剪后正间隙，各叶片对等权；与原始 bank 间隙均值不同。XML 的 SAS10 为全分段正间隙计数混池：

$$
\mathrm{SAS10}=\frac{\sum_s\#\{j:0<g_{sj}<10\,\mathrm{mm}\}}{\sum_s\#\{j:g_{sj}>0\}}.
$$

它不按 MU 或分段等权平均每段比例。没有正间隙时按实现零回退。

标准 MLC 回退采用 [IMRT/VMAT](vmat_imrt_guide.md) 的控制点/区间体系：MCS 先取相邻端点 AAV 与 LSV 各自均值再相乘，PM 使用各条带最大裁剪面积之和 U，EM/PI 使用中心控制点 MU 均值；LG、SAS 使用 Y jaw 内原始正间隙。XML 的 $\sum q_s(A_s/E)\mathrm{LSV}_s$ 不能替换该端点均值公式。

EM 单位 mm⁻¹，LG 为 mm，其余为无量纲。不能将未匹配的 XML、缺失 bank/jaw 或非 MLC 计划强行套入上述公式；空值与不支持的区别见[使用说明](user_guide.md)。
