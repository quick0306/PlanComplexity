# Aurora SVMAT：统一物理孔径与指标公式

当前公式版本为 `aurora-v5-unified-physical-closure1mm`（2026-10-23）。共77个输出键，包含别名和派生量。V2/V3/legacy/V4仍表示输出家族，不再表示混用不同的孔径实现。

## Motion

每个物理层的位置数组分别拆成前N个A-bank与后N个B-bank。MLCX1和MLCX2是两个完整MLC层。用两层真实叶片边界的并集划分共同Y覆盖，求每条带的双层开口交集并裁剪X/Y jaws。

令原始交集间隙为g；g≤1+10⁻⁸ mm时置零，其余保留原宽度。这是统一的几何分析闭合约定，不代表测得的穿透或半影宽度。面积和周长均在掩膜后的矩形并集上计算。

$$
g_{ij}=[\min(R^{(1)}_{ij},R^{(2)}_{ij},X_{2i})-\max(L^{(1)}_{ij},L^{(2)}_{ij},X_{1i})]_+,\qquad
A_i=\sum_jh_{ij}\,\widetilde g_{ij}.
$$

原来的两通道逐项相减代理已退出当前计算。孔径变化率改为实际交集面积变化/床位移：

$$
a_i=\frac{|A_{i+1}-A_i|}{|\Delta z_i|},\quad
\mathrm{aperture\_change\_per\_mm}
=\frac{\sum_{|\Delta z_i|>0}|A_{i+1}-A_i|}{\sum_{|\Delta z_i|>0}|\Delta z_i|}.
$$

单位为mm²/mm。均值、CV、P95、max、top3及区域指标使用同一面积序列。几何变化率保留所有正床位移区间，包括零MU增量区间；它描述几何轨迹，不是交付MU加权平均。缺少任一参与射束的有效几何时，不计算部分计划均值。

以下轨迹及相对密度定义保持：

$$
p_i=|\Delta z_i|/|\Delta\theta_i|,\quad
\rho_i=|\Delta C_i|/|\Delta z_i|,\quad
v_i=\sum_{\ell}|\Delta x_{i\ell}|/|\Delta z_i|.
$$

角差按观测序列最短展开；不跨射束连接。普通均值、总体CV、最近秩P95及top3均在有效区间上计算：

$$
\mathrm{CV}(x)=\sigma_{\rm population}(x)/|\bar x|,\quad P_{95}=x_{(\lceil0.95N\rceil)}.
$$

名字含proxy的剂量密度仍使用相对CMW差。mu_per_mm改为绝对BeamMeterset总MU/总轴向行程；任一射束MU缺失或非法时为空，不能用相对权重跨度代替绝对MU。

## Aperture

所有孔径均值使用正ΔCMW区间的下一端点i+1。CMW必须有限、从零起、非递减且末值正。相同闭合掩膜用于面积、周长、SAS、LSV、AAV包络、小开度和层面积差。

$$
w_{bi}=\frac{\Delta C_{bi}}{C_{b,\mathrm{final}}}M_b,\qquad
E_{\rm open}[f]=
\frac{\sum_{bi:A_{b,i+1}>0}w_{bi}f_{b,i+1}}
{\sum_{bi:A_{b,i+1}>0}w_{bi}}.
$$

闭合端点不进入均值分母。零MU射束及零增量区间不产生样本。若任一射束缺少MU，全部贡献射束先使用单位归一化相对权重，并输出警告；排除闭合端点后不再重新平衡射束。原始几何/权重非法时输出空值及原因，不静默丢弃该射束。

$$
\mathrm{BA}=E_{\rm open}[A],\qquad
\mathrm{BI}=E_{\rm open}[P^2/(4\pi A)],\qquad
\mathrm{CA}=E_{\rm open}[P/A].
$$

P是矩形并集的完整外露边界，包括不连通区域，公共内边不重复计数。CA单位mm⁻¹，是周长/面积，不是圆度，也不是BI的倒数。

$$
\mathrm{SAS}_{\tau}=E_{\rm open}\left[
\frac{\#\{j:1+10^{-8}<g_{ij}<\tau\}}
{\#\{j:g_{ij}>1+10^{-8}\}}
\right],\qquad \tau=5,10\ {\rm mm}.
$$

同一控制点内有效子条带等计数，然后按开放交付权重汇总。SAS不是“面积/跨度低于阈值”的控制点占比，也不是将全计划叶隙直接混池。等于5或10 mm不计入相应分子。

每束分别建立同一掩膜下的逐条带最大面积包络：

$$
U_b=\sum_j\max_{i:\Delta C_i>0}(h_{i+1,j}\widetilde g_{i+1,j}),\quad
\mathrm{AAV}_i=A_i/U_b,\quad
\mathrm{LSV}_i=1-\frac{\sum_{j=1}^{n-1}|g_{j+1}-g_j|}{(n-1)\max_j g_j}.
$$

LSV仅使用按Y排列的开放间隙压缩序列；n≤1取1，结果限制在[0,1]。这是Aurora间隙序列改编MCS，不是原始McNiven bank-based MCS；U也不是整束最大总面积或真实多边形并集。

$$
\mathrm{mean\_mcs\_aurora}=E_{\rm open}[\mathrm{AAV}\,\mathrm{LSV}],\qquad
\mathrm{mcs\_complexity\_aurora}=1-\mathrm{mean\_mcs\_aurora}.
$$

## Research

小开度、近闭合和严重度与SAS共用几何、样本、分母及交付权重：

$$
\mathrm{small\_opening\_fraction}=\mathrm{SAS}_{10},\quad
\mathrm{near\_closed\_fraction}=\mathrm{SAS}_{2},\quad
B_{10}=E_{\rm open}[\operatorname{mean}_{g>1+10^{-8}}(1-g/10)_+].
$$

层孔径差异改为同一Y覆盖和jaws内的两个原生层面积差；不再比较绝对叶片坐标幅值：

$$
D_{\rm layer}=E_{\rm open}\left[\frac{|A_1-A_2|}{A_1+A_2}\right].
$$

原生层面积也应用1 mm闭合掩膜；采样端点仍以有效交集开放为条件。整体平移叶片与jaws不会改变该指标。

层行程比、不平衡和相关系数仍根据两个物理层的区间叶片行程计算。区域按区间z中点的全局跨度三等分：低z为head、中间为mid、高z为tail；不保证每区间数量恰好相等，也不能单凭标签解释患者解剖方向。

耦合指标保持等权饱和组合，明确固定单位尺度：

$$
C=\operatorname{mean}_{x\ {\rm available}}\frac{x}{1+x},\quad
x\in\left\{\frac{\mathrm{area\ change/mm}}{1\ {\rm mm^2/mm}},
\frac{\mathrm{leaf\ travel/mm}}{1\ {\rm mm/mm}},
\mathrm{CV}(\rho),\mathrm{CV}(p)\right\}.
$$

物理面积项是必要输入；无效几何不允许由其余分量生成一个部分耦合值。没有通过队列数据拟合尺度或系数。

正反向按净z位移符号分组。各方向内先作射束等权平均；对密度、孔径面积变化、叶片行程、pitch四个家族的对称性取均值：

$$
S=\operatorname{mean}_k\left(1-\frac{|f_k-b_k|}{|f_k|+|b_k|}\right),\quad
D=|\bar C_f-\bar C_b|,\quad
B=1-\frac{|\sum C_f-\sum C_b|}{\sum C_f+\sum C_b}.
$$

双方均零时对应对称性为1；缺任一方向为空。Difference和Balance不是互补量。

## Migration

77个键保持，但孔径变化单位、闭合掩膜、小开度、层孔径差异、耦合与正反向派生量、绝对MU/mm均需按新版重新计算。几何阈值也影响七项物理孔径指标。旧数值只用于历史复现，不与新版直接混合。

逐控制点/区间导出包含effective_aperture_area_mm2或起止面积、aperture_closure_threshold_mm和metric_formula_version，供逐步核验。旧aperture_width_mm代理列已退出当前导出。

运行完整测试和针对性测试后，可用tools/recompute_aurora_migration.py对本地RTPLAN目录生成新版77列、逐指标变化汇总和输入哈希。原始临床文件与逐例结果留在本地。
