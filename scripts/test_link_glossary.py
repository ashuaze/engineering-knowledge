"""Behavior checks for the source rewriter's ambiguity and Markdown boundaries."""
import unittest
from common import DOCS, load_json
from link_glossary import GlossaryLinker


class GlossaryLinksTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.linker = GlossaryLinker(load_json('terms.json'))

    def link(self, text, domain='api'):
        return self.linker.link(text, DOCS / 'knowledge' / domain / 'sample.md')

    def test_first_mention_and_idempotence(self):
        original = '幂等性与 Idempotency；幂等键可重复使用。'
        result = self.link(original)
        self.assertEqual(result.count('#api.idempotency'), 1)
        self.assertIn('[幂等性](../../glossary/api.md#api.idempotency)', result)
        self.assertEqual(self.link(result), result)

    def test_code_metadata_headings_and_existing_links_are_untouched(self):
        protected = '''---
title: "幂等性"
---
# 幂等性
> ## 幂等性

幂等性
========

```python
print("幂等性")
```
~~~text
幂等性
~~~
    幂等性

`幂等性`、``幂等性 ` 示例``、[幂等性](other.md "title (with parentheses)")。
[引用][幂等性] 与 ![幂等性](image.png)。
[幂等性]: https://example.com/Idempotency
<a title="幂等性">幂等性</a>
<pre>
幂等性
</pre>
<!-- 幂等性 -->
'''
        result = self.link(protected + '\n幂等性。\n')
        self.assertTrue(result.startswith(protected))
        self.assertEqual(result.count('#api.idempotency'), 1)

    def test_urls_identifiers_and_longest_aliases(self):
        text = 'https://example.com/Idempotency <https://example.com/Idempotency> MyIdempotency。'
        self.assertEqual(self.link(text), text)
        result = self.link('Hydration Mismatch 与 Hydration。', 'frontend')
        self.assertIn('[Hydration Mismatch](../../glossary/frontend.md#frontend.hydration-mismatch)', result)
        self.assertIn('[Hydration](../../glossary/frontend.md#frontend.hydration)', result)

    def test_ambiguous_terms_use_domain_and_related_article(self):
        self.assertIn('#systems.memory-layout', self.link('Stack', 'systems'))
        self.assertIn('#algorithms.queues', self.link('Stack', 'algorithms'))
        self.assertEqual(self.link('Stack', 'security'), 'Stack')
        self.assertIn('#reliability.retry-budget', self.link('Timeout', 'reliability'))
        terms = [dict(t, aliases=['Shared Alias'], name='Shared Alias',
                      articles=['docs/knowledge/runtime/related.md'] if t['id'] == 'api.retries' else [])
                 for t in load_json('terms.json') if t['id'] in {'api.retries', 'reliability.retry-budget'}]
        path = DOCS / 'knowledge' / 'runtime' / 'related.md'
        self.assertIn('#api.retries', GlossaryLinker(terms).link('Shared Alias', path))

    def test_polysemous_terms_do_not_link_to_unrelated_concepts(self):
        self.assertEqual(self.link('RFC 9110、键的作用域、同步复制、会话、函数调用。'),
                         'RFC 9110、键的作用域、同步复制、会话、函数调用。')
        self.assertEqual(self.link('SELECT 与 OFFSET，数据库分页。', 'database'),
                         'SELECT 与 OFFSET，数据库分页。')
        self.assertEqual(self.link('可达性与扩容。', 'performance'), '可达性与扩容。')
        self.assertIn('#runtime.closure', self.link('作用域', 'runtime'))
        self.assertIn('#systems.io-multiplexing', self.link('select', 'systems'))

    def test_maintenance_terms_keep_package_and_type_context(self):
        text = '组件命名空间 / Namespace'
        self.assertEqual(self.link(text, 'engineering'), text)
        self.assertIn('#devops.isolation', self.link('命名空间', 'devops'))
        self.assertIn('#devops.isolation', self.link('Namespace', 'systems'))
        protected = '`npm ci`，TypeScript [类型兼容性](../runtime/type-systems-and-runtime-validation.md)。'
        result = self.link(protected, 'engineering')
        self.assertNotIn('#devops.cicd', result)
        self.assertNotIn('#api.versioning', result)
        self.assertIn('[类型兼容性](../runtime/type-systems-and-runtime-validation.md)', result)

    def test_feedback_and_infrastructure_terms_preserve_context(self):
        text = '测试重试后通过，不能覆盖首轮失败。'
        self.assertEqual(self.link(text, 'engineering'), text)
        self.assertIn('#api.retries', self.link('请求重试', 'api'))
        plan = '还没有执行计划里的资源变更。'
        self.assertEqual(self.link(plan, 'devops'), plan)
        self.assertIn('#database.plans', self.link('执行计划', 'database'))
        explicit = '[重试](#重试和临时隔离都要留下失败身份)仍需记录。'
        self.assertEqual(self.link(explicit, 'engineering'), explicit)

    def test_protocol_and_signal_terms_do_not_use_unrelated_domains(self):
        self.assertEqual(self.link('RTO 是重传计时期限。', 'networking'), 'RTO 是重传计时期限。')
        self.assertIn('#reliability.recovery', self.link('RTO', 'reliability'))
        self.assertEqual(self.link('nonce', 'api'), 'nonce')
        self.assertEqual(self.link('nonce', 'security'), 'nonce')
        explicit_nonce = '[nonce](../../glossary/security.md#security.oauth)'
        self.assertEqual(self.link(explicit_nonce, 'security'), explicit_nonce)
        self.assertEqual(self.link('通用 Undo', 'distributed'), '通用 Undo')
        self.assertIn('#database.recovery-log', self.link('Undo', 'database'))
        self.assertEqual(self.link('异步处理函数', 'systems'), '异步处理函数')
        self.assertEqual(self.link('异步处理回调', 'api'), '异步处理回调')
        self.assertIn('#messaging.cdc', self.link('异步处理', 'messaging'))
        identifiers = '`CREATE INDEX`、`index.gc_deletes`、`version_type=external`。'
        self.assertEqual(self.link(identifiers, 'cache-search'), identifiers)
        protocol = self.link('2PC 的协议阻塞不是线程挂起。', 'distributed')
        self.assertIn('#distributed.2pc', protocol)
        self.assertNotIn('#systems.blocking', protocol)
        self.assertIn('#systems.blocking', self.link('阻塞调用', 'systems'))

    def test_shared_state_and_browser_terms_keep_their_subject(self):
        self.assertEqual(self.link('传递闭包与 The Partial Ordering。', 'distributed'),
                         '传递闭包与 The Partial Ordering。')
        self.assertIn('#runtime.closure', self.link('闭包', 'runtime'))
        self.assertIn('#messaging.ordering', self.link('Ordering', 'messaging'))
        self.assertEqual(self.link('管道字节流与 POSIX 消息队列、Unix 数据报。', 'systems'),
                         '管道字节流与 POSIX 消息队列、Unix 数据报。')
        self.assertIn('#networking.transport', self.link('字节流', 'networking'))
        self.assertIn('#messaging.models', self.link('消息队列', 'messaging'))
        self.assertNotIn('#security.oauth', self.link('CSP nonce', 'security'))
        self.assertNotIn('#systems.concurrency', self.link('因果并发', 'distributed'))
        self.assertIn('#systems.concurrency', self.link('并发', 'systems'))

    def test_network_routing_and_subnets_keep_their_layer(self):
        self.assertEqual(self.link('HTTP 路由', 'networking'), 'HTTP 路由')
        self.assertIn('#networking.routing', self.link('IP 路由', 'networking'))
        self.assertIn('#networking.routing', self.link('路由表', 'networking'))
        self.assertIn('#networking.routing', self.link('最长前缀匹配', 'networking'))
        self.assertNotIn('#networking.routing', self.link('最长前缀匹配', 'algorithms'))
        self.assertIn('#ai.planning', self.link('路由', 'ai'))
        self.assertEqual(self.link('路由', 'frontend'), '路由')
        self.assertIn('#networking.ip-prefix', self.link('CIDR', 'networking'))
        self.assertEqual(self.link('子网', 'networking'), '子网')
        self.assertIn('#networking.ip-prefix', self.link('子网掩码', 'networking'))
        self.assertIn('#devops.cloud-network', self.link('子网', 'devops'))
        self.assertIn('#networking.nat', self.link('NAT', 'networking'))
        fields = '`TTL`、`Hop Limit`、`TTL=64`。'
        self.assertEqual(self.link(fields, 'networking'), fields)
        self.assertEqual(self.link('IP 分片与 NAT 空闲超时', 'networking').count('#database.partitioning'), 0)
        self.assertNotIn('#api.retries', self.link('NAT 空闲超时', 'networking'))
        self.assertIn('#database.partitioning', self.link('分片', 'database'))
        self.assertIn('#api.retries', self.link('超时', 'api'))

    def test_security_credentials_do_not_use_distributed_ownership_terms(self):
        text = self.link('Vault 凭据租约与 Lease', 'security')
        self.assertNotIn('#distributed.fencing', text)
        self.assertNotIn('#cache-search.lock-lease', text)
        self.assertIn('#distributed.fencing', self.link('租约', 'distributed'))
        self.assertIn('#database.prepared', self.link('Prepared Statement', 'security'))
        fields = '`lease_id`、`TTL`、`AWSCURRENT`、`statement_timeout`。'
        self.assertEqual(self.link(fields, 'security'), fields)
        self.assertNotIn('#algorithms.sequences', self.link('PostgreSQL 数组', 'security'))
        self.assertIn('#algorithms.sequences', self.link('数组', 'algorithms'))
        self.assertNotIn('#api.versioning', self.link('驱动兼容性', 'security'))
        self.assertIn('#api.versioning', self.link('兼容性', 'api'))

    def test_data_model_and_query_terms_keep_their_meaning(self):
        text = 'DynamoDB 分区键 / Partition Key；数据冗余与 Redundancy。'
        self.assertEqual(self.link(text, 'database'), text)
        routing = '分片查询的局部性与扇出 / Fanout。'
        linked = self.link(routing, 'database')
        self.assertNotIn('#systems.cpu-cache', linked)
        self.assertNotIn('#algorithms.b-tree', linked)
        self.assertEqual(self.linker.link('查询扇出', DOCS / 'index.md'), '查询扇出')
        self.assertIn('#messaging.ordering', self.link('分区键', 'messaging'))
        self.assertIn('#reliability.fault-domains', self.link('冗余', 'reliability'))
        self.assertIn('#systems.cpu-cache', self.link('局部性', 'systems'))
        self.assertIn('#algorithms.b-tree', self.link('扇出', 'algorithms'))
        self.assertIn('#database.functional-dependency', self.link('函数依赖', 'database'))
        self.assertIn('#database.shard-key', self.link('分片键', 'database'))
        self.assertIn('#database.partition-pruning', self.link('分区裁剪', 'database'))
        explicit = '[扇出](../../glossary/algorithms.md#algorithms.b-tree)'
        self.assertEqual(self.link(explicit, 'database'), explicit)

    def test_formal_availability_and_random_identifiers_keep_context(self):
        text = self.link('CAP 可用性 / Availability；UUID 碰撞。', 'distributed')
        self.assertNotIn('#reliability.availability', text)
        self.assertNotIn('#algorithms.hash-table', text)
        self.assertIn('#distributed.uuid', text)
        self.assertIn('#reliability.availability', self.link('可用性', 'reliability'))
        self.assertIn('#reliability.availability', self.link('Availability', 'devops'))
        self.assertIn('#algorithms.hash-table', self.link('碰撞', 'algorithms'))
        explicit = '[可用性](../../glossary/reliability.md#reliability.availability)'
        self.assertEqual(self.link(explicit, 'distributed'), explicit)
        member_names = '`AB` 与 `CD` 的副本集合。'
        self.assertEqual(self.link(member_names, 'distributed'), member_names)

    def test_rpc_streams_and_call_budgets_keep_their_layer(self):
        text = 'gRPC 的消息顺序与下一跳服务的剩余预算。'
        result = self.link(text, 'api')
        self.assertNotIn('#messaging.ordering', result)
        self.assertNotIn('#networking.routing', result)
        self.assertIn('#api.styles', result)
        self.assertIn('#messaging.ordering', self.link('消息顺序', 'messaging'))
        self.assertIn('#networking.routing', self.link('下一跳', 'networking'))
        resumption = '[TLS 会话恢复](../networking/tcp-tls-and-connection-states.md)'
        self.assertEqual(self.link(resumption, 'security'), resumption)

    def test_cache_prefilling_is_not_benchmark_warmup(self):
        text = '缓存预热在真实请求到达前填充数据。'
        self.assertNotIn('#performance.benchmark', self.link(text, 'cache-search'))
        self.assertIn('#performance.benchmark', self.link('预热', 'performance'))

    def test_transport_reliability_is_not_service_availability(self):
        self.assertNotIn('#reliability.availability', self.link('UDP 可靠性与重传', 'networking'))
        self.assertIn('#reliability.availability', self.link('服务可靠性', 'reliability'))
        self.assertIn('#reliability.availability', self.link('可靠性', 'devops'))

    def test_command_batching_is_not_frontend_bundling(self):
        self.assertNotIn('#frontend.bundling', self.link('把命令打包传输的 pipeline', 'cache-search'))
        self.assertIn('#frontend.bundling', self.link('打包', 'frontend'))

    def test_redis_groups_do_not_imply_partition_assignment(self):
        self.assertNotIn('#messaging.groups', self.link('Stream 消费组 / Consumer Group', 'cache-search'))
        self.assertIn('#messaging.groups', self.link('消费组', 'messaging'))
        self.assertIn('#messaging.groups', self.link('Consumer Group', 'messaging'))

    def test_existing_glossary_link_counts_as_first_mention(self):
        text = '[解释](../../glossary/api.md#api.idempotency) 幂等性'
        self.assertEqual(self.link(text), text)
        code = '```text\n../../glossary/api.md#api.idempotency\n```\n'
        self.assertIn('[幂等性]', self.link(code + '幂等性'))
        quoted_code = '> ```text\n> 幂等性\n> ```\n'
        self.assertTrue(self.link(quoted_code + '幂等性').startswith(quoted_code))
        self.assertIn('[幂等性]', self.link(quoted_code + '幂等性'))

    def test_search_stack_container_is_not_an_os_container(self):
        self.assertNotIn('#devops.containers', self.link('显式栈容器保存控制信息。', 'algorithms'))
        self.assertNotIn('#devops.containers', self.link('Container', 'algorithms'))
        self.assertIn('#devops.containers', self.link('容器', 'devops'))
        self.assertIn('#devops.containers', self.link('Container', 'systems'))

    def test_matching_invariant_is_not_automatically_atomicity(self):
        self.assertNotIn('#systems.atomicity', self.link('扫描不变量 / Invariant', 'algorithms'))
        self.assertIn('#systems.atomicity', self.link('原子性', 'systems'))
        explicit = '[不变量](../../glossary/systems.md#systems.atomicity)'
        self.assertEqual(self.link(explicit, 'systems'), explicit)

    def test_exact_matching_errors_are_not_bloom_membership(self):
        self.assertNotIn('#algorithms.bloom', self.link('精确匹配不误报 / False Positive / 假阳性', 'algorithms'))
        self.assertIn('#algorithms.bloom', self.link('Bloom Filter', 'cache-search'))

    def test_automaton_transitions_do_not_imply_dynamic_programming(self):
        self.assertNotIn('#algorithms.dynamic-programming', self.link('多模式扫描需要状态转移。', 'algorithms'))
        self.assertIn('#algorithms.dynamic-programming', self.link('动态规划', 'algorithms'))

    def test_rp_id_hash_is_not_password_derivation(self):
        self.assertNotIn('#security.passwords', self.link('RP ID hash', 'security'))
        self.assertIn('#security.passwords', self.link('口令哈希', 'security'))
        self.assertIn('#security.passwords', self.link('KDF', 'security'))

    def test_authenticator_is_not_split_into_authentication(self):
        text = '认证器、多因子认证器。'
        self.assertEqual(self.link(text, 'security'), text)
        self.assertIn('#security.identity', self.link('认证', 'security'))
        self.assertIn('#security.mfa', self.link('多因子认证', 'security'))

    def test_algebraic_merge_is_not_request_idempotence(self):
        text = '交换律、结合律与幂等性 / Idempotency；合并幂等。'
        self.assertNotIn('#api.idempotency', self.link(text, 'distributed'))
        self.assertIn('#api.idempotency', self.link('请求幂等性', 'api'))
        explicit = '[幂等性](../../glossary/api.md#api.idempotency)'
        self.assertEqual(self.link(explicit, 'distributed'), explicit)

    def test_cdc_target_checkpoint_is_not_a_wal_checkpoint(self):
        text = '目标检查点 / Checkpoint'
        self.assertEqual(self.link(text, 'database'), text)
        explicit = '[检查点](../../glossary/database.md#database.checkpoints)'
        self.assertEqual(self.link(explicit, 'database'), explicit)
        self.assertIn('#database.recovery-log', self.link('WAL', 'database'))

    def test_event_time_terms_do_not_capture_general_time_or_browser_windows(self):
        self.assertNotIn('#messaging.event-time', self.link('故障处理时间', 'devops'))
        self.assertNotIn('#messaging.event-time', self.link('事件时间戳', 'distributed'))
        self.assertNotIn('#messaging.windows', self.link('浏览器 Window', 'runtime'))
        stream = self.link('事件时间、处理时间、水位线、Window 与 Trigger', 'messaging')
        self.assertIn('#messaging.event-time', stream)
        self.assertIn('#messaging.windows', stream)

    def test_native_abi_does_not_imply_a_kernel_transition(self):
        self.assertNotIn('#systems.privilege', self.link('FFI 的 ABI 需要双方约定。', 'runtime'))
        self.assertIn('#systems.privilege', self.link('系统调用 ABI', 'systems'))

    def test_literal_matching_text_is_not_a_concurrent_aba_problem(self):
        self.assertNotIn('#systems.memory-reclamation', self.link('前缀 aba 与 ABA', 'algorithms'))
        self.assertIn('#systems.memory-reclamation', self.link('并发中的 ABA', 'systems'))

    def test_scheduler_entities_are_not_domain_model_entities(self):
        self.assertNotIn('#architecture.domain-model', self.link('调度实体与 Entity', 'systems'))
        self.assertIn('#architecture.domain-model', self.link('领域实体', 'architecture'))

    def test_cluster_control_plane_is_not_ip_route_selection(self):
        text = '控制平面调整端点，数据平面继续处理请求。'
        self.assertNotIn('#networking.policy-routing', self.link(text, 'devops'))
        self.assertIn('#networking.policy-routing', self.link(text, 'networking'))

    def test_network_queue_does_not_imply_fifo_data_structure(self):
        self.assertNotIn('#algorithms.queues', self.link('路由器中的队列等待。', 'networking'))
        self.assertNotIn('#algorithms.queues', self.link('Active Queue Management', 'networking'))
        self.assertIn('#algorithms.queues', self.link('FIFO 队列', 'algorithms'))

    def test_service_worker_plural_is_not_a_kubernetes_service(self):
        self.assertNotIn('#devops.k8s', self.link('Service Workers 草案', 'frontend'))
        self.assertIn('#devops.k8s', self.link('Service', 'devops'))

    def test_component_reordering_is_not_retrieval_reranking(self):
        self.assertNotIn('#cache-search.hybrid', self.link('按身份复用和重排组件。', 'frontend'))
        self.assertIn('#cache-search.hybrid', self.link('召回与重排', 'cache-search'))

    def test_sse_event_stream_does_not_imply_a_durable_event_log(self):
        self.assertNotIn('#messaging.models', self.link('SSE 的 HTTP 事件流', 'frontend'))
        self.assertIn('#messaging.models', self.link('事件流', 'messaging'))

    def test_small_change_lists_are_not_layout_shift_metrics(self):
        self.assertNotIn('#frontend.web-vitals', self.link('Google Small CLs', 'engineering'))
        self.assertIn('#frontend.web-vitals', self.link('CLS', 'frontend'))

    def test_package_identity_is_not_ui_component_identity(self):
        self.assertNotIn('#frontend.component-identity', self.link('SBOM 的组件身份包含名称和版本。', 'engineering'))
        self.assertIn('#frontend.component-identity', self.link('组件身份', 'frontend'))

    def test_generated_output_has_all_term_destinations(self):
        # Validate actual generated destinations; no snapshot of incidental prose.
        for term in load_json('terms.json'):
            page = DOCS / 'glossary' / f"{term['domain']}.md"
            with self.subTest(term=term['id']):
                self.assertIn(f'<a id="{term["id"]}"></a>', page.read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
