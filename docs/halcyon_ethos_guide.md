# Halcyon / Ethos：双层解释与 LaTeX 公式

通过 `AUTO` 或 `VMAT_IMRT` 分析，必须具备可识别的双层、叶片边界、jaws 和权重。这里的专属算法有机器结构检查，不能把所有双层机器自动视为 Halcyon。共享符号、通用公式见 [IMRT/VMAT](vmat_imrt_guide.md)，逐键差异见[定义表](metric_definitions_vmat_imrt.md)。

## Representations

MLCX1 为 distal，MLCX2 为 proximal。有效孔径在对齐的原生边界上按 5 mm 条带构建双层交集：

$$
l_j^{\mathrm{eff}}=\max(l_j^p,l_j^d,X_1),\quad
r_j^{\mathrm{eff}}=\min(r_j^p,r_j^d,X_2),\quad
g_j^{\mathrm{eff}}=(r_j^{\mathrm{eff}}-l_j^{\mathrm{eff}})_+.
$$

原生层描述实体叶片运动；effective 描述合成开口；stacked 是坐标拼接表示，不是具有透射含义的物理孔径。effective 虚拟条带数不能当实体叶片数。`mcsv_mlcx1`、`mcsv_mlcx2` 保留原生值，兼容标量 `mcsv` 可表示 effective 论文路径，比较时应指定完整键。Hybrid v2 的原生层、effective、stacked 指标共享各自表示上的通用公式，不能先把数值混合再解释为有效孔径。

还需区分聚合细节：原生 ALG_SD 通过射束均值和方差按 MU 混池；effective/stacked 是射束 SD 的 MU 均值。effective/stacked LT 用两端任一 Y jaw 重叠的槽位，不用 X jaw 排除轨迹。它们不是把通用原生层结果简单改名。跨层对齐失败使 hybrid 输出不可用；无活动叶片的某些射束会被排除，见逐键契约。

## Tamura

MCS5、PA5、PI5、PM5 在 5 mm 有效交集上使用通用 MCS、面积、PI、PM 公式。每个有效开口的左右限制边分别归属更紧的一层，同界各分一半（实现使用数值近似比较）。设共有 $2N_i$ 个有效限制边，层归属分数为：

$$
w_{\ell,i}=\frac{e_{\ell,i}}{2N_i},\quad
u_{\ell,i}=\frac{e_{\ell,i}^{\mathrm{unique}}}{2N_i},\quad
w_{p,i}+w_{d,i}=1.
$$

u 排除同界边，不是面积比例。无有效开口时 w 各为 0.5，u 为 0。令 $t_{\ell,i}=\overline{\mathrm{AAV}}_{\ell,i}\overline{\mathrm{LSV}}_{\ell,i}$，横线表示相邻端点算术均值：

$$
\mathrm{MCSw}_{\ell}=\sum_i\widehat d_i\,t_{\ell,i}\overline w_{\ell,i},\quad
\mathrm{PAw}_{\ell}=\langle w_{\ell}A_{\ell}\rangle_c,\quad
\mathrm{PIw}_{\ell}=\langle w_{\ell}\mathrm{PI}_{\ell}\rangle_c,
$$
$$
\mathrm{PMw}_{\ell}=\left\langle w_{\ell}\left(1-\frac{A_{\ell}}{U_{\ell}}\right)\right\rangle_c,\quad
\mathrm{EDS}=\langle w_d\rangle_c.
$$

$\widehat d_i=d_i/\sum_i d_i$；层贡献直接相加，不对层权重再次归一化。PMw 层贡献下限取零、总量裁剪至 [0,1]；射束结果按 MU 聚合。

## Quintero

$$
\mathrm{UL}_{\ell}=\langle u_{\ell}\rangle_c,\quad
\mathrm{UL}=\mathrm{UL}_p+\mathrm{UL}_d,\quad
\mathrm{MCSUL}_{\ell}=\sum_i\widehat d_i\,t_{\ell,i}\overline w_{\ell,i}\overline u_{\ell,i},\quad
\mathrm{MCSUL}=\mathrm{MCSUL}_p+\mathrm{MCSUL}_d.
$$

两个端点均值分别相乘，不是先将 w 与 u 相乘再平均。`MUcp` 为：

$$
\mathrm{MUcp}=100\,\frac{\operatorname{mean}_i d_i}{M_b}.
$$

NP 在位移范围大于 $10^{-6}$ 的原始运动叶片轨迹上计峰，再对这些叶片算术平均；优先使用 SciPy `find_peaks`，回退实现仅计严格邻域峰，平台峰可能不同。其定义不是叶速度峰或 MU 加权峰数。

## Report

`ethos-report-v2` 的 SAS10、1−MCS、PR 是独立报告口径，不能用通用同名指标替换。仅支持完整、连续、未裁剪的 5 mm 有效条带、有效 MU 与有限 CMW。全闭合射束使该报告配置不可用，不套用 Aurora 开放条件均值。

定义报告开放集 $\mathcal O_i=\{j:g_{ij}>0.5\,\mathrm{mm}+10^{-8}\,\mathrm{mm}\}$。对中心 MU 为正的控制点，射束 SAS10 使用计数混池：

$$
\mathrm{SAS10}_b=\frac{\sum_i\#\{j\in\mathcal O_i:g_{ij}\le10\,\mathrm{mm}+10^{-8}\,\mathrm{mm}\}}{\sum_i|\mathcal O_i|}.
$$

这是射束内计数比，非控制点 MU 均值；计划再按射束 MU 平均。报告 MCS 使用开放时 bank 包络 $E_{\mathrm{open}}$ 及只连接物理相邻开放条带的 bank LSV：

$$
(1-\mathrm{MCS})_b=1-\left\langle\frac{A_{\mathrm{open},i}}{E_{\mathrm{open}}}\mathrm{LSV}_{\mathrm{adjacent},i}\right\rangle_c,\quad
\mathrm{PR}_i=\frac{|\mathcal R_{\mathrm{tip},i}\cup\mathcal R_{\mathrm{side},i}|}{A_{\mathrm{open},i}}.
$$

PR 用叶尖 2.8 mm、暴露叶侧 2.3 mm 的风险区多边形并集，不能替换为周长乘厚度。完整几何条件与异常处理见 [Ethos 报告配置](ethos_report_profile.md)。
