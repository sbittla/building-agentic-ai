def test_citations(ex):
    got = ex.citations("(work/2026-06-02-incident-kafka-lag.md:3) and (plan.v2/read-me.txt:12)")
    assert got == [("work/2026-06-02-incident-kafka-lag.md", 3), ("plan.v2/read-me.txt", 12)]
    assert ex.citations("(see page 12) (12:30) (plan.md)") == [], "these aren't citations"
