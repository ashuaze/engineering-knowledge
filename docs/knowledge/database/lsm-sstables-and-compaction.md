---
id: "kb-database-lsm"
title: "LSM、SSTable 与压缩合并：写入返回后，后台为什么仍然忙"
kind: "concept"
domain: "database"
status: "evolving"
summary: "解释内存写入、不可变有序文件与多路合并，区分快照、删除标记、读写空间放大和持续写入能力。"
created: "2026-10-20"
updated: "2026-10-20"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-algorithms-sorting-boundaries", "kb-database-wal-recovery"]
related: ["kb-algorithms-page-indexes", "kb-cache-search-bloom", "kb-cache-search-eviction", "kb-database-isolation-mvcc", "kb-performance-backpressure", "kb-cache-search-inverted-index"]
tags: ["lsm", "sstable", "compaction", "write-amplification"]
---

# LSM、SSTable 与压缩合并：写入返回后，后台为什么仍然忙

学习入口：一批写入很快返回，为什么稍后读变慢、磁盘继续忙，甚至新写入开始等待？前置：[排序与合并的成本](../algorithms/sorting-binary-search-and-boundaries.md)、[WAL 与恢复](wal-and-crash-recovery.md)。本文用单机有序键值模型解释 [LSM](../../glossary/database.md#database.lsm)，产品机制对照 LevelDB 和 RocksDB 官方资料；不提供具体版本的配置建议，没有运行存储引擎。

## 把零散更新汇成有序文件

LSM 是 Log-Structured Merge 的缩写，核心思路是先积累更新，再分批写出、合并有序数据。它不是一棵必须长成二叉形状的树，也不表示磁盘上只有一份不断追加的日志。

在本文采用的常见路径中，写入先进入 [WAL](../../glossary/database.md#database.recovery-log) 和内存表 MemTable；WAL 用于恢复尚未形成稳定表文件的更新，内存表供当前读取。内存表达到条件后冻结，由后台 Flush 写成新的 SSTable，后续写入进入新内存表。RocksDB 的[架构说明](https://github.com/facebook/rocksdb/wiki/RocksDB-Overview)展示了这些组成部分；不同实现的内存表示和日志选项有差异，不能把“MemTable”固定理解为某种树。

SSTable 可理解为已排好序的键值表文件。文件完成后通常不在原位置逐项覆盖，而是生成新文件替换旧文件。LevelDB 的[表格式](https://github.com/google/leveldb/blob/main/doc/table_format.md)包含数据块、块索引和过滤器等元数据：有序文件仍可借助索引定位块，不意味着每次点查都从头读到尾。

```text
更新 → WAL + 当前内存表
                 ↓ 冻结与 Flush
             新有序表文件
                 ↓ 与选定旧文件 Compaction
             替换后的有序文件集合
```

这是概念流程，不是崩溃安全的操作清单。写入返回、日志同步、Flush 完成和合并完成是不同事件。LevelDB 的[同步写入说明](https://github.com/google/leveldb/blob/main/doc/index.md#synchronous-writes)规定：默认异步写在数据交给操作系统后返回，尚未承诺已进入持久介质，机器崩溃可能丢失近期更新；sync=true 则要求在返回前完成相应持久化同步，仍依赖其文件系统、存储设备及同步接口兑现语义。这个同步边界针对日志等写入，不要求先完成 SSTable Flush 或合并；仅看到值已在内存可读，也不能断言已满足断电持久性要求。

## 查一个键，也要确定可见版本

内存表与多个文件可能都包含同一个用户键的不同版本。下面自设键按 ASCII 升序，序列号唯一且递增，表示本模型的更新顺序，不是墙上时钟；所有操作已成功进入模型，不讨论事务、Merge 操作或[并发](../../glossary/systems.md#systems.concurrency)发布。

| 所在位置 | 按键列出的内容 |
| --- | --- |
| 旧文件 T1 | a@1=A1，b@2=B1 |
| 新文件 T2 | a@3=A2，b@4=删除标记 |
| 当前内存表 | c@5=C1 |

本例读取视图 S，只选择序列号不大于 S 的最新版本：S=5 时，a 返回 A2，b 不存在，c 返回 C1；保留的 S=2 快照则看到 A1、B1，看不到 c。找到旧文件里的 a，不代表可以立即返回 A1；遇到当前可见的 b 删除标记，也不能继续用更旧的 B1 填回结果。

点查可先排除键范围不相交的文件，再利用文件内索引与过滤器定位。范围扫描还需合并多条有序流、选择可见版本并处理删除，不能把某个文件的排序结果直接当作整个数据库的结果。具体文件集合与层级组织参照 [LevelDB 实现说明](https://github.com/google/leveldb/blob/main/doc/impl.md)；经典 LevelDB 中 L0 文件范围可重叠，后续各层文件范围不重叠，这不是所有 LSM 变体都必须采用的形状。

[Bloom Filter](../cache-search/bloom-filters-membership-and-synchronization.md)可以省去部分不必要的点查：在过滤器完整覆盖对应文件、编码与查询规则一致等前提下，阴性可排除相应文件中的该键；仍需检查其他候选文件与内存表。阳性还需核对，某个文件的阴性不表示整个数据库没有该键。过滤器不能替代跨文件版本选择，更不能直接跳过范围内全部结果。

## 合并可以回收旧数据，但不能让删除复活

Compaction 读取选定有序文件，按键和版本归并，写出新的文件集合，同时在安全条件下丢弃旧版本。这里常译作“压缩合并”；它与 Snappy、Zstd 等字节压缩不同，即使不用字节压缩，也可能需要 Compaction。

继续本例：若 S=2 快照仍有效，合并 T1、T2 不能仅保留 a@3 与 b@4，否则旧视图失去 A1、B1。[RocksDB Snapshot](https://github.com/facebook/rocksdb/wiki/Snapshot)说明 Flush/Compaction 会考虑快照并保留相应可见数据。快照对象不必复制一份完整数据库，但可能延长旧版本的保留时间。

若已无旧视图需要相关版本，且本次处理已覆盖 b 的全部更旧值、没有其他位置还需被屏蔽，则可同时去掉 B1 和删除标记。若只合并含 b@4 的新文件，却留下含 B1 的旧文件，提前丢掉删除标记会让 B1 再次被读到。逻辑删除成功、删除标记可回收与旧字节实际清理不是同一时刻，备份副本另有生命周期。

输出文件完成后，还需一致地发布新的有效文件集合，再在没有读者依赖等条件下回收旧文件。LevelDB 用 MANIFEST 记录文件集合等元数据；只写出一个新 SSTable 不能证明它已经安全替代旧集合，更不是完整备份与恢复协议。

## 写入成本被重排，不会消失

| 成本 | 要明确的口径 |
| --- | --- |
| 写放大 | 存储层实际写出字节相对应用逻辑写入字节；是否计入 WAL、元数据与压缩需注明 |
| 读放大 | 一次逻辑读取还要检查多少文件、块或字节；这些单位不能混用 |
| 空间放大 | 当前及临时存储相对逻辑有效数据的额外占用；快照、旧版本和合并输出都可能参与 |

纸面例：应用逻辑写入 100 字节，若仅计 SSTable 的 Flush 与后续合并总共写出 400 字节，该口径的写放大为 4。假定不启用字节压缩，400 字节已含表内数据、索引等元数据，但不含 WAL、文件系统元数据或设备内部写入；这些数值不是实测。合并期间新旧文件可能暂时共存，不能仅按最终有效数据大小规划可用空间。

Leveled 通常用更多重写换取较少重叠和空间占用，Tiered/Universal 可减少某些重写，却可能保留更多有序段，增加读与临时空间成本。具体差异与例外见 [RocksDB Compaction](https://github.com/facebook/rocksdb/wiki/Compaction)；不能据此宣称某策略或 LSM 总比 [B+ 树](../algorithms/b-trees-bplus-trees-and-page-indexes.md)快。

## 持续写入还受后台处理能力约束

短时突发可以被内存与待合并文件吸收，长期写入超过 Flush/合并处理能力则会积压。RocksDB 的 [Write Stalls](https://github.com/facebook/rocksdb/wiki/Write-Stalls)说明内存表、L0 文件和待合并工作过多时可能减速或停写。后台[线程](../../glossary/systems.md#systems.execution-units)也会与前台争用 CPU、I/O 和缓存，“放到后台”不等于免费。

排查应把请求[延迟](../../glossary/performance.md#performance.latency-throughput)与各层文件、待合并字节、Flush 等待、停写时间及实际 I/O 放在同一时间段观察。单看前几秒接收吞吐，不能证明持续吞吐或[尾延迟](../../glossary/performance.md#performance.percentiles)；盲目增大缓存、线程和触发阈值也可能只是推迟[背压](../performance/backpressure-and-bounded-queues.md)。

自检：返回成功对应哪种持久性？同键多个版本怎样选？删除标记还在屏蔽哪些旧值？合并需要多大临时空间？测量写放大时计入了哪一层？

2026-10-20 核查 LevelDB main 文档及 RocksDB 官方 Wiki 的架构、合并、快照和停写机制，状态为 source-checked；未将文档默认值当作通用配置。序列、读结果及字节比为纸面推演；未执行 WAL 同步、Flush、快照回收、删除合并、崩溃恢复或性能实验。
