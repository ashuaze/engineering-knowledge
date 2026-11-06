---
id: "kb-algorithms-trie"
title: "Trie 与前缀检索：路径存在，为什么不等于键存在"
kind: "concept"
domain: "algorithms"
status: "evolving"
summary: "区分完整键、前缀枚举与最长前缀匹配，解释终止标记、字符编码、路径压缩、输出成本与删除责任。"
created: "2026-10-20"
updated: "2026-10-23"
last_verified: "2026-10-20"
verification: "source-checked"
prerequisites: ["kb-algorithms-trees-heaps", "kb-algorithms-hash-tables"]
related: ["kb-algorithms-page-indexes", "kb-algorithms-sorting-boundaries", "kb-cache-search-bloom", "kb-cache-search-eviction", "kb-algorithms-string-matching"]
tags: ["trie", "prefix-search", "radix-tree", "key-encoding"]
---

# Trie 与前缀检索：路径存在，为什么不等于键存在

学习入口：能沿着字符走到某个节点，就能断言这个词已收录吗？前置：[树的路径](trees-heaps-and-priority-queues.md)、[键身份](hash-tables-collisions-and-key-contracts.md)。本文用有限 ASCII 字符串集合解释 [Trie](../../glossary/algorithms.md#algorithms.trees)，不运行索引或自动补全服务；Unicode 和压缩结构仅说明必须补齐的契约。

## 路径复用共同前缀

Trie 按键的字符、字节或位等单位分支，共同前缀复用共同路径；节点或边上的标签组合成键的一部分。它不靠对整个键反复比较来缩小左右区间，机制见 [NIST Trie](https://xlinux.nist.gov/dads/HTML/trie.html)与 [CMU 索引讲义](https://15445.courses.cs.cmu.edu/fall2024/notes/09-indexes2.pdf)。

本例以一个 ASCII 字符为一步，保存 car、cart、cat，星号表示“完整键在此结束”，不是字符本身：

```text
根 → c → a ─┬→ r* → t*
             └→ t*
```

ca 的路径存在，但 a 后没有终止标记，因此 ca 不是已存键。car 既是完整键，又是 cart 的前缀；不能只把没有孩子的节点当作词尾。若允许空字符串，还要单独规定根的终止标记；本例不存空键。

## 三种查询要不同答案

| 查询 | 含义 | 本例结果 |
| --- | --- | --- |
| 完整键查找 ca | ca 本身是否被收录 | 否 |
| 枚举前缀 ca | 哪些已存键以 ca 开头 | car、cart、cat |
| 查询 carton 的最长已存前缀 | 哪个完整键是 carton 的最长开头 | cart |

最长前缀匹配沿查询继续前进，同时记住最近遇到的终止位置；不能把最长匹配路径当作最长已存键。若查询为 cabin，共同路径 ca 仍不是终止键，本例没有已存前缀。不同接口的定义也可参照 [Princeton TrieST](https://algs4.cs.princeton.edu/code/javadoc/edu/princeton/cs/algs4/TrieST.html)；其示例实现限定扩展 ASCII，不是任意 Unicode 文本的通用实现。

前缀枚举不等于按相关性排名、模糊匹配或语义检索。要按字典序输出，还要按约定的符号顺序遍历孩子；哈希映射孩子的任意迭代顺序不能自动给出目标[排序](../../glossary/algorithms.md#algorithms.sorting-search)，语言的字节顺序也未必符合用户的语言排序规则。

## 长度和输出规模都要计入

若每步孩子定位为有界成本，长度为 L 的完整键查找可分析为 O(L)，不表示与键长度无关的 O(1)。孩子若用哈希映射，其相应定位成本带有预期假设；若用别的结构，需计入该结构的操作成本。

长度为 P 的前缀定位之后，还要遍历相关子树并构造输出。返回一百万个匹配键，成本不可能只有 O(P)；应另计访问节点、候选数量与输出字符总量。仅返回前几个结果也需明确顺序和停止条件，不能默认等于最热门的几个。

内存与总键长度、共享程度和孩子表示有关。为每个节点放一个固定大小的孩子[数组](../../glossary/algorithms.md#algorithms.sequences)，查分支方便却可能留下大量空槽；稀疏映射节省部分槽位，又增加元数据、分配与定位成本。Trie 不是对所有短键、长键和字符集都更省空间。

## 路径压缩减少节点，不免除字符核对

一条没有分叉、且被省略的中间节点没有终止标记的路径，可合并成较长的边标签；若要跨越完整键的结束位置，则必须另存标签内部的终止信息。本例可把根到 a 的两步压缩为标签 ca，再保留 r、t 分支。r* 到 t* 虽不分叉，却不能直接合成只在末尾终止的 rt*，否则会丢掉 car。查询前缀 c 时可能结束在标签 ca 的中间；这对前缀枚举仍可能是有效匹配，但不能把它当作完整键命中。

完整保存并比较压缩标签，同时保留所有键的终止信息，才能保持相应精确查询语义。若实现省略必要标签或只保存摘要，就还需其他完整键核对；不能只因节点变少而跳过匹配。插入导致标签中间分叉时需拆边；新短键恰好结束在标签中途时，则需拆边或保存内部终止位置。例如在已有标签 ca 时插入完整键 c，不能只因字符已经匹配就省掉其终止状态。删除后若重新合并，也必须保留仍存在键的结束位置。压缩概念参照 [CMU Trie/Compression](https://15445.courses.cs.cmu.edu/fall2024/notes/09-indexes2.pdf)，本文不提供压缩 Trie 实现。

长文本中的精确子串与跨块出现，继续见[字符串匹配](string-matching-prefix-functions-and-text-boundaries.md)。前缀树的键定位、[KMP](../../glossary/algorithms.md#algorithms.string-matching) 的失配复用和 Unicode 位置映射各有独立契约，不能由共享前缀直接推导任意位置扫描。

## 更新和编码属于键契约

从本例删除 car，应移除 r 的终止标记，保留通向 cart 的 t；若整条 r 分支被删除，会错误丢掉 cart。只有没有终止值且没有仍需保留的孩子时，才可考虑回收相应路径。更新已有键的值、重复插入和不存在键的删除也需分别定义。

生产文本要先规定按字节、码点还是其他单位建路，以及大小写、规范化和分隔符规则。同样外观的字符可以由不同码点序列表示，Unicode 的规范等价与规范化见 [UAX #15](https://www.unicode.org/reports/tr15/)。若写入和查询采用不同规则，精确结构也会返回业务上意外的结果；反过来，擅自合并大小写或规范形式又可能改变身份含义。

[并发](../../glossary/systems.md#systems.concurrency)修改时，读者还需看到一致的节点和终止状态，旧根、共享子树与回收分别有生命周期。结构有共同前缀不等于全部键自动有相同权限；枚举前缀仍需[授权](../../glossary/security.md#security.identity)和输出预算，不能把路径可达当作可返回给任意主体。

自检：路径还是完整键？要枚举前缀，还是找查询的最长已存前缀？压缩标签中途结束怎样解释？按什么编码和排序？删除短键后哪些长键还必须存在？

2026-10-20 核查 NIST、CMU、Princeton TrieST 的公开资料及 Unicode UAX #15，状态为 source-checked。路径、查询和删除均为纸面设计；未运行 Trie、压缩边、Unicode 规范化、排序、并发更新或检索性能实验。
