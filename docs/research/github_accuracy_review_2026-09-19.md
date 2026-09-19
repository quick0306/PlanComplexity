# 用 GitHub 资源提高 PlanComplexity 科学性与准确性

核查日期：2026-09-19。范围：9 个相关 GitHub 仓库、UCoMX 官方发布页、关键源码和官方文档；其中 8 个仓库记录了固定提交，30 个下载成功的源码/文档文件记录了 SHA256。完整记录见同目录 `github_accuracy_review_2026-09-19.json`。

结论：下一步优先补齐 TOMO 计划床运动读取和可追溯的外部数值验证，再扩展指标。GitHub 实现用于交叉核对；指标同名、代码同源、两种语言结果相同，都不足以证明物理量正确。本轮完成检索、源码核对和最小数值复现，未修改计算实现、依赖或已冻结的基准。

## 值得采用的资源与边界

| 资源 | 可提取的内容 | 对本项目的用途与限制 |
| --- | --- | --- |
| [SamueleCavinato/TCoMX](https://github.com/SamueleCavinato/TCoMX) | TOMO MATLAB 指标函数、TPS 分支、18 个作者标注匿名的参考计划 | 优先核对 LOT、投影、床运动与剂量分次语义。GitHub v1.0 已声明停止维护，必须标明历史版本，不能代表当前 UCoMX。 |
| [UCoMX v1.1 官方发布](https://zenodo.org/records/15673571) | 手册、参考数据、正式输出；v1.1 更新 TG 和 MRIdian 叶片存储模式处理 | 优先作为固定版本的外部运行参照。发布的是 MATLAB pcode/编译程序，源码不可见，不能把它当成可移植的开源算法库。 |
| [umro/Complexity](https://github.com/umro/Complexity)、[victorgabr/ApertureComplexity](https://github.com/victorgabr/ApertureComplexity)、[Jothy/ComplexityCalc](https://github.com/Jothy/ComplexityCalc) | Younge 孔径复杂度来源、Python 移植、测试结构 | 用于追溯边缘复杂度定义和历史实现。三者存在明确来源关系，不能算三份独立验证证据。 |
| [MAAS-PlanComplexity](https://github.com/Varian-MedicalAffairsAppliedSolutions/MAAS-PlanComplexity) | Eclipse ESAPI 的面积、BI、BM 和叶对开口计算 | 适合核对特定 C-arm 机型。README 排除 Halcyon；源码有固定 60 对叶片、机型宽度表和最小动态间隙门槛，面积函数未显式裁剪 jaws，不能直接作为所有本项目指标的真值。 |
| [PyMedPhys](https://github.com/pymedphys/pymedphys) | MetersetMap、DICOM/日志交付数据接口与测试 | 适合建立 MU—MLC—jaw 的独立几何投影检查。`_experimental/plancomplexity` 明示主要在 Pinnacle 上测试，不能把整个库的成熟度等同于该实验模块已获跨 TPS 验证。 |
| [rt-complexity-lens](https://github.com/matteomaspero/rt-complexity-lens) | 逐控制点检查、公式文档、差异报告和跨实现审计结构 | 借鉴透明报告。其归档审计中 TS/Python 一致，但 UCoMX 层被跳过；与本项目存在明确公式差异，需逐指标比较。 |
| [pylinac](https://github.com/jrkerns/pylinac) | 合成 QA RTPLAN、Halcyon 计划生成及测试 | 适合生成可公开运行的测试计划。官方 fluence 文档明确忽略 jaws 和准直器旋转，不适合直接验证本项目已裁剪的物理孔径。 |
| [PlanDeliverySimulator](https://github.com/Varian-MedicalAffairsAppliedSolutions/PlanDeliverySimulator) | 交付动画、机器速度约束、模拟时间的表达 | 可借鉴诊断界面。作者说明其 MCSv 使用简化 LSV 惩罚并加入准直器旋转项，不是可直接替代的文献 MCSv 标准答案。 |

PyMedPhys 的坐标约定为等中心面毫米和双极叶片/准直器位置，接入前需做显式转换，而不能直接传入本项目数组。参见其 [MetersetMap 官方 API](https://docs.pymedphys.com/en/latest/users/ref/lib/metersetmap.html)。pylinac 的限制见 [官方 fluence 文档](https://pylinac.readthedocs.io/en/latest/topics/fluence.html)。

固定提交记录如下，均指检索时默认分支的快照，不等同于稳定发行版：

| 仓库 | 提交前缀 | 提交日期 |
| --- | --- | --- |
| TCoMX | `ac8f28e4068f` | 2024-08-27 |
| rt-complexity-lens | `ece2965ea81d` | 2026-09-04 |
| MAAS-PlanComplexity | `57132954f728` | 2026-02-03 |
| PyMedPhys | `98c800132c4a` | 2026-09-16 |
| ComplexityCalc | `1b1fd69ab243` | 2021-12-22 |
| ApertureComplexity | `fbb25e756dd2` | 2023-05-01 |
| umro/Complexity | `76aaeb550a04` | 2017-10-12 |
| PlanDeliverySimulator | `dcf247e7ac09` | 2026-02-23 |

复用方式需区别对待：TCoMX 与 Complexity 系列声明 GPL-3.0；PyMedPhys 为 Apache-2.0；rt-complexity-lens 根目录 LICENSE 为 CC BY-NC-SA 4.0；两个 Varian 仓库使用各自的 Limited Use 协议。本轮只做来源与公式分析，没有将上游实现移入项目。

## 已复现的新问题：TOMO 床运动

`tomo_parser.py:253` 目前先读标准床纵向位置；缺失时尝试用 pitch 推导。但 `_infer_pitch` 未读取已有的 `TOMO_HA_01` 私有 pitch，床移动距离会返回 0，之后才应用默认 pitch 0.287。两个本地参考案例因此报告 0 床速、0 床移动距离，以及 -25.1 mm 的 `target_length_mm`。

TCoMX 的 [Hi-Art 读取分支](https://github.com/SamueleCavinato/TCoMX/blob/ac8f28e4068fac0c883bd409dd8cc464593ea351/libs/01_read-input/TCoMX_read_RTplan.m#L209-L222) 读取床速 `(300D,1080)` 与 pitch `(300D,1060)`，再计算计划床移动距离。Accuray 官方文档索引同样将床速定义为 mm/s，pitch 定义为每转前进距离除以 Y 方向开口宽度。

| 案例别名 | 现有距离 mm | 计划床速 mm/s | 已核对治疗时间 s | 床速 × 时间得到的距离 mm |
| --- | ---: | ---: | ---: | ---: |
| tomo_canonical | 0 | 0.610483 | 365.568627451 | 223.173432392 |
| tomo_default_inference_edge | 0 | 0.238533 | 412.733333333 | 98.450520200 |

两例原始 pitch 均为 0.287。交叉检查 `床速 × 机架周期 / pitch` 分别得到 25.099998 与 25.099988 mm，与现有 jaw 宽度 25.1 mm 相符。这是独立的物理量闭合检查。上述距离代表**计划运动**，不代表测量或实际交付轨迹。

建议优先修复该读取路径：验证 private creator 与有限数值，区分螺旋/固定角度和不同 TPS；字段缺失时保留不可用状态。随后补充手算用例、更新 TOMO 公式版本并迁移受影响基准。RayStation 分支还涉及不同床坐标与私有字段，应单独核查，不能把 Hi-Art 规则直接推广过去。

单位证据：[Accuray 1066787 Rev. A，p84](https://www.accuray.com/wp-content/uploads/1066787.pdf) 与 [1025620 Rev. B，p98](https://www.accuray.com/wp-content/uploads/tt-dicom-statement-pn-1025620.pdf) 的官方域名索引摘要。直接 PDF 请求返回 404；这一获取限制保留在机器可读记录中。源码与字段数值闭合检查提供了另外两条证据，但没有据此声称完成全部厂商格式验证。

## 同名指标的两个最小反例

对照本项目当前源码与固定提交的 [rt-complexity-lens metrics.py](https://github.com/matteomaspero/rt-complexity-lens/blob/ece2965ea81d05f935087edce4d3556e3ed6a291/python/rtplan_complexity/metrics.py)：

| 手算输入 | 本项目定义 | 对方实现 | 含义 |
| --- | ---: | ---: | --- |
| 单叶库位置 `[0,1,2]`，全部有效 | LSV 以位置极差 2 归一，结果 0.5 | 以最大相邻差 1 归一，结果 0 | 不能按 `LSV` 同名设置精确等价 |
| 20 × 5 mm 矩形，面积 100、完整周长 50 | 叶片侧边长度/面积 = 40/100 = 0.4 mm⁻¹ | 完整周长/(2×面积) = 50/200 = 0.25 mm⁻¹ | 正方形用例可能碰巧相同，应加长方形反例 |

这些结果已在本地复算；它们证明定义不一致，并不单独裁定哪种定义符合某篇论文。现有公式应先与目标论文逐项核对，再决定新增具名变体或标为不可直接比较。

对方 [2026-07-25 审计报告](https://github.com/matteomaspero/rt-complexity-lens/blob/ece2965ea81d05f935087edce4d3556e3ed6a291/python/tests/reference_data/AUDIT_REPORT.md) 已明确区分内部语言一致性、与 ApertureComplexity 的定义差异，以及未运行的 UCoMX 层。该报告还早于本次固定的 9 月源码，不能当作本项目或其当前代码的外部验证结论。

## 本项目的改进优先级

| 顺序 | 具体改动 | 验收依据 |
| --- | --- | --- |
| 1 | 修复 TOMO 计划床速、距离与 pitch；区分已知值、推导值、假设值和不可用值 | 上表两例复算；床速×周期/pitch 的宽度闭合；缺失/非法 creator 和固定角度反例 |
| 2 | 建立真实外部输出证据包 | 固定工具版本、源数据标识、运行配置、原始输出校验和；每个数值能追溯到一次外部运行 |
| 3 | 为 MCS、AAV、LSV、EM、SAS 建立逐指标公式契约 | 写明原始文献、CP/控制弧定义、叶片筛选、归一化、jaw 规则、MU 权重、单位与实现版本；上述反例进入测试 |
| 4 | 计算和验证保留全精度，显示时再舍入 | 当前 `vcomx_vmat_metrics.py:410` 等路径提前舍入两位；比较未舍入中间量，保留兼容的显示输出 |
| 5 | 扩展独立几何与端到端测试 | PyMedPhys 检查 MU/MLC/jaw 投影；pylinac 生成合成输入；覆盖非均匀叶宽、闭合、移动 jaws、零 MU 与双层交集 |
| 6 | 最后评价复杂度与 QA 的关联 | 使用独立 QA 终点，按机型/TPS/技术分层；按患者或计划分组验证，防止同源计划泄漏；不能从单个复杂度值直接推出可交付性 |

目前 `validation/specs/comparator_mapping.yaml` 仅有 3 条映射，其中两条可作数值比较，且各只有 1 个样本；记录没有外部工具版本、原始输出哈希与运行配置。现有 `269` 项精确比较通过说明版本化回归一致性，不能据此宣称已获得 `269` 项独立外部验证。新增证据应扩充来源，而不是用当前程序重新生成所谓外部真值。

建议第一批外部比较先覆盖 PA/PI、指定定义的 EM、MCS/AAV/LSV 和 TOMO LOT/计划运动。先检查单位和每控制点中间量，再比较束和计划汇总；只有定义已对齐的指标才进入精确误差门槛。公开参考计划按来源去重，同源移植只计一个算法来源。

## 核查边界

- 本轮没有执行 MATLAB、ESAPI 或上游整套软件，因此没有新增跨软件一致性通过率。
- pylinac 核对了官方 3.48.0 文档；GitHub API 限流导致未固定其当前提交，暂不作为已锁定的运行依赖。
- 外部文件读取失败项没有计入源码证据；完整成功文件列表、固定提交和本地数值检查保存在伴随 JSON。
- 现有原始 DICOM 和上一轮基准保持原状；本轮发现的缺陷尚需按上述顺序实施修复。
