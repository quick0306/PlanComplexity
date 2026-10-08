# TOMO：输入、使用与 LaTeX 指标说明

对应 `tomo-v3`。GUI 选择 `AUTO` 或 `TOMO`，读取当前支持的螺旋 RTPLAN / sinogram 信息；固定角度计划不属于现版螺旋读取器支持范围。私有标签必须匹配正确 creator，不能只按标签号猜测；时间、场宽或运动字段缺失及回退必须查看警告。详细字段契约见 [TOMO 输入说明](tomo_input_contract.md)。

令 $S_{pj}\in[0,1]$ 为投影 p、叶片 j 的开放分数，P 为投影数，L 为列数，投影时间为 $t_p$（当前标量投影周期）。本页纵向跨度和连通长度使用叶片索引，不是 mm。没有 MU 加权。逐项边界见[定义表](metric_definitions_tomo.md)和[契约](metric_formula_contracts.md)。

## Delivery

$$
T_{pj}=1000\,t_pS_{pj}\quad(\mathrm{ms}),\quad
\mathrm{MF}=\frac{\operatorname{mean}_{T>0}T}{\max T},\quad
N_{\mathrm{rot}}=P/R,\quad \mathrm{GP}=t_pR,\quad\mathrm{TT}=t_pP.
$$

R 为每圈投影数，GP、TT 单位 s。**现版 MF 是开放时间均值/最大值，与常见最大值/均值定义互为倒数**，不能按其他系统 MF 直接比较。Nproj=P，Nprojrot=R，PT=$t_p$，FW 为名义场宽 mm。

$$
\mathrm{pitch}=\frac{\text{每圈床位移}}{\mathrm{FW}},\quad
\mathrm{CS}=\mathrm{CT}/\mathrm{TT},\quad
\mathrm{TL}=\mathrm{CT}-\mathrm{FW},\quad
\mathrm{TTDF}=\mathrm{TT}/D_{\mathrm{fraction,cGy}}.
$$

CT 优先取已知计划速度乘时间或完整床轨迹；CS 优先取显式计划速度。只有有限非负的 CT−FW 才给出 TL。未知床运动不补零。20 ms 时间/10 mm 场宽等回退只能按读取器的相应条件使用，并在来源中标注；不应作为每个计划的真实参数。

## Leaf times

开放时间统计只使用 $\mathcal T=\{T_{pj}:T_{pj}>0\}$，开放分数统计使用 $\mathcal S=\{S_{pj}:S_{pj}>0\}$。m/sd/median/mode/max/min 分别为算术均值、样本标准差（ddof=1）、中位数、众数、最大最小值；LOT 为 ms，FLOT 为无量纲。众数按六位小数分组，并列取首先出现者。偏度、峰度使用 SciPy 非偏估计，峰度为 Fisher excess。空集合的这些统计沿用零回退。

$$
\mathrm{CLNS}_{\tau}=\frac{\#\{0<T<\tau\}}{\#\{T>0\}},\quad
\mathrm{CLNSpt}_{\tau}=\frac{\#\{T>1000t_p-\tau\}}{\#\{T>0\}},\quad
\mathrm{CFNS}_{q}=\frac{\#\{0<S<q\}}{\#\{S>0\}}.
$$

$\tau=10,20,30,50$ ms，$q=0.1,0.25,0.5,0.75$。严格不等号不含阈值。LOTV 虽归于开放时间家族，其完整公式见下方 Modulation；它不是上述正值集合的离散系数。

## Sinogram geometry

令 $B_{pj}=\mathbf1_{S_{pj}>0}$，每行开放数 $n_p=\sum_jB_{pj}$，非空行跨度 $a_p=j_{\max}-j_{\min}+1$，连通开放段数为 $c_p$；空行三者均为零。

$$
\mathrm{TA}=\frac1P\sum_pa_p,\quad\mathrm{NCC}=\frac1P\sum_pc_p,\quad
f_{\mathrm{disc}}=\frac{\#\{p:c_p>1\}}P,\quad
\mathrm{CLS}=\frac1P\sum_p\frac{L-n_p}{L}.
$$

lengthCC 是所有开放连通段长度的混池均值。TA、NCC、CLS 包含空行；以下均值只含非空行：

$$
\mathrm{CLSin}=\operatorname{mean}_{n_p>0}\frac{a_p-n_p}{L},\quad
\mathrm{CLSinarea}=\operatorname{mean}_{n_p>0}\frac{a_p-n_p}{a_p},\quad
\mathrm{centroid}=\operatorname{mean}_{n_p>0}\frac{\sum_{j:B_{pj}=1}(j-(L-1)/2)}{n_p}.
$$

disc 变体额外要求 $c_p>1$。L0NS/L1NS/L2NS 为每非空行中有 0/1/2 个开放相邻叶片的开放叶比例，再对行均值；数组外视为闭合。centroid 不是开放分数加权中心，也不是物理坐标。

## Modulation

设 $m_j=\max_pS_{pj}$，各列等权：

$$
\mathrm{LOTV}=\frac1L\sum_j\frac{\sum_{p=0}^{P-2}(m_j-|S_{p+1,j}-S_{pj}|)}{(P-1)m_j},
$$
$$
\mathrm{ELOTV}_{\delta}=\frac1L\sum_j\frac{\sum_{p=0}^{P-\delta-1}|S_{p+\delta,j}-S_{pj}|}{(P-\delta)m_j},\quad\delta\in\{1,5\}.
$$

全闭合列 LOTV=1，ELOTV=0。P≤δ 时 ELOTV=0；单投影非零列的 LOTV 分母退化，现版可能 NaN，不以正常数值解释。

对偏移 $(d_p,d_l)$ 的有效起点域 $\mathcal D$：

$$
\mathrm{EPSTV}_{d_p,d_l}=\frac1{|\mathcal D|}\sum_{(p,j)\in\mathcal D}
\left(|S_{p+d_p,j}-S_{pj}|+|S_{p,j+d_l}-S_{pj}|\right).
$$

偏移为零的项省略，域按两个偏移共同裁剪；输出 (1,1)、(1,0)、(0,1)，PSTV 对应 (1,1)。

MI 的四个差分集合为投影、叶片及两个对角方向的绝对差；σ 为正 S 的样本标准差。每方向使用全部有效差分，空方向的比例取零：

$$
z(f)=\frac14\sum_{k=1}^{4}\frac{\#\{D_k>f\sigma\}}{|D_k|},\quad
\mathrm{MI}=\operatorname{Trapz}_{f=0,0.01,\ldots,2}z(f).
$$

这是 201 点梯形积分，不是解析积分。NOC 将每个正值转为投影坐标上的开放区间 $[p+0.5-S_{pj}/2,p+0.5+S_{pj}/2]$，合并相接区间；若第 j 列合并后为 $K_j$ 段：

$$
\mathrm{NOC}=\frac1L\sum_j\frac{2K_j}{P}.
$$

令 $I_j=P^{-1}\sum_pS_{pj}$：

$$
\mathrm{MSA}=\frac{\sum_j(j-(L-1)/2)I_j}{\sum_jI_j},\quad
\mathrm{MSI}=\operatorname{mean}_jI_j,\quad
\mathrm{MDSI}=\operatorname{median}_jI_j,\quad
\mathrm{SDSI}=\operatorname{SD}_{\mathrm{sample},j}I_j.
$$

这些列统计包含全闭合列；零总强度、单样本等退化规则以逐项契约为准。不能把“只保留正 LOT”推广为所有 TOMO 指标均删除闭合行列。
