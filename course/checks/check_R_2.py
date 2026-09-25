def test_mask(ex):
    assert ex.mask("key sk-ant-api03-XYZ1234567 end") == "key sk-*** end"
    assert ex.mask("two: sk-1234567890 and sk-abcdefghijKLM") == "two: sk-*** and sk-***"
    assert ex.mask("sk- alone") == "sk- alone" and ex.mask("sk-short") == "sk-short"
    assert ex.mask("task-1234567890") == "task-1234567890", "only keys that START with sk-"
