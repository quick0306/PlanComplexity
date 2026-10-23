# Aurora 统一物理孔径指标

当前版本：`aurora-v5-unified-physical-closure1mm`。完整数学定义及使用说明见[Aurora 全指标说明](aurora_guide.md)，迁移见[V5迁移](aurora_v5_migration.md)。

共享几何实现位于 `aurora_svmat_lab/physical_aperture.py`。两层分别拆A/B bank，按真实叶片边界划分共同Y条带并求交集、裁剪jaws。有效叶隙≤1+10⁻⁸ mm闭合；同一掩膜用于孔径面积、周长、SAS、MCS和小开度指标。

| 输出 | 定义 | 单位 |
| --- | --- | --- |
| mean_ba | 开放交付MU条件均值 A | mm² |
| mean_bi | 开放交付MU条件均值 P²/(4πA) | 无量纲 |
| mean_ca | 开放交付MU条件均值 P/A，不是圆度 | mm⁻¹ |
| mean_sas5 / mean_sas10 | 逐CP开放有效条带小叶隙占比，再作开放交付MU均值 | 无量纲 |
| mean_mcs_aurora | 同一掩膜下的逐条带包络AAV×间隙序列LSV的条件均值 | 无量纲 |
| mcs_complexity_aurora | 1−mean_mcs_aurora | 无量纲 |

SAS严格小于5/10 mm，不使用等效宽度判定。MCS是Aurora改编公式，不是原始McNiven bank-based MCS。small_opening_fraction与mean_sas10完全相同；near_closed_fraction使用2 mm上限；严重度为同一开放条带上(1−g/10)的正部均值。

孔径变化及其区域/峰值从实际交集面积序列重建，单位mm²/mm；几何轨迹统计仍使用正床位移区间。层孔径差异使用原生层面积差，不使用绝对位置幅值。mu_per_mm读取绝对BeamMeterset，缺失时为空。

所有孔径均值只使用正ΔCMW的下一端点；面积零端点排除并重新归一化开放权重，零增量不产生伪样本。缺少MU时全部射束回退到单位相对权重并警告。无效几何不允许计算部分计划均值。全部闭合时孔径均值为空；几何面积变化仍可为零。

77个输出键保留，其中含别名和派生量；旧版数值不能与新版直接混合。
