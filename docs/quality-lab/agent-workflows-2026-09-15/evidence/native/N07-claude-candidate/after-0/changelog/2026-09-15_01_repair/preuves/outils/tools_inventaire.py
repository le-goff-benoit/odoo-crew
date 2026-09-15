recs = env['lab.preparation'].search([], order='id')
print("total=%s" % len(recs))
print("id | name | state | ordered | delivered | prepared | manual | parent")
for r in recs:
    print("%s | %s | %s | %s | %s | %s | %s | %s" % (
        r.id, r.name, r.state, r.ordered_qty, r.delivered_qty,
        r.prepared_qty, r.manual, r.parent_id.id or ''))
