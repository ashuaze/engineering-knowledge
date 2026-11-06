<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 性能与容量词汇表

本页解释 15 组术语，按[完整术语索引](../glossary.md#performance)中的顺序排列。示例为说明性场景；具体技术版本与验证范围见各条深入阅读。

[分类词汇表](index.md) · [性能与容量文章](../knowledge/performance/index.md)

## 本页术语

- [Latency / Throughput](#performance.latency-throughput)
- [QPS / RPS / TPS](#performance.rates)
- [P50 / P95 / P99](#performance.percentiles)
- [CPU-bound / I/O-bound](#performance.bound)
- [Little’s Law](#performance.little)
- [Profiling / Flame Graph](#performance.profiling)
- [Load / Stress / Soak Test](#performance.load-tests)
- [Horizontal / Vertical Scaling](#performance.scaling)
- [Batching / Pipelining](#performance.batching)
- [Rate Limiting / Load Shedding](#performance.overload)
- [Hotspot / Contention](#performance.contention)
- [Queueing / Backpressure](#performance.queueing)
- [Capacity Planning](#performance.capacity)
- [CPU Time / Utilization / Load Average](#performance.cpu-metrics)
- [Benchmark / Speedup / Amdahl’s Law](#performance.benchmark)

<a id="performance.latency-throughput"></a>

## Latency / Throughput

**ID：** `performance.latency-throughput` · **建议优先级：** P0

**别名 / 检索词：** Latency、Throughput、延迟、吞吐量

**简释：** 完成一次操作的时间与单位时间处理量。

延迟是一次工作从规定起点到终点的耗时，吞吐量是单位时间完成的数量。边界、负载与成功口径必须一致，高吞吐不意味着尾延迟低。

**例子：** 并发增加后每秒完成量不再增长，而排队延迟仍可能持续上升。

**深入阅读：** [延迟、吞吐与排队：为什么请求更多却没有更快](../knowledge/performance/latency-throughput-and-queues.md)

<a id="performance.rates"></a>

## QPS / RPS / TPS

**ID：** `performance.rates` · **建议优先级：** P0

**别名 / 检索词：** QPS、RPS、TPS、请求速率、事务速率

**简释：** 查询、请求和事务速率，须写清计数口径。

QPS、RPS、TPS 分别常用于查询、请求、事务的每秒速率，但各团队定义可能不同。一次请求可含多次查询或事务，比较前需统一计数对象。

**例子：** 每秒一千个 API 请求若各查三次数据库，不能直接当作一千数据库 QPS。

**深入阅读：** [延迟、吞吐与排队：为什么请求更多却没有更快](../knowledge/performance/latency-throughput-and-queues.md)

<a id="performance.percentiles"></a>

## P50 / P95 / P99

**ID：** `performance.percentiles` · **建议优先级：** P0

**别名 / 检索词：** P50、P95、P99、分位数、尾延迟

**简释：** 观测窗口内延迟分布的分位数。

P95 表示样本中约 95% 不超过该值，其他分位数类似。窗口、样本和聚合方式决定意义，各实例分位数不能简单求平均得到全局分位数。

**例子：** 平均延迟不变时，少数请求恶化仍可能使 P99 明显上升。

**深入阅读：** [延迟、吞吐与排队：为什么请求更多却没有更快](../knowledge/performance/latency-throughput-and-queues.md)

<a id="performance.bound"></a>

## CPU-bound / I/O-bound

**ID：** `performance.bound` · **建议优先级：** P0

**别名 / 检索词：** CPU-bound、I/O-bound、计算密集、I/O 密集

**简释：** 描述当前主要受计算或 I/O 等资源约束的工作，需结合运行与等待证据，不能靠固定利用率阈值分类。

CPU-bound 和 I/O-bound 描述当前负载的主要限制因素，需用执行时间、等待和资源证据判断。约束会随输入、并发和资源配额变化。

**例子：** 线程等磁盘时利用率可能低；受 CPU 配额限制时也可能出现长调度等待。

**深入阅读：** [CPU 利用率、负载与配额：主机还有空闲，请求为什么仍在等](../knowledge/performance/cpu-time-utilization-load-and-quotas.md)

<a id="performance.little"></a>

## Little’s Law

**ID：** `performance.little` · **建议优先级：** P0

**别名 / 检索词：** Little’s Law、利特尔定律

**简释：** 稳定系统中平均在途量、到达率和停留时间的关系。

Little 定律用 L = λW 关联稳定系统内平均在途量、平均有效到达率与平均停留时间。三者必须采用同一边界与群体，持续增长的积压不能直接当稳态估计。

**例子：** 平均每秒进入 100 个请求、停留 0.2 秒，满足前提时平均在途约 20 个。

**深入阅读：** [延迟、吞吐与排队：为什么请求更多却没有更快](../knowledge/performance/latency-throughput-and-queues.md)

<a id="performance.profiling"></a>

## Profiling / Flame Graph

**ID：** `performance.profiling` · **建议优先级：** P0

**别名 / 检索词：** Profiling、Flame Graph、性能剖析、火焰图、on-CPU、off-CPU、Inclusive Time、Self Time

**简释：** 把所选事件和资源权重归到代码或调用栈，区分聚合宽度、执行时间线、累计/自身及运行/等待范围。

Profiling 把采样事件或计量权重归到代码和调用栈；火焰图宽度表示选定权重的聚合量。需区分 on-CPU 与 off-CPU、自身与累计，横向位置通常不是时间线。

**例子：** 锁等待不在 CPU 样本里显著，并不意味着它对端到端延迟无影响。

**深入阅读：** [Profiling 与火焰图：最宽的函数，为什么未必是延迟根因](../knowledge/performance/profiling-stacks-and-flame-graphs.md)

<a id="performance.load-tests"></a>

## Load / Stress / Soak Test

**ID：** `performance.load-tests` · **建议优先级：** P0

**别名 / 检索词：** Load、Stress、Soak Test、负载测试、压力测试、耐久测试

**简释：** 分别观察目标负载、超限失效和持续退化；需说明请求发起方式、正确性、尾延迟及资源边界。

负载测试观察目标流量，压力测试探索超限行为，耐久测试观察长时间退化。要同时检查正确性、发压方式、完成率、尾延迟与资源，而非只报峰值。

**例子：** 持续运行数小时才能暴露连接泄漏，短促峰值测试可能看不到。

**深入阅读：** [基准测试与加速比：局部快四倍，整体为什么只快一点](../knowledge/performance/benchmarks-workloads-and-speedup.md)

<a id="performance.scaling"></a>

## Horizontal / Vertical Scaling

**ID：** `performance.scaling` · **建议优先级：** P0

**别名 / 检索词：** Horizontal、Vertical Scaling、水平扩容、垂直扩容

**简释：** 增加实例与提升单实例资源。

水平扩容增加实例，垂直扩容增加单实例资源。共享瓶颈、数据分布和协调成本限制收益；状态迁移与故障恢复也影响扩容效果。

**例子：** 应用实例翻倍而数据库仍饱和时，请求吞吐未必翻倍。

**深入阅读：** [容量规划与自动扩缩容：副本增加为什么不等于能力立即增加](../knowledge/performance/capacity-planning-scaling-and-autoscaling-feedback.md)

<a id="performance.batching"></a>

## Batching / Pipelining

**ID：** `performance.batching` · **建议优先级：** P0

**别名 / 检索词：** Batching、Pipelining、批处理、流水线

**简释：** 合并操作和重叠多个执行阶段。

Batching 合并多个操作以分摊固定成本，Pipelining 让不同操作或阶段重叠推进。二者都可能增加在途量，批大小与等待时间需共同约束。

**例子：** 批量写入减少往返，但等待凑批会增加低流量时单请求延迟。

**深入阅读：** [批处理与流水线：减少往返为什么可能增加单项等待](../knowledge/performance/batching-pipelining-and-amortized-waiting.md)

<a id="performance.overload"></a>

## Rate Limiting / Load Shedding

**ID：** `performance.overload` · **建议优先级：** P0

**别名 / 检索词：** Rate Limiting、Load Shedding、负载丢弃

**简释：** 约束进入速率和过载时拒绝工作。

限流限制进入速度，负载丢弃在容量不足时拒绝部分工作。拒绝位置应尽量靠前，并结合优先级、重试提示和总预算控制放大。

**例子：** 队列已满时及时拒绝低优先级请求，可保留容量处理已接受工作。

**深入阅读：** [延迟、吞吐与排队：为什么请求更多却没有更快](../knowledge/performance/latency-throughput-and-queues.md) · [限流、并发限制与配额：分别在限制什么](../knowledge/api/rate-limits-concurrency-and-quotas.md) · [过载控制实验：排队、拒绝与取消的实际边界](../knowledge/performance/overload-control-lab.md)

<a id="performance.contention"></a>

## Hotspot / Contention

**ID：** `performance.contention` · **建议优先级：** P0

**别名 / 检索词：** Hotspot、Contention、热点、资源竞争

**简释：** 局部集中访问与共享资源竞争。

热点是访问集中到局部键或分片，竞争是多个执行者争用有限资源。增加并发可能提高锁等待或一致性开销，需要识别串行点及其所有者。

**例子：** 所有请求更新同一个计数行时，增加工作线程可能只增加排队。

**深入阅读：** [热点与资源竞争：整体不忙为什么局部已经过载](../knowledge/performance/hotspots-contention-and-serialized-service.md)

<a id="performance.queueing"></a>

## Queueing / Backpressure

**ID：** `performance.queueing` · **建议优先级：** P0

**别名 / 检索词：** Queueing、Backpressure、排队、背压

**简释：** 等待队列形成和压力反馈。

排队暂存尚不能执行的工作，背压把压力传回上游。队列应限制容量和等待时间，取消还需传到执行端；无限积压会把过载转换为高延迟和内存消耗。

**例子：** 下游变慢时限制在途请求，并让超期任务退出队列。

**深入阅读：** [慢 API 排查：把执行时间与排队时间分开](../knowledge/performance/slow-api-investigation.md) · [延迟、吞吐与排队：为什么请求更多却没有更快](../knowledge/performance/latency-throughput-and-queues.md) · [背压与有界队列：把等待放在哪里](../knowledge/performance/backpressure-and-bounded-queues.md) · [过载控制实验：排队、拒绝与取消的实际边界](../knowledge/performance/overload-control-lab.md) · [TCP 流量控制与拥塞控制：发送变慢到底受谁限制](../knowledge/networking/tcp-flow-control-and-congestion.md)

<a id="performance.capacity"></a>

## Capacity Planning

**ID：** `performance.capacity` · **建议优先级：** P0

**别名 / 检索词：** Capacity Planning、容量规划

**简释：** 用工作负载、资源余量和增长预估容量。

容量规划根据负载构成、增长、资源瓶颈和故障余量估算可持续服务能力。需要在目标延迟与正确性要求下测量，而非仅外推平均 CPU。

**例子：** 规划单区故障后剩余实例仍能承载目标流量的容量。

**深入阅读：** [容量规划与自动扩缩容：副本增加为什么不等于能力立即增加](../knowledge/performance/capacity-planning-scaling-and-autoscaling-feedback.md)

<a id="performance.cpu-metrics"></a>

## CPU Time / Utilization / Load Average

**ID：** `performance.cpu-metrics` · **建议优先级：** P0

**别名 / 检索词：** CPU 时间、CPU 利用率、负载均值、调度等待、cpu.max、PSI、CPU Throttling

**简释：** 按范围、时间窗口和分母解释执行、利用率、平滑负载、组带宽与资源停顿，不能直接换算成慢请求比例。

CPU 时间累计实际执行消耗，利用率是相对指定容量的比例，Linux Load Average 还包含特定等待任务。cgroup 配额和 PSI 分别提供带宽限制与停顿证据。

**例子：** 容器 CPU 百分比必须说明分母是单核、宿主机还是分配配额。

**深入阅读：** [CPU 利用率、负载与配额：主机还有空闲，请求为什么仍在等](../knowledge/performance/cpu-time-utilization-load-and-quotas.md)

<a id="performance.benchmark"></a>

## Benchmark / Speedup / Amdahl’s Law

**ID：** `performance.benchmark` · **建议优先级：** P1

**别名 / 检索词：** 基准测试、微基准、预热、加速比、Amdahl、阿姆达尔定律

**简释：** 固定工作契约、测量边界和负载比较成本，用明确假设下的局部时间占比解释整体收益与上限。

基准测试固定工作契约与测量条件比较成本，加速比需说明基线。Amdahl 定律在固定工作量等假设下用可优化占比限制整体收益，不能直接当实际容量预测。

**例子：** 占总时间一半的步骤加速两倍，理想整体加速约为 1.33 倍。

**深入阅读：** [基准测试与加速比：局部快四倍，整体为什么只快一点](../knowledge/performance/benchmarks-workloads-and-speedup.md)

## 资料与延伸

下列资料提供相关机制的进一步说明，并不表示覆盖本页所有术语。各条已关联的专题文章另列具体来源、适用版本与验证边界。

- [Google SRE：容量、过载与性能工程](https://sre.google/sre-book/table-of-contents/)
- [Redis pipelining](https://redis.io/docs/latest/develop/using-commands/pipelining/)
- [PostgreSQL 18 pipeline mode](https://www.postgresql.org/docs/18/libpq-pipeline-mode.html)
- [Google SRE Handling Overload](https://sre.google/sre-book/handling-overload/)
- [USE Method](https://www.brendangregg.com/usemethod.html)
- [Linux lockstat](https://docs.kernel.org/locking/lockstat.html)
- [Linux False Sharing](https://docs.kernel.org/kernel-hacking/false-sharing.html)
- [Kubernetes v1.36 HPA](https://v1-36.docs.kubernetes.io/docs/concepts/workloads/autoscaling/horizontal-pod-autoscale/)
- [Pod 生命周期](https://v1-36.docs.kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/)

[返回分类词汇表](index.md) · [完整术语索引](../glossary.md)
