# Aurora SVMAT：全指标使用与 LaTeX 公式

GUI 使用 `AUTO` 或 `AURORA`。DeepPlan/慧软导出的 Aurora 计划须具备正确的双层控制点、叶片边界、jaws、累积 meterset 及轴向信息；兼容字段与错误处理见 [DeepPlan 兼容说明](deepplan_aurora_compatibility.md)。当前共 77 项：V2 21、V3 40、legacy 9、V4 7。V4 版本为 `aurora-v4-physical-aperture-open-only`；旧 70 项仍是各自的研究/代理定义。

以下不能套用到 Halcyon 或普通 VMAT。每个输出键的统计类型、单位、来源见[逐项定义](metric_definitions_aurora.md)及[公式契约](metric_formula_contracts.md)。

## Motion

只在射束内部形成相邻控制点区间，不跨射束连接。令 $\Delta z_i=|z_{i+1}-z_i|$，$\Delta\theta_i$ 为最短展开后的绝对角差，$\Delta C_i$ 为累积权重差。旧定义的开口宽度代理为：

$$
W_i=\sum_j\max(x^{(2)}_{ij}-x^{(1)}_{ij},0),\quad
D_i=\sum_j\left(|\Delta x^{(1)}_{ij}|+|\Delta x^{(2)}_{ij}|\right).
$$

两通道按可配对元素计算，未使用真实叶宽或 jaw 裁剪；W 不是面积，不能按 V4 双层交集解释。

$$
p_i=\Delta z_i/\Delta\theta_i,\quad
\rho_i=|\Delta C_i|/\Delta z_i,\quad
a_i=|W_{i+1}-W_i|/\Delta z_i,\quad
v_i=D_i/\Delta z_i.
$$

pitch 仅保留正角差，后三者仅保留正轴向位移。各区间样本等权，按键输出普通均值、总体 CV、最大、最近秩 P95 或最大 min(3,N) 项均值：

$$
\mathrm{CV}(x)=\sigma_{\mathrm{population}}(x)/|\overline x|,\quad
P_{95}=x_{(\lceil0.95N\rceil)}.
$$

一个样本或全零 CV 为零，无有效样本/不可定义比值为 None。轴向总行程、角度总行程先求区间绝对距离和，再形成计划比值：

$$
Z=\sum_i\Delta z_i,\quad\Theta=\sum_i\Delta\theta_i,\quad
N_{\mathrm{rot}}=\Theta/360,\quad
\mathrm{mm/deg}=Z/\Theta,\quad\mathrm{mm/rotation}=360Z/\Theta.
$$

MU/mm 使用显式射束 MU；缺 MU 时回退为累积权重跨度，必须标为代理，不能作为绝对 MU/mm 比较。开口变化/mm 和叶片行程/mm 使用正 Δz 区间的变化总和除以其距离总和，不是区间比值算术均值。legacy 同义键保留兼容，不能按新增独立指标计数。

## Research

正向/反向按每束净 z 位移符号分组，绝对净位移≤$10^{-9}$ 的束排除。对 MU 密度代理、开口变化、叶片行程、pitch 四个家族，先分别求方向内射束等权均值 $f_k,b_k$：

$$
\mathrm{Symmetry}=\operatorname{mean}_{k\,\mathrm{available}}\left(1-\frac{|f_k-b_k|}{|f_k|+|b_k|}\right).
$$

双方为零时该家族取 1；缺任一方向为 None。forward/backward difference 比较两方向的平均耦合指标，beam pair balance 比较耦合指标之和，详见逐键定义。

$$
\mathrm{Difference}=|\overline C_f-\overline C_b|,\quad
\mathrm{Balance}=1-\frac{|\sum C_f-\sum C_b|}{\sum C_f+\sum C_b}.
$$

C 为下述耦合指标，零总耦合负荷的 Balance 为 None。

small-opening 指标使用每区间下一端点的正代理间隙 g，样本权重 $w=|\Delta C|$，零增量回退为 1：

$$
F_{\tau}=\frac{\sum w\mathbf1_{0<g<\tau}}{\sum_{g>0}w},\quad
B_{10}=\frac{\sum_{g>0}w\max(0,1-g/(10\,\mathrm{mm}))}{\sum_{g>0}w}.
$$

small opening 阈值 10 mm，near closed 为 2 mm；无正样本取零。它们不同于 V4 SAS：代理配对、权重和几何均不同。

区域指标把区间 z 中点按全计划中点跨度分三段：归一化位置 <1/3 为 head、<2/3 为 mid，其余 tail；零跨度归 mid，未覆盖区域为空，不能补零。区域内用相同区间统计。局部峰值用上述最大/P95/top3 规则。

$$
\mathrm{Coupled}=\operatorname{mean}_{x\,\mathrm{available}}\frac{x}{1+x},\quad
x\in\{\text{aperture change/mm},\text{leaf travel/mm},\mathrm{CV}(\rho),\mathrm{CV}(p)\}.
$$

层协调指标沿用原始通道序列：

$$
\mathrm{Imbalance}=\frac{|\overline x_1-\overline x_2|}{|\overline x_1|+|\overline x_2|},\quad
\mathrm{TravelRatio}=\overline x_1/\overline x_2,\quad
\mathrm{Correlation}=\frac{\operatorname{cov}_{\mathrm{population}}(x_1,x_2)}{\sigma_1\sigma_2}.
$$

常量或单样本相关性在逐对相等（绝对容差 $10^{-12}$）时取 1，否则 0。aperture disparity 对每个控制点两通道绝对位置和比较，跳过两者总和为零的项；不是两层面积差。

## Aperture

真实 A/B bank、两层 `LeafPositionBoundaries` 的共同 Y 覆盖及边界分割形成子条带。每条带取双层横向交集，再裁剪 X/Y jaws：

$$
g_{ij}=\left[\min(R^{(1)}_{ij},R^{(2)}_{ij},X_{2i})-\max(L^{(1)}_{ij},L^{(2)}_{ij},X_{1i})\right]_+,\quad
A_i=\sum_jh_{ij}g_{ij}.
$$

P 是这些矩形并集的真实外边界长度，不是逐矩形周长之和。只采正 ΔCMW 区间的末端 i+1。初始 CMW 必须为零，序列有限非递减，末值正；零 MU 束排除。全部七项的同一开放条件均值为：

$$
w_{b,i}=\frac{\Delta C_{b,i}}{C_{b,\mathrm{final}}}M_b,\quad
\mathbb E_{\mathrm{open}}[f]=\frac{\sum_{b,i:A_{b,i+1}>0}w_{b,i}f_{b,i+1}}{\sum_{b,i:A_{b,i+1}>0}w_{b,i}}.
$$

若有射束 MU 缺失，全部射束改为先在各束所有正区间上归一化，再排除闭合样本，避免混用 MU 与相对权重。删除闭合样本后不重新平衡每束权重。

$$
\mathrm{BA}=\mathbb E_{\mathrm{open}}[A],\quad
\mathrm{BI}=\mathbb E_{\mathrm{open}}[P^2/(4\pi A)],\quad
\mathrm{CA}=\mathbb E_{\mathrm{open}}[P/A],
$$
$$
\mathrm{SAS}_{\tau}=\mathbb E_{\mathrm{open}}\left[\frac{\#\{j:0<g_j<\tau\}}{\#\{j:g_j>0\}}\right],\quad\tau\in\{5,10\}\,\mathrm{mm}.
$$

BA 为 mm²，BI 无量纲，CA 为 mm⁻¹（不是圆度）。SAS 对正间隙条带等计数，不按条带宽度或面积加权。Aurora 改编 MCS 用正间隙压缩序列，与通用 bank LSV 不同：

$$
U_b=\sum_j\max_{i:\Delta C_i>0}(h_{i+1,j}g_{i+1,j}),\quad
\mathrm{AAV}_i=A_i/U_b,\quad
\mathrm{LSV}_i=1-\frac{\sum_{j=1}^{n-1}|g_{j+1}-g_j|}{(n-1)\max_jg_j},
$$
$$
\mathrm{mean\_mcs\_aurora}=\mathbb E_{\mathrm{open}}[\mathrm{AAV}\,\mathrm{LSV}],\quad
\mathrm{mcs\_complexity\_aurora}=1-\mathrm{mean\_mcs\_aurora}.
$$

正间隙数 n≤1 时 LSV=1；闭合叶片不参与 SAS/LSV。全部闭合、缺失或无效几何/权重时七项为空并警告，不能填零；部分闭合只排除对应样本，并报告数量和权重占比。实例、几何重建和历史差异见[完整七项说明](aurora_aperture_metrics.md)及[迁移说明](aurora_v4_migration.md)。
