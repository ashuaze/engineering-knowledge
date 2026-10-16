<!-- GENERATED: edit data/*.json or article frontmatter, then run scripts/generate_indexes.py -->

# 计算机系统与操作系统

建议优先级：P0。目标：解释进程、内存、同步与 I/O，定位资源等待。

下方术语用于知识索引。建议从[实际工程问题](../../problems.md)或本页核心问题进入，结合已有正文理解机制、适用边界与相关概念。

## 一个核心问题

一个服务为何 CPU 不高，却不再处理请求？

## 已有正文

- [进程、线程与协程：资源边界和执行调度如何分工](process-thread-coroutine.md)：区分资源隔离、执行线程与可挂起任务，解释并发为什么不自动带来并行。

## 术语范围

| 术语 | 简释 |
| --- | --- |
| Process / Thread / Coroutine | 进程、线程与协程，资源、执行和调度边界。 |
| Concurrency / Parallelism | 并发推进与并行执行，关注调度和硬件资源。 |
| Blocking / Non-blocking | 指定操作会不会让当前执行线程等待。 |
| Context Switch | 保存和恢复执行上下文及其开销。 |
| User Mode / Kernel Mode / Syscall | 权限边界、系统调用和内核服务。 |
| Stack / Heap | 调用栈、动态分配和对象生命周期。 |
| Virtual Memory / Paging | 地址映射、分页和缺页处理。 |
| Mutex / Semaphore / CAS | 互斥、资源计数与原子比较交换。 |
| Race Condition / Deadlock | 时序依赖错误与循环等待。 |
| File Descriptor / Socket | 操作系统资源句柄与通信端点。 |
| I/O Multiplexing / epoll | 监视多个 I/O 就绪事件，减少逐连接阻塞等待。 |
| Memory Model / Happens-before | 跨执行单元的可见性、顺序与同步关系。 |

## 练习与验收

选择上面的一个核心问题，先画执行过程或数据边界，再构造一个正常路径和一个失败路径。用原理解释、架构或代码、诊断证据和取舍依据说明保证范围；记录已完成验证与待验证项。

[回到知识地图](../../map.md) · [问题导航](../../problems.md) · [学习路径](../../paths/index.md)
