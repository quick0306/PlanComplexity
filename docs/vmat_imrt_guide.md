# IMRT / VMAT：使用与 LaTeX 指标说明

对应当前 `geometry-v4`。使用 GUI 的 `AUTO` 或 `VMAT_IMRT`，输入包含完整 MLC、控制点、jaws 和累积 meterset 的 RTPLAN。DeepPlan 等 TPS 名称本身不决定兼容性；以实际几何和权重是否完整为准。静态 IMRT 可计算孔径类指标，但无旋转时每度指标及运动指标可能为零或不可用。旧 `metrics_mit.py` 脚本按旋转标志筛选，可能跳过静态 IMRT；通用分析请使用 GUI/服务入口。

本页给出共享公式；每个键的单位、掩码、回退和源函数见[逐项定义](metric_definitions_vmat_imrt.md)及[公式契约](metric_formula_contracts.md)。双层方案另见 [Halcyon/Ethos](halcyon_ethos_guide.md)。以下长度为 mm，面积为 mm²，角度为度。

## Plan

令射束 MU 为 $M_b$，累积权重为 $C_i$，控制点累积 MU 为 $u_i=M_bC_i/C_{\mathrm{final}}$，区间 MU 为 $d_i=u_{i+1}-u_i$。控制点中心权重为：

$$
c_0=\frac{d_0}{2},\quad c_n=\frac{d_{n-1}}{2},\quad
c_i=\frac{d_{i-1}+d_i}{2}\quad(0<i<n).
$$

记 $\langle f\rangle_c=\sum_i c_if_i/\sum_i c_i$、$\langle f\rangle_d=\sum_i d_if_i/\sum_i d_i$。常规计划聚合为 $\langle f_b\rangle_M=\sum_bM_bf_b/\sum_bM_b$，但运动分箱等有独立规则，不能全部套用 MU 均值。

$$
\mathrm{MU}_{\mathrm{total}}=\sum_bM_b,\quad
\mathrm{PMU}=\frac{2\,\mathrm{Gy}}{D_{\mathrm{fraction,Gy}}}\mathrm{MU}_{\mathrm{total}},\quad
\mathrm{MUcGy}=\frac{\mathrm{MU}_{\mathrm{total}}}{D_{\mathrm{fraction,cGy}}},\quad
\mathrm{MUCA}=\frac{\mathrm{MU}_{\mathrm{total}}}{N_{\mathrm{control\ arcs}}}.
$$

分次剂量取处方总剂量除以分次数；无正分次数时沿用处方剂量。`narcs` 为治疗射束数。取最短跨零角差 $\delta\theta_i$：

$$
G=\sum_{b,i}|\delta\theta_{b,i}|,\quad
\mathrm{GT}=G,\quad\mathrm{AL}=G/N_{\mathrm{beams}},\quad
\mathrm{CAL}=G/N_{\mathrm{control\ arcs}},\quad\mathrm{MUdeg}=\mathrm{MU}_{\mathrm{total}}/G.
$$

缺处方、零旋转及无效权重的处理逐键不同。核心旧指标对某些 NaN 项计零且保留权重；补充指标可能均匀回退并警告，不能将两者解释成自动排除闭合样本。

## Aperture

把孔径分成纵向条带 $j$，jaws 裁剪后的高度为 $h_j$、左右界为 $l_j,r_j$，正间隙 $g_j=\max(r_j-l_j,0)$。$P$ 是矩形并集的完整边界长度，接触处的内部边不重复计数。

$$
A=\sum_jh_jg_j,\quad J=(X_2-X_1)_+(Y_2-Y_1)_+,\quad
\mathrm{PA}=\langle A\rangle_c,\quad\mathrm{JA}=\langle J\rangle_c,
$$
$$
\mathrm{perimeter}=\langle P\rangle_c,\quad
\mathrm{EFS}=\left\langle\frac{4A}{P}\right\rangle_c,\quad
\mathrm{psmall}=\langle\mathbf1_{\mathrm{EFS}_i<30\,\mathrm{mm}}\rangle_c,\quad
\mathrm{BJAR}=\langle A/J\rangle_c.
$$

EFS 的零周长项取零，因此闭合孔径可进入 `psmall`。`AXJD`、`AYJD` 是 jaw 跨度，不是叶尖与 jaw 的净距。

令 $H$ 为水平方向的暴露叶片侧边界长度；本程序 EM 的系数为 $C_1=0,C_2=1$：

$$
\mathrm{EM}=\langle H/A\rangle_c.
$$

EM 不是 $P/(2A)$。ALG、MAD、SAS 使用 Y jaw 内的原始正叶片间隙 $g_j^{\mathrm{raw}}$，不把 X jaw 裁剪后的间隙代入：

$$
\mathrm{ALG}=\left\langle\frac1{n_i}\sum_{j:g_j^{\mathrm{raw}}>0}g_j^{\mathrm{raw}}\right\rangle_c,\quad
\mathrm{MAD}=\left\langle\frac1{n_i}\sum_{j:g_j^{\mathrm{raw}}>0}\left|\frac{L_j+R_j}{2}\right|\right\rangle_c,
$$
$$
\mathrm{SAS}_{\tau}=\left\langle\frac{\#\{j:0<g_j^{\mathrm{raw}}<\tau\}}{n_i}\right\rangle_c,
\quad\tau\in\{5,10,20\}\,\mathrm{mm}.
$$

ALG_SD 为控制点平衡权重下的总体标准差；不是所有叶片样本不加权混池。TG 对 jaw 内原始相邻 bank 位置差求均值，包含闭合叶片；ASR 按裁剪后大于 0.5 mm 的条带连接分量计数，横向间隙仅接触也视为断开。

$$
\mathrm{CAM}_i=1-\frac1{n_i}\sum_j(1-e^{-g_j/(10\,\mathrm{mm})})(1-e^{-\sqrt{A_i}/(10\,\mathrm{mm})}),
$$
$$
\mathrm{EAM}_i=\frac{10\,\mathrm{mm}\,H_{\mathrm{exposed},i}}{A_i+5\,\mathrm{mm}\,H_{\mathrm{exposed},i}}.
$$

CAM 包含 Y jaw 内闭合条带；EAM 的暴露高度也可来自闭合叶片。各键的退化分母规则见契约，不能统一承诺为零。

## Modulation

MCS 的归一化面积 $E$ 是跨控制点的原始 bank 包络与最大暴露高度组合；PM 的 $U$ 是各条带最大裁剪面积之和。两者都不应称为完整几何并集：

$$
E=\sum_j(\max_iR_{ij}-\min_iL_{ij})_+\max_i h_{ij},\quad
U=\sum_j\max_i(h_{ij}g_{ij}),\quad \mathrm{AAV}_i=A_i/E.
$$

包络只使用该叶片未完全位于 jaws 外的控制点。对每个 bank 的活动位置序列 $x_1,\ldots,x_n$：

$$
V(x)=1-\frac{\sum_{j=1}^{n-1}|x_{j+1}-x_j|}{(n-1)(\max x-\min x)},\quad
\mathrm{LSV}_i=V(L_i)V(R_i).
$$

常量 bank 或单叶取 1，无活动叶片取 0。活动索引压缩后相邻，不要求原索引相邻。

$$
t_i=\frac{\mathrm{AAV}_i+\mathrm{AAV}_{i+1}}2
\frac{\mathrm{LSV}_i+\mathrm{LSV}_{i+1}}2,\quad
\mathrm{MCS}=\left\langle\langle t\rangle_d\right\rangle_M,
$$
$$
\mathrm{PM}=\left\langle1-\frac{\langle A\rangle_c}{U}\right\rangle_M,\quad
\mathrm{MD}=\left\langle\frac{U}{\langle A\rangle_c}\right\rangle_M,\quad
\mathrm{PI}=\left\langle\left\langle\frac{P^2}{4\pi A}\right\rangle_c\right\rangle_M.
$$

MCS 是两个端点均值的乘积，既不是端点乘积的均值，也不是中点几何。独立 AAV/LSV 输出先取相邻端点均值再区间加权；PI 的零面积项取零。

## Travel

令 $D_i=\sum_j(|\Delta L_{ij}|+|\Delta R_{ij}|)$，仅剔除在两端均完全位于 jaws 外的叶片对；$n_i$ 是两端活动叶片对数的均值。

$$
\mathrm{LT}=\langle D\rangle_d,\quad\mathrm{LTMU}=\frac{\sum_iD_i}{M_b},\quad
\mathrm{LTNL}=\langle D/n\rangle_d,\quad\mathrm{LTNLMU}=\frac{\sum_iD_i/n_i}{M_b},
$$
$$
\mathrm{LTAL}=\langle D/|\delta\theta|\rangle_d,\quad
\mathrm{LNA}=\langle D/(n|\delta\theta|)\rangle_d.
$$

计划值再按射束 MU 聚合。`nl` 的旧含义是叶片对数，与 `nl_pairs` 相同；`nl_leaves=2*nl_pairs`。`lt_mean_leaf` 先求每片实体叶的总轨迹，再在发生运动的叶片中求均值，最后按射束 MU 聚合；它没有区间 MU 加权，活动判断只使用 Y jaw。

## Dynamics

RTPLAN 没有实测时间戳时，使用处方剂量率和机器最大角速度估计时间：

$$
\Delta t_i=\max\left(\frac{|d_i|}{\mathrm{DoseRateSet}_i/60},\frac{|\delta\theta_i|}{\omega_{\max}}\right),\quad
\mathrm{DR}_i=|d_i|/\Delta t_i,\quad\mathrm{GS}_i=|\delta\theta_i|/\Delta t_i.
$$

只使用可用候选项。DR 单位 MU/s，GS 为度/s；叶速度由位置差除以该估计时间。LS 先对每片叶的有限正速度求均值，再对叶片求均值。

$$
\mathrm{mDRV}=\operatorname{mean}_{\mathrm{finite}}\frac{|\Delta\mathrm{DR}|}{|\delta\theta|},\quad
\mathrm{mGSV}=\operatorname{mean}_{\mathrm{finite}}\frac{|\Delta\mathrm{GS}|}{|\delta\theta|}.
$$

零角差项取零。旧输出 `dt` 是平均区间时间乘控制点数，不是区间时间之和；缺累积 MU 或时间计算异常时六项旧动力学指标可全为零，不应解释为实测静止。

Park 分箱速度为 [0,4)、[4,8)、[8,12)、[12,16)、[16,20] mm/s；加速度为 [0,40) 等五档至 [160,200] mm/s²。分母包含全部有限值，超上限者不进入任何箱，所以五箱之和可能小于 1。均值与样本标准差（ddof=1）排除零；各可用叶片等权，计划按 $\max(N_{\mathrm{CP}}-1,1)$ 加权，非 MU 权重。无效时间为不可用值。`mlc_speed_acc` 是容器，标量分箱另列。

## MI

全部原始叶片参与，不作 jaw 过滤。每片叶速度、加速度分别用其样本标准差归一化，$\alpha=1/\overline{\Delta t}$：

$$
r_v=v/\sigma_v,\quad r_a=|a|/(\alpha\sigma_a),\quad
\mathrm{MIs}(k)=\frac{\sum_{i,j}\min(r_{v,ij},k)}{\max(N_{\mathrm{CP}}-1,1)},
$$
$$
\mathrm{MIa}(k)=\frac{\sum_{i,j}\min(\max(r_{v,ij},r_{a,ij}),k)}{\max(N_{\mathrm{CP}}-2,1)},
$$
$$
W_{\mathrm{GA},i}=\frac2{1+e^{-a_{\mathrm{gantry},i}/2}},\quad
W_{\mathrm{MU},i}=\frac2{1+e^{-\Delta\mathrm{DR}_i/2}},\quad
\mathrm{MIt}(k)=\frac{\sum_iW_{\mathrm{GA},i}W_{\mathrm{MU},i}\sum_j\min(\max(r_{v,ij},r_{a,ij}),k)}{\max(N_{\mathrm{CP}}-2,1)}.
$$

时间行按实现对齐。零尺度的正分子产生无穷比值后由 k 截断，0/0 项置零。输出 $k=0.2,0.5,1,2$；三元容器顺序为 MIs、MIa、MIt，CSV 导出对应标量组件。计划按射束 MU 聚合。

## Sport

对站点 s 的前后各十个控制点邻域 $\mathcal N_s$，使用全部原始叶片：

$$
\mathrm{SPORT}_s=\sum_{t\in\mathcal N_s}\sum_j
\frac{|x_{sj}-x_{tj}|\,|u_s-u_t|}{|\theta_s-\theta_t|_{\mathrm{shortest}}}.
$$

跳过零角差。站点按中心控制点 MU、射束按 MU 聚合；权重缺失时使用 NaN 忽略均值，长度不匹配时按实现截断。双层分别输出，不是双层交集的物理运动。
