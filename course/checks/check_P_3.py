def test_tasklist(ex):
    t = ex.TaskList()
    assert t.add("buy milk") == 1 and t.add("call bank", "2026-10-01") == 2
    assert t.complete(1) is True and t.complete(99) is False
    assert t.open_tasks() == ["call bank"]
    assert all(isinstance(x, ex.Task) for x in t.tasks), "store Task objects"
    assert ex.TaskList().open_tasks() == [], "a new list starts empty (no shared state)"
