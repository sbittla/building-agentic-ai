"""The gateway's audit trail redacts arguments the same way traces do (sections 28.3 and 30.9)."""


def test_audit_arguments_are_redacted_but_keep_their_shape(ws):
    import ch30_gateway as gw
    args = {"to": "ana@example.com", "items": [{"note": "call ana@example.com"}], "qty": 2}
    out = gw._redacted(args)
    assert "ana@example.com" not in str(out)
    assert out["qty"] == 2 and isinstance(out["items"], list) and set(out) == set(args)
