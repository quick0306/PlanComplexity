# 全平台指标与 LaTeX 公式索引

由 `python tools/export_metric_definitions.py` 生成。每个已注册记录均指向可直接编辑的 Markdown/LaTeX 章节。

公式章节按共享定义归组，原生层、effective、stacked 和容器/标量组件仍是独立记录。章节公式与逐项公式契约共同阅读，不能把共享符号理解为跨平台同一算法。

| Platform | Metric key | Display name | Unit | LaTeX chapter |
| --- | --- | --- | --- | --- |
| VMAT_IMRT | `ethos_sas10` | Varian Dual-layer SAS10 | dimensionless | [Varian Ethos/Halcyon dual-layer MLC](halcyon_ethos_guide.md#report) |
| VMAT_IMRT | `ethos_one_minus_mcs` | Varian Dual-layer 1-MCS | dimensionless | [Varian Ethos/Halcyon dual-layer MLC](halcyon_ethos_guide.md#report) |
| VMAT_IMRT | `ethos_penumbra_ratio` | Varian Dual-layer Penumbra Ratio | dimensionless | [Varian Ethos/Halcyon dual-layer MLC](halcyon_ethos_guide.md#report) |
| VMAT_IMRT | `mus` | MUs | MU | [Plan prescription](vmat_imrt_guide.md#plan) |
| VMAT_IMRT | `pmu` | PMU | MU | [Plan prescription](vmat_imrt_guide.md#plan) |
| VMAT_IMRT | `muca` | MUCA | MU/control arc | [Plan prescription](vmat_imrt_guide.md#plan) |
| VMAT_IMRT | `fraction_dose_gy` | Prescribed Dose | Gy | [Plan prescription](vmat_imrt_guide.md#plan) |
| VMAT_IMRT | `fractions_count` | Fractions | count | [Plan prescription](vmat_imrt_guide.md#plan) |
| VMAT_IMRT | `mucgy` | MUcGy | MU/cGy | [Plan prescription](vmat_imrt_guide.md#plan) |
| VMAT_IMRT | `lt` | LT | mm | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `lt_mlcx1` | LT MLCX1 | mm | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `lt_mlcx2` | LT MLCX2 | mm | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `ltmu` | LTMU | mm/MU | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `ltmu_mlcx1` | LTMU MLCX1 | mm/MU | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `ltmu_mlcx2` | LTMU MLCX2 | mm/MU | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `ltnlmu` | LTNLMU | mm/(pair*MU) | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `ltnlmu_mlcx1` | LTNLMU MLCX1 | mm/(pair*MU) | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `ltnlmu_mlcx2` | LTNLMU MLCX2 | mm/(pair*MU) | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `nl` | NL | count | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `nl_mlcx1` | NL MLCX1 | count | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `nl_mlcx2` | NL MLCX2 | count | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `ltnl` | LTNL | mm/pair | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `ltnl_mlcx1` | LTNL MLCX1 | mm/pair | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `ltnl_mlcx2` | LTNL MLCX2 | mm/pair | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `al` | AL | deg | [Arc geometry](vmat_imrt_guide.md#plan) |
| VMAT_IMRT | `lna` | LNA | mm/(pair*deg) | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `lna_mlcx1` | LNA MLCX1 | mm/(pair*deg) | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `lna_mlcx2` | LNA MLCX2 | mm/(pair*deg) | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `cal` | CAL | deg/control arc | [Arc geometry](vmat_imrt_guide.md#plan) |
| VMAT_IMRT | `gt` | GT | deg | [Arc geometry](vmat_imrt_guide.md#plan) |
| VMAT_IMRT | `mudeg` | MUdeg | MU/deg | [Arc geometry](vmat_imrt_guide.md#plan) |
| VMAT_IMRT | `ltal` | LTAL | mm/deg | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `ltal_mlcx1` | LTAL MLCX1 | mm/deg | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `ltal_mlcx2` | LTAL MLCX2 | mm/deg | [Leaf travel](vmat_imrt_guide.md#travel) |
| VMAT_IMRT | `narcs` | NArcs | count | [Plan prescription](vmat_imrt_guide.md#plan) |
| VMAT_IMRT | `mdrv` | mDRV | MU/(s*deg) | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mdrv_mlcx1` | mDRV MLCX1 | MU/(s*deg) | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mdrv_mlcx2` | mDRV MLCX2 | MU/(s*deg) | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mgsv` | mGSV | deg/s/deg | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mgsv_mlcx1` | mGSV MLCX1 | deg/s/deg | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mgsv_mlcx2` | mGSV MLCX2 | deg/s/deg | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `dr` | DR | MU/s | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `dr_mlcx1` | DR MLCX1 | MU/s | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `dr_mlcx2` | DR MLCX2 | MU/s | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `gs` | GS | deg/s | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `gs_mlcx1` | GS MLCX1 | deg/s | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `gs_mlcx2` | GS MLCX2 | deg/s | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `ls` | LS | mm/s | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `ls_mlcx1` | LS MLCX1 | mm/s | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `ls_mlcx2` | LS MLCX2 | mm/s | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mcsv` | MCSv | dimensionless | [McNiven-style modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `mcsv_mlcx1` | MCSv MLCX1 | dimensionless | [McNiven-style modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `mcsv_mlcx2` | MCSv MLCX2 | dimensionless | [McNiven-style modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `aav` | AAV | dimensionless | [McNiven-style modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `aav_mlcx1` | AAV MLCX1 | dimensionless | [McNiven-style modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `aav_mlcx2` | AAV MLCX2 | dimensionless | [McNiven-style modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `lsv` | LSV | dimensionless | [McNiven-style modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `lsv_mlcx1` | LSV MLCX1 | dimensionless | [McNiven-style modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `lsv_mlcx2` | LSV MLCX2 | dimensionless | [McNiven-style modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `tg` | TG | mm | [McNiven-style modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `tg_mlcx1` | TG MLCX1 | mm | [McNiven-style modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `tg_mlcx2` | TG MLCX2 | mm | [McNiven-style modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `mi_0_2` | MI(0.2) | dimensionless | [MI family](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_2_mis` | MI(0.2) Speed | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_2_mia` | MI(0.2) Acceleration | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_2_mit` | MI(0.2) Total | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_2_mlcx1_mis` | MI(0.2) MLCX1 Speed | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_2_mlcx1_mia` | MI(0.2) MLCX1 Acceleration | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_2_mlcx1_mit` | MI(0.2) MLCX1 Total | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_2_mlcx2_mis` | MI(0.2) MLCX2 Speed | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_2_mlcx2_mia` | MI(0.2) MLCX2 Acceleration | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_2_mlcx2_mit` | MI(0.2) MLCX2 Total | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_5` | MI(0.5) | dimensionless | [MI family](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_5_mis` | MI(0.5) Speed | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_5_mia` | MI(0.5) Acceleration | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_5_mit` | MI(0.5) Total | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_5_mlcx1_mis` | MI(0.5) MLCX1 Speed | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_5_mlcx1_mia` | MI(0.5) MLCX1 Acceleration | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_5_mlcx1_mit` | MI(0.5) MLCX1 Total | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_5_mlcx2_mis` | MI(0.5) MLCX2 Speed | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_5_mlcx2_mia` | MI(0.5) MLCX2 Acceleration | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_0_5_mlcx2_mit` | MI(0.5) MLCX2 Total | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_1_0` | MI(1.0) | dimensionless | [MI family](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_1_0_mis` | MI(1.0) Speed | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_1_0_mia` | MI(1.0) Acceleration | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_1_0_mit` | MI(1.0) Total | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_1_0_mlcx1_mis` | MI(1.0) MLCX1 Speed | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_1_0_mlcx1_mia` | MI(1.0) MLCX1 Acceleration | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_1_0_mlcx1_mit` | MI(1.0) MLCX1 Total | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_1_0_mlcx2_mis` | MI(1.0) MLCX2 Speed | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_1_0_mlcx2_mia` | MI(1.0) MLCX2 Acceleration | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_1_0_mlcx2_mit` | MI(1.0) MLCX2 Total | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_2_0` | MI(2.0) | dimensionless | [MI family](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_2_0_mis` | MI(2.0) Speed | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_2_0_mia` | MI(2.0) Acceleration | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_2_0_mit` | MI(2.0) Total | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_2_0_mlcx1_mis` | MI(2.0) MLCX1 Speed | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_2_0_mlcx1_mia` | MI(2.0) MLCX1 Acceleration | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_2_0_mlcx1_mit` | MI(2.0) MLCX1 Total | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_2_0_mlcx2_mis` | MI(2.0) MLCX2 Speed | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_2_0_mlcx2_mia` | MI(2.0) MLCX2 Acceleration | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `mi_2_0_mlcx2_mit` | MI(2.0) MLCX2 Total | dimensionless | [MI components](vmat_imrt_guide.md#mi) |
| VMAT_IMRT | `dt` | dt | s | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `dt_mlcx1` | dt MLCX1 | s | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `dt_mlcx2` | dt MLCX2 | s | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `pi` | PI | dimensionless | [Shape modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `pi_mlcx1` | PI MLCX1 | dimensionless | [Shape modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `pi_mlcx2` | PI MLCX2 | dimensionless | [Shape modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `pm` | PM | dimensionless | [Shape modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `pm_mlcx1` | PM MLCX1 | dimensionless | [Shape modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `pm_mlcx2` | PM MLCX2 | dimensionless | [Shape modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `mcs5` | MCS5 (Tamura 2020 effective 5 mm MLC) | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `pa5` | PA5 (Tamura 2020 effective 5 mm MLC) | mm^2 | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `pi5` | PI5 (Tamura 2020 effective 5 mm MLC) | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `pm5` | PM5 (Tamura 2020 effective 5 mm MLC) | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `eds` | EDS (Tamura 2020 effective distal MLC score) | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `mcsw` | MCSw (Tamura 2020 weighted dual-layer MCS) | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `paw` | PAw (Tamura 2020 weighted dual-layer PA) | mm^2 | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `piw` | PIw (Tamura 2020 weighted dual-layer PI) | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `pmw` | PMw (Tamura 2020 weighted dual-layer PM) | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `proximal_mcs` | pMCS | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `distal_mcs` | dMCS | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `proximal_pa` | pPA | mm^2 | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `distal_pa` | dPA | mm^2 | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `proximal_pi` | pPI | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `distal_pi` | dPI | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `proximal_pm` | pPM | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `distal_pm` | dPM | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `proximal_mcsw` | pMCSw | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `distal_mcsw` | dMCSw | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `proximal_paw` | pPAw | mm^2 | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `distal_paw` | dPAw | mm^2 | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `proximal_piw` | pPIw | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `distal_piw` | dPIw | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `proximal_pmw` | pPMw | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `distal_pmw` | dPMw | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `ul` | UL (Quintero 2021 uncovered-layer score) | dimensionless | [Halcyon/Ethos Quintero 2021](halcyon_ethos_guide.md#quintero) |
| VMAT_IMRT | `proximal_ul` | pUL | dimensionless | [Halcyon/Ethos Quintero 2021](halcyon_ethos_guide.md#quintero) |
| VMAT_IMRT | `distal_ul` | dUL | dimensionless | [Halcyon/Ethos Quintero 2021](halcyon_ethos_guide.md#quintero) |
| VMAT_IMRT | `mcsul` | MCSUL (Quintero 2021 uncovered-layer weighted MCS) | dimensionless | [Halcyon/Ethos Quintero 2021](halcyon_ethos_guide.md#quintero) |
| VMAT_IMRT | `proximal_mcsul` | pMCSUL | dimensionless | [Halcyon/Ethos Quintero 2021](halcyon_ethos_guide.md#quintero) |
| VMAT_IMRT | `distal_mcsul` | dMCSUL | dimensionless | [Halcyon/Ethos Quintero 2021](halcyon_ethos_guide.md#quintero) |
| VMAT_IMRT | `np` | NP (Quintero 2021 number of peaks score) | peaks/leaf | [Halcyon/Ethos Quintero 2021](halcyon_ethos_guide.md#quintero) |
| VMAT_IMRT | `mucp` | MUcp (Quintero 2021 mean MU increment %) | % | [Halcyon/Ethos Quintero 2021](halcyon_ethos_guide.md#quintero) |
| VMAT_IMRT | `proximal_weight_mean` | Mean wp | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `distal_weight_mean` | Mean wd | dimensionless | [Halcyon/Ethos Tamura 2020](halcyon_ethos_guide.md#tamura) |
| VMAT_IMRT | `md` | MD | dimensionless | [Shape modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `md_mlcx1` | MD MLCX1 | dimensionless | [Shape modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `md_mlcx2` | MD MLCX2 | dimensionless | [Shape modulation](vmat_imrt_guide.md#modulation) |
| VMAT_IMRT | `pa` | PA | mm^2 | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `pa_mlcx1` | PA MLCX1 | mm^2 | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `pa_mlcx2` | PA MLCX2 | mm^2 | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `efs` | EFS | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `efs_mlcx1` | EFS MLCX1 | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `efs_mlcx2` | EFS MLCX2 | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `psmall` | psmall | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `psmall_mlcx1` | psmall MLCX1 | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `psmall_mlcx2` | psmall MLCX2 | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `sas_5mm` | SAS5mm | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `sas_5mm_mlcx1` | SAS5mm MLCX1 | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `sas_5mm_mlcx2` | SAS5mm MLCX2 | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `sas_10mm` | SAS10mm | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `sas_10mm_mlcx1` | SAS10mm MLCX1 | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `sas_10mm_mlcx2` | SAS10mm MLCX2 | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `sas_20mm` | SAS20mm | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `sas_20mm_mlcx1` | SAS20mm MLCX1 | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `sas_20mm_mlcx2` | SAS20mm MLCX2 | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `em` | EM | mm^-1 | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `em_mlcx1` | EM MLCX1 | mm^-1 | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `em_mlcx2` | EM MLCX2 | mm^-1 | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `bjar` | BJAR | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `bjar_mlcx1` | BJAR MLCX1 | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `bjar_mlcx2` | BJAR MLCX2 | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `mad` | MAD | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `mad_mlcx1` | MAD MLCX1 | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `mad_mlcx2` | MAD MLCX2 | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `alg` | ALG | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `alg_mlcx1` | ALG MLCX1 | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `alg_mlcx2` | ALG MLCX2 | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `alg_sd` | ALG SD | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `alg_sd_mlcx1` | ALG SD MLCX1 | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `alg_sd_mlcx2` | ALG SD MLCX2 | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `perimeter` | P | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `perimeter_mlcx1` | P MLCX1 | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `perimeter_mlcx2` | P MLCX2 | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `asr` | ASR | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `asr_mlcx1` | ASR MLCX1 | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `asr_mlcx2` | ASR MLCX2 | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `axjd` | AXJD | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `axjd_mlcx1` | AXJD MLCX1 | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `axjd_mlcx2` | AXJD MLCX2 | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `ayjd` | AYJD | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `ayjd_mlcx1` | AYJD MLCX1 | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `ayjd_mlcx2` | AYJD MLCX2 | mm | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `ja` | JA | mm^2 | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `ja_mlcx1` | JA MLCX1 | mm^2 | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `ja_mlcx2` | JA MLCX2 | mm^2 | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `cam` | CAM | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `cam_mlcx1` | CAM MLCX1 | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `cam_mlcx2` | CAM MLCX2 | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `eam` | EAM | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `eam_mlcx1` | EAM MLCX1 | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `eam_mlcx2` | EAM MLCX2 | dimensionless | [Aperture geometry](vmat_imrt_guide.md#aperture) |
| VMAT_IMRT | `mlc_speed_acc` | MLC Speed and Acceleration Proportions (Park 2015) | dimensionless | [Delivery dynamics](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `speed_0_4` | Park Speed 0-4 mm/s | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `speed_4_8` | Park Speed 4-8 mm/s | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `speed_8_12` | Park Speed 8-12 mm/s | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `speed_12_16` | Park Speed 12-16 mm/s | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `speed_16_20` | Park Speed 16-20 mm/s | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `acc_0_40` | Park Acceleration 0-40 mm/s^2 | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `acc_40_80` | Park Acceleration 40-80 mm/s^2 | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `acc_80_120` | Park Acceleration 80-120 mm/s^2 | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `acc_120_160` | Park Acceleration 120-160 mm/s^2 | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `acc_160_200` | Park Acceleration 160-200 mm/s^2 | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `speed_average` | Mean Leaf Speed (mm/s) | mm/s | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `acc_average` | Mean Leaf Acceleration (mm/s^2) | mm/s^2 | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `speed_std` | Mean Leaf Speed SD (mm/s) | mm/s | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `acc_std` | Mean Leaf Acceleration SD (mm/s^2) | mm/s^2 | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx1_speed_0_4` | MLCX1 Park Speed 0-4 mm/s | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx1_speed_4_8` | MLCX1 Park Speed 4-8 mm/s | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx1_speed_8_12` | MLCX1 Park Speed 8-12 mm/s | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx1_speed_12_16` | MLCX1 Park Speed 12-16 mm/s | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx1_speed_16_20` | MLCX1 Park Speed 16-20 mm/s | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx1_acc_0_40` | MLCX1 Park Acceleration 0-40 mm/s^2 | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx1_acc_40_80` | MLCX1 Park Acceleration 40-80 mm/s^2 | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx1_acc_80_120` | MLCX1 Park Acceleration 80-120 mm/s^2 | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx1_acc_120_160` | MLCX1 Park Acceleration 120-160 mm/s^2 | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx1_acc_160_200` | MLCX1 Park Acceleration 160-200 mm/s^2 | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx1_speed_average` | MLCX1 Mean Leaf Speed (mm/s) | mm/s | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx1_acc_average` | MLCX1 Mean Leaf Acceleration (mm/s^2) | mm/s^2 | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx1_speed_std` | MLCX1 Mean Leaf Speed SD (mm/s) | mm/s | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx1_acc_std` | MLCX1 Mean Leaf Acceleration SD (mm/s^2) | mm/s^2 | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx2_speed_0_4` | MLCX2 Park Speed 0-4 mm/s | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx2_speed_4_8` | MLCX2 Park Speed 4-8 mm/s | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx2_speed_8_12` | MLCX2 Park Speed 8-12 mm/s | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx2_speed_12_16` | MLCX2 Park Speed 12-16 mm/s | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx2_speed_16_20` | MLCX2 Park Speed 16-20 mm/s | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx2_acc_0_40` | MLCX2 Park Acceleration 0-40 mm/s^2 | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx2_acc_40_80` | MLCX2 Park Acceleration 40-80 mm/s^2 | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx2_acc_80_120` | MLCX2 Park Acceleration 80-120 mm/s^2 | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx2_acc_120_160` | MLCX2 Park Acceleration 120-160 mm/s^2 | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx2_acc_160_200` | MLCX2 Park Acceleration 160-200 mm/s^2 | proportion | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx2_speed_average` | MLCX2 Mean Leaf Speed (mm/s) | mm/s | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx2_acc_average` | MLCX2 Mean Leaf Acceleration (mm/s^2) | mm/s^2 | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx2_speed_std` | MLCX2 Mean Leaf Speed SD (mm/s) | mm/s | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `mlcx2_acc_std` | MLCX2 Mean Leaf Acceleration SD (mm/s^2) | mm/s^2 | [Motion bins](vmat_imrt_guide.md#dynamics) |
| VMAT_IMRT | `lt_mean_leaf` | LT Mean Leaf | mm/moving leaf | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `lt_mean_leaf_mlcx1` | LT Mean Leaf MLCX1 | mm/moving leaf | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `lt_mean_leaf_mlcx2` | LT Mean Leaf MLCX2 | mm/moving leaf | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `nl_pairs` | NL Pairs | active leaf pairs | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `nl_pairs_mlcx1` | NL Pairs MLCX1 | active leaf pairs | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `nl_pairs_mlcx2` | NL Pairs MLCX2 | active leaf pairs | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `nl_leaves` | NL Leaves | active physical leaves | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `nl_leaves_mlcx1` | NL Leaves MLCX1 | active physical leaves | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `nl_leaves_mlcx2` | NL Leaves MLCX2 | active physical leaves | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `mcsv_effective` | MCSv Effective | dimensionless | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `aav_effective` | AAV Effective | dimensionless | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `lsv_effective` | LSV Effective | dimensionless | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `pa_effective` | PA Effective | mm^2 | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `mad_effective` | MAD Effective | mm | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `alg_effective` | ALG Effective | mm | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `alg_sd_effective` | ALG SD Effective | mm | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `sas_5mm_effective` | SAS5mm Effective | dimensionless | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `sas_10mm_effective` | SAS10mm Effective | dimensionless | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `sas_20mm_effective` | SAS20mm Effective | dimensionless | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `lt_effective` | LT Effective | mm | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `lt_mean_leaf_effective` | LT Mean Leaf Effective | mm/moving effective virtual leaf | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `nl_pairs_effective` | NL Pairs Effective | active effective virtual leaf pairs | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `nl_leaves_effective` | NL Leaves Effective | active effective virtual leaves | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `mcsv_stacked` | MCSv Stacked | dimensionless | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `aav_stacked` | AAV Stacked | dimensionless | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `lsv_stacked` | LSV Stacked | dimensionless | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `pa_stacked` | PA Stacked | mm^2 | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `mad_stacked` | MAD Stacked | mm | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `alg_stacked` | ALG Stacked | mm | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `alg_sd_stacked` | ALG SD Stacked | mm | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `sas_5mm_stacked` | SAS5mm Stacked | dimensionless | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `sas_10mm_stacked` | SAS10mm Stacked | dimensionless | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `sas_20mm_stacked` | SAS20mm Stacked | dimensionless | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `lt_stacked` | LT Stacked | mm | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `lt_mean_leaf_stacked` | LT Mean Leaf Stacked | mm/moving leaf | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `nl_pairs_stacked` | NL Pairs Stacked | active leaf pairs | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `nl_leaves_stacked` | NL Leaves Stacked | active physical leaves | [Halcyon/Ethos Hybrid v2](halcyon_ethos_guide.md#representations) |
| VMAT_IMRT | `sport` | SPORT Modulation Index (Li and Xing 2013) | mm*MU/deg | [SPORT](vmat_imrt_guide.md#sport) |
| VMAT_IMRT | `sport_mlcx1` | SPORT MLCX1 | mm*MU/deg | [SPORT](vmat_imrt_guide.md#sport) |
| VMAT_IMRT | `sport_mlcx2` | SPORT MLCX2 | mm*MU/deg | [SPORT](vmat_imrt_guide.md#sport) |
| TOMO | `mf` | MF | dimensionless | [Delivery](tomo_guide.md#delivery) |
| TOMO | `nproj_rot` | N proj,rot | count | [Delivery](tomo_guide.md#delivery) |
| TOMO | `nproj` | N proj | count | [Delivery](tomo_guide.md#delivery) |
| TOMO | `nrot` | N rot | count | [Delivery](tomo_guide.md#delivery) |
| TOMO | `projection_time_s` | PT | s | [Delivery](tomo_guide.md#delivery) |
| TOMO | `gantry_period_s` | GP | s | [Delivery](tomo_guide.md#delivery) |
| TOMO | `treatment_time_s` | TT | s | [Delivery](tomo_guide.md#delivery) |
| TOMO | `field_width_mm` | FW | mm | [Delivery](tomo_guide.md#delivery) |
| TOMO | `pitch` | Pitch | dimensionless | [Delivery](tomo_guide.md#delivery) |
| TOMO | `couch_translation_mm` | CT | mm | [Delivery](tomo_guide.md#delivery) |
| TOMO | `couch_speed_mm_s` | CS | mm/s | [Delivery](tomo_guide.md#delivery) |
| TOMO | `target_length_mm` | TL | mm | [Delivery](tomo_guide.md#delivery) |
| TOMO | `ttdf_s_cgy` | TTDF | s/cGy | [Delivery](tomo_guide.md#delivery) |
| TOMO | `mlot` | mLOT | ms | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `sdlot` | sdLOT | ms | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `mdlot` | mdLOT | ms | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `molot` | moLOT | ms | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `maxlot` | maxLOT | ms | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `minlot` | minLOT | ms | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `klot` | kLOT | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `slot` | sLOT | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `clns_10ms` | CLNS10 | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `clns_20ms` | CLNS20 | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `clns_30ms` | CLNS30 | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `clns_50ms` | CLNS50 | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `clns_pt_10ms` | CLNSpt10 | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `clns_pt_20ms` | CLNSpt20 | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `clns_pt_30ms` | CLNSpt30 | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `clns_pt_50ms` | CLNSpt50 | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `mflot` | mFLOT | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `sdflot` | sdFLOT | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `mdflot` | mdFLOT | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `moflot` | moFLOT | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `maxflot` | maxFLOT | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `minflot` | minFLOT | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `cfns_0_1` | CFNS0.1 | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `cfns_0_25` | CFNS0.25 | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `cfns_0_5` | CFNS0.5 | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `cfns_0_75` | CFNS0.75 | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `ta` | TA | leaf slots | [Sinogram geometry](tomo_guide.md#sinogram-geometry) |
| TOMO | `ncc` | nCC | count | [Sinogram geometry](tomo_guide.md#sinogram-geometry) |
| TOMO | `lengthcc` | lengthCC | leaf slots | [Sinogram geometry](tomo_guide.md#sinogram-geometry) |
| TOMO | `fdisc` | fDISC | dimensionless | [Sinogram geometry](tomo_guide.md#sinogram-geometry) |
| TOMO | `cls` | CLS | dimensionless | [Sinogram geometry](tomo_guide.md#sinogram-geometry) |
| TOMO | `clsin` | CLSin | dimensionless | [Sinogram geometry](tomo_guide.md#sinogram-geometry) |
| TOMO | `clsinarea` | CLSinarea | dimensionless | [Sinogram geometry](tomo_guide.md#sinogram-geometry) |
| TOMO | `clsindisc` | CLSindisc | dimensionless | [Sinogram geometry](tomo_guide.md#sinogram-geometry) |
| TOMO | `clsinareadisc` | CLSinareadisc | dimensionless | [Sinogram geometry](tomo_guide.md#sinogram-geometry) |
| TOMO | `centroid` | Centroid | leaf-index displacement | [Sinogram geometry](tomo_guide.md#sinogram-geometry) |
| TOMO | `l0ns` | L0NS | proportion | [Sinogram geometry](tomo_guide.md#sinogram-geometry) |
| TOMO | `l1ns` | L1NS | proportion | [Sinogram geometry](tomo_guide.md#sinogram-geometry) |
| TOMO | `l2ns` | L2NS | proportion | [Sinogram geometry](tomo_guide.md#sinogram-geometry) |
| TOMO | `lotv` | LOTV | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `elotv_1` | ELOTV-1 | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `elotv_5` | ELOTV-5 | dimensionless | [Leaf open time](tomo_guide.md#leaf-times) |
| TOMO | `pstv` | PSTV | dimensionless | [Sinogram modulation](tomo_guide.md#modulation) |
| TOMO | `epstv_1_1` | EPSTV-1,1 | dimensionless | [Sinogram modulation](tomo_guide.md#modulation) |
| TOMO | `epstv_1_0` | EPSTV-1,0 | dimensionless | [Sinogram modulation](tomo_guide.md#modulation) |
| TOMO | `epstv_0_1` | EPSTV-0,1 | dimensionless | [Sinogram modulation](tomo_guide.md#modulation) |
| TOMO | `mi` | MI | dimensionless | [Sinogram modulation](tomo_guide.md#modulation) |
| TOMO | `noc` | nOC | count | [Sinogram modulation](tomo_guide.md#modulation) |
| TOMO | `msa` | mSA | leaf-index displacement | [Sinogram modulation](tomo_guide.md#modulation) |
| TOMO | `msi` | mSI | dimensionless | [Sinogram modulation](tomo_guide.md#modulation) |
| TOMO | `mdsi` | mdSI | dimensionless | [Sinogram modulation](tomo_guide.md#modulation) |
| TOMO | `sdsi` | sdSI | dimensionless | [Sinogram modulation](tomo_guide.md#modulation) |
| CYBERKNIFE_MLC | `mcs` | MCS (CyberKnife MLC) | dimensionless | [MLC-based subset](cyberknife_guide.md#metrics) |
| CYBERKNIFE_MLC | `em` | EM | mm^-1 | [MLC-based subset](cyberknife_guide.md#metrics) |
| CYBERKNIFE_MLC | `pi` | PI | dimensionless | [MLC-based subset](cyberknife_guide.md#metrics) |
| CYBERKNIFE_MLC | `pm` | PM | dimensionless | [MLC-based subset](cyberknife_guide.md#metrics) |
| CYBERKNIFE_MLC | `lg` | LG (Mean Leaf Gap) | mm | [MLC-based subset](cyberknife_guide.md#metrics) |
| CYBERKNIFE_MLC | `sas10` | SAS10 (CyberKnife) | dimensionless | [MLC-based subset](cyberknife_guide.md#metrics) |
| AURORA | `longitudinal_travel_mm` | longitudinal_travel_mm | mm | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `total_rotation_deg` | total_rotation_deg | deg | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `rotations` | rotations | turns | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `travel_per_rotation_mm` | travel_per_rotation_mm | mm/rotation | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `projection_pitch_mean` | projection_pitch_mean | mm/deg | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `projection_pitch_cv` | projection_pitch_cv | dimensionless | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `projection_mu_density_mean_proxy` | projection_mu_density_mean_proxy | weight/mm | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `projection_mu_density_cv_proxy` | projection_mu_density_cv_proxy | dimensionless | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `projection_aperture_change_mean` | projection_aperture_change_mean | mm/mm | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `projection_aperture_change_cv` | projection_aperture_change_cv | dimensionless | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `projection_leaf_travel_mean` | projection_leaf_travel_mean | mm/mm | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `projection_leaf_travel_cv` | projection_leaf_travel_cv | dimensionless | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `projection_leaf_travel_mean_mlcx1` | projection_leaf_travel_mean_mlcx1 | mm/mm | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `projection_leaf_travel_cv_mlcx1` | projection_leaf_travel_cv_mlcx1 | dimensionless | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `projection_leaf_travel_mean_mlcx2` | projection_leaf_travel_mean_mlcx2 | mm/mm | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `projection_leaf_travel_cv_mlcx2` | projection_leaf_travel_cv_mlcx2 | dimensionless | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `theta_z_coupling_cv` | theta_z_coupling_cv | dimensionless | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `mu_z_coupling_cv_proxy` | mu_z_coupling_cv_proxy | dimensionless | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `mlc_z_coupling_cv` | mlc_z_coupling_cv | dimensionless | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `mlcx1_z_coupling_cv` | mlcx1_z_coupling_cv | dimensionless | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `mlcx2_z_coupling_cv` | mlcx2_z_coupling_cv | dimensionless | [V2 paper-style physics](aurora_guide.md#motion) |
| AURORA | `reversal_symmetry_index` | reversal_symmetry_index | dimensionless | [V3 bidirectional symmetry](aurora_guide.md#research) |
| AURORA | `forward_backward_metric_difference` | forward_backward_metric_difference | dimensionless | [V3 bidirectional symmetry](aurora_guide.md#research) |
| AURORA | `beam_pair_balance_index` | beam_pair_balance_index | dimensionless | [V3 bidirectional symmetry](aurora_guide.md#research) |
| AURORA | `small_opening_fraction` | small_opening_fraction | dimensionless | [V3 small-opening burden](aurora_guide.md#research) |
| AURORA | `near_closed_fraction` | near_closed_fraction | dimensionless | [V3 small-opening burden](aurora_guide.md#research) |
| AURORA | `effective_small_gap_burden` | effective_small_gap_burden | dimensionless | [V3 small-opening burden](aurora_guide.md#research) |
| AURORA | `projection_pitch_p95` | projection_pitch_p95 | mm/deg | [V3 local interval peaks](aurora_guide.md#research) |
| AURORA | `projection_pitch_max` | projection_pitch_max | mm/deg | [V3 local interval peaks](aurora_guide.md#research) |
| AURORA | `projection_pitch_top3_mean` | projection_pitch_top3_mean | mm/deg | [V3 local interval peaks](aurora_guide.md#research) |
| AURORA | `projection_mu_density_p95_proxy` | projection_mu_density_p95_proxy | weight/mm | [V3 local interval peaks](aurora_guide.md#research) |
| AURORA | `projection_mu_density_max_proxy` | projection_mu_density_max_proxy | weight/mm | [V3 local interval peaks](aurora_guide.md#research) |
| AURORA | `projection_mu_density_top3_mean_proxy` | projection_mu_density_top3_mean_proxy | weight/mm | [V3 local interval peaks](aurora_guide.md#research) |
| AURORA | `projection_aperture_change_p95` | projection_aperture_change_p95 | mm/mm | [V3 local interval peaks](aurora_guide.md#research) |
| AURORA | `projection_aperture_change_max` | projection_aperture_change_max | mm/mm | [V3 local interval peaks](aurora_guide.md#research) |
| AURORA | `projection_aperture_change_top3_mean` | projection_aperture_change_top3_mean | mm/mm | [V3 local interval peaks](aurora_guide.md#research) |
| AURORA | `projection_leaf_travel_p95` | projection_leaf_travel_p95 | mm/mm | [V3 local interval peaks](aurora_guide.md#research) |
| AURORA | `projection_leaf_travel_max` | projection_leaf_travel_max | mm/mm | [V3 local interval peaks](aurora_guide.md#research) |
| AURORA | `projection_leaf_travel_top3_mean` | projection_leaf_travel_top3_mean | mm/mm | [V3 local interval peaks](aurora_guide.md#research) |
| AURORA | `head_mu_density_mean_proxy` | head_mu_density_mean_proxy | weight/mm | [V3 axial regions](aurora_guide.md#research) |
| AURORA | `head_mu_density_cv_proxy` | head_mu_density_cv_proxy | dimensionless | [V3 axial regions](aurora_guide.md#research) |
| AURORA | `head_aperture_change_mean` | head_aperture_change_mean | mm/mm | [V3 axial regions](aurora_guide.md#research) |
| AURORA | `head_aperture_change_cv` | head_aperture_change_cv | dimensionless | [V3 axial regions](aurora_guide.md#research) |
| AURORA | `head_leaf_travel_mean` | head_leaf_travel_mean | mm/mm | [V3 axial regions](aurora_guide.md#research) |
| AURORA | `head_leaf_travel_cv` | head_leaf_travel_cv | dimensionless | [V3 axial regions](aurora_guide.md#research) |
| AURORA | `mid_mu_density_mean_proxy` | mid_mu_density_mean_proxy | weight/mm | [V3 axial regions](aurora_guide.md#research) |
| AURORA | `mid_mu_density_cv_proxy` | mid_mu_density_cv_proxy | dimensionless | [V3 axial regions](aurora_guide.md#research) |
| AURORA | `mid_aperture_change_mean` | mid_aperture_change_mean | mm/mm | [V3 axial regions](aurora_guide.md#research) |
| AURORA | `mid_aperture_change_cv` | mid_aperture_change_cv | dimensionless | [V3 axial regions](aurora_guide.md#research) |
| AURORA | `mid_leaf_travel_mean` | mid_leaf_travel_mean | mm/mm | [V3 axial regions](aurora_guide.md#research) |
| AURORA | `mid_leaf_travel_cv` | mid_leaf_travel_cv | dimensionless | [V3 axial regions](aurora_guide.md#research) |
| AURORA | `tail_mu_density_mean_proxy` | tail_mu_density_mean_proxy | weight/mm | [V3 axial regions](aurora_guide.md#research) |
| AURORA | `tail_mu_density_cv_proxy` | tail_mu_density_cv_proxy | dimensionless | [V3 axial regions](aurora_guide.md#research) |
| AURORA | `tail_aperture_change_mean` | tail_aperture_change_mean | mm/mm | [V3 axial regions](aurora_guide.md#research) |
| AURORA | `tail_aperture_change_cv` | tail_aperture_change_cv | dimensionless | [V3 axial regions](aurora_guide.md#research) |
| AURORA | `tail_leaf_travel_mean` | tail_leaf_travel_mean | mm/mm | [V3 axial regions](aurora_guide.md#research) |
| AURORA | `tail_leaf_travel_cv` | tail_leaf_travel_cv | dimensionless | [V3 axial regions](aurora_guide.md#research) |
| AURORA | `layer_imbalance_index` | layer_imbalance_index | dimensionless | [V3 dual-layer coordination](aurora_guide.md#research) |
| AURORA | `layer_correlation_index` | layer_correlation_index | dimensionless | [V3 dual-layer coordination](aurora_guide.md#research) |
| AURORA | `x1_x2_aperture_disparity` | x1_x2_aperture_disparity | dimensionless | [V3 dual-layer coordination](aurora_guide.md#research) |
| AURORA | `x1_x2_leaf_travel_ratio` | x1_x2_leaf_travel_ratio | dimensionless | [V3 dual-layer coordination](aurora_guide.md#research) |
| AURORA | `mean_ba` | mean_ba | mm^2 | [V4 physical aperture and adapted MCS](aurora_guide.md#aperture) |
| AURORA | `mean_bi` | mean_bi | dimensionless | [V4 physical aperture and adapted MCS](aurora_guide.md#aperture) |
| AURORA | `mean_ca` | mean_ca | mm^-1 | [V4 physical aperture and adapted MCS](aurora_guide.md#aperture) |
| AURORA | `mean_sas5` | mean_sas5 | dimensionless | [V4 physical aperture and adapted MCS](aurora_guide.md#aperture) |
| AURORA | `mean_sas10` | mean_sas10 | dimensionless | [V4 physical aperture and adapted MCS](aurora_guide.md#aperture) |
| AURORA | `mean_mcs_aurora` | mean_mcs_aurora | dimensionless | [V4 physical aperture and adapted MCS](aurora_guide.md#aperture) |
| AURORA | `mcs_complexity_aurora` | mcs_complexity_aurora | dimensionless | [V4 physical aperture and adapted MCS](aurora_guide.md#aperture) |
| AURORA | `axial_travel_mm` | axial_travel_mm | mm | [Legacy engineering](aurora_guide.md#motion) |
| AURORA | `gantry_rotation_deg` | gantry_rotation_deg | deg | [Legacy engineering](aurora_guide.md#motion) |
| AURORA | `mm_per_deg` | mm_per_deg | mm/deg | [Legacy engineering](aurora_guide.md#motion) |
| AURORA | `mm_per_rotation` | mm_per_rotation | mm/rotation | [Legacy engineering](aurora_guide.md#motion) |
| AURORA | `pitch_consistency` | pitch_consistency | dimensionless | [Legacy engineering](aurora_guide.md#motion) |
| AURORA | `mu_per_mm` | mu_per_mm | MU/mm | [Legacy engineering](aurora_guide.md#motion) |
| AURORA | `aperture_change_per_mm` | aperture_change_per_mm | mm/mm | [Legacy engineering](aurora_guide.md#motion) |
| AURORA | `leaf_travel_per_mm` | leaf_travel_per_mm | mm/mm | [Legacy engineering](aurora_guide.md#motion) |
| AURORA | `coupled_modulation_index` | coupled_modulation_index | dimensionless | [Legacy engineering](aurora_guide.md#motion) |
