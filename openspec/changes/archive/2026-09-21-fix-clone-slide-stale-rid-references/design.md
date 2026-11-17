## Context

`clone_slide` 当前流程：

```
1. add_slide(layout) → 新 slide 有骨架 spTree + 自动创建的 rId1→layout
2. 遍历源 slide 关系 → 跳过 TAG/LAYOUT，复制其余 → rId_map: {rId4→rId2}
3. deepcopy spTree → _remap_rIds(clone, rId_map) → rId4→rId2 ✓
4. 替换新 slide 的 spTree
```

问题在第 3 步：`_remap_rIds` 只重映射存在于 `rId_map` 中的 rId。被跳过的 rId1、rId2（指向源 slide 的 tags）保留原值。新 slide 的 `.rels` 中 rId1→layout、rId2→image，但克隆的 spTree 中 `<tags r:id="rId1">` 和 `<tags r:id="rId2">` 仍然存在，形成类型错配。

## Goals / Non-Goals

**Goals:**
- 清除克隆 spTree 中引用被跳过 rId 的 XML 元素
- 保持 `clone_slide` 的函数签名不变
- 不影响非 tag 类型的 spTree 内容

**Non-Goals:**
- 不保留或迁移 tag 内容（template slide 的 custom XML tags 不属于生成输出）
- 不改变 `_remap_rIds` 的行为
- 不修改 prune_slides、generate 等其他函数

## Decisions

### 决策：追踪跳过 rId + 从 spTree 移除对应元素

**方案**：在遍历源 slide 关系时收集被跳过的 rId 到集合 `skipped_rids`。`_remap_rIds` 之后，遍历克隆的 spTree，找到引用跳过 rId 的元素并将其从父元素中移除。

```python
skipped_rids = set()
for rel in source_slide.part.rels.values():
    if rel.reltype in (RT.SLIDE_LAYOUT, RT.TAGS):
        skipped_rids.add(rel.rId)
        continue
    ...

# After _remap_rIds
_remove_skipped_refs(cloned_spTree, skipped_rids)
```

**备选方案**：
- **覆盖 rId_map 中跳过的 rId → 映射到移除**：改变 `_remap_rIds` 语义，增加复杂度，影响其他调用方
- **移除后重新编号**：不需要，`_remap_rIds` 已将有效引用更新为新 rId，只需删除 stale 引用
- **克隆前过滤 spTree**：在 copy.deepcopy 前移除元素 → 修改源数据，不安全

**选择理由**：最小侵入，逻辑清晰 —— 跳过的关系 → 对应的 spTree 引用也要移除。不影响现有的 `_remap_rIds` 机制。

### 决策：`_remove_skipped_refs` 作为独立辅助函数

将清理逻辑封装为 `_remove_skipped_refs(element, skipped_rids)`，与 `_remap_rIds` 并行。职责单一，方便测试。

```
def _remove_skipped_refs(element, skipped_rids):
    for el in element.iter():
        for attr in (rId_attr, embed_attr, link_attr):
            if el.get(attr) in skipped_rids:
                el.getparent().remove(el)
                break  # 元素已移除，跳出属性循环
```

## Risks / Trade-offs

- **删除 `<custDataLst>` 中的 `<tags>` 子元素可能留下空的 `<custDataLst>`** → 低风险：空的 custDataLst 不影响 PowerPoint 解析。可在后续迭代中清理空容器。
- **删除操作在迭代中进行** → 使用 `list(element.iter())` 冻结遍历列表，避免修改迭代器。
