# Interlude: Testing with pytest

From Chapter 2 on, you'll check your agent code with automated tests, so this short interlude teaches you to write them. You'll run a small test file, break the code on purpose to watch a test catch it, and learn the five pytest patterns the rest of this book relies on. By the end, you'll be able to test code that reads files or calls the network without touching either.

## Learning objectives

By the end of this interlude you can:

- Write a pytest test that checks a function's result with `assert`.
- Run one check over many examples with `parametrize`, and check errors with `pytest.raises`.
- Test code that uses files (`tmp_path`) or slow and costly calls (`monkeypatch`).
- Explain why you test tools directly and replace the model with a stand-in.

## Why this interlude

From Chapter 2 on, exercises ask you to "add tests". A **test** is a small program that checks your code does what you think it does. Agents make tests even more important: in Chapter 10 an agent uses tests to know when it has fixed a bug, and in Chapter 27 you test the agent itself. This interlude teaches the five pytest features this book uses.

## T.1 A test is a function that asserts

pytest finds files named `test_*.py`, runs every function named `test_*` and reports which `assert` statements failed. Here's a small module to test:

@@code i_pricing.py

And its tests:

@@code test_i_pricing.py

Run them with `./course.sh pytest -q test_i_pricing.py`. A dot means a test passed. An `F` means it failed, followed by an explanation showing the values that didn't match.

## T.2 The five patterns you'll use

| Pattern | Use it when | In the file |
| --- | --- | --- |
| Plain `assert` | Checking one input and output | `test_ten_percent_off` |
| `@pytest.mark.parametrize` | Running the same check on many examples | `test_parse_price` |
| `pytest.raises` | Checking that bad input raises an error | `test_rejects_bad_percent` |
| `tmp_path` fixture | The code reads or writes files | `test_save_receipt` |
| `monkeypatch` | Temporarily replacing something slow, costly or random (a network call, the model) with a stand-in | `test_replace_a_function` (and exercise T.4 for a real network call) |

A **fixture** is something pytest prepares for a test and cleans up afterward. You ask for one by naming it as a parameter: `def test_x(tmp_path):` gets a fresh temporary folder.

:::tip Test the model-free parts
Model answers vary from run to run, so test your **tools** directly (they're ordinary functions) and replace the model with a stand-in when you test the loop. This book's own solution tests do exactly this, with a scripted fake model.
:::

## T.3 Good tests

- **One behavior per test**, with a name that says what it checks.
- **Arrange, act, assert**: set up inputs, call the code, check the result.
- **Test edges**: empty input, zero, very large numbers, missing fields.
- **Make them fast.** You'll run tests that finish in a second often.

## Summary

- A test is a function named `test_*` that asserts; pytest finds and runs it.
- `parametrize`, `pytest.raises`, `tmp_path` and `monkeypatch` cover almost every test in this book.
- Test the model-free parts directly; replace the model with a scripted stand-in to test the loop.
- Good tests check one behavior, cover the edges and run fast.

Next comes Chapter 2, where you'll put these habits to work: its exercises ask you to add tests alongside the new code, and the patterns above are all you need.

## Learn more

Free, trustworthy places to read more about this chapter's topics. Start with the **Start here** rows; **Go deeper** rows are for when you want more detail. Links were checked in September 2026; if one has moved, search for its title.

| Resource | What you'll find | Level |
| --- | --- | --- |
| **pytest: Get started**<br>[docs.pytest.org/en/stable/getting-started.html](https://docs.pytest.org/en/stable/getting-started.html) | Install, write and run your first tests | Start here |
| **Real Python: Effective testing with pytest**<br>[realpython.com/pytest-python-testing](https://realpython.com/pytest-python-testing/) | A friendly tour of fixtures, marks and parametrize | Start here |
| **pytest: How to parametrize tests**<br>[docs.pytest.org/en/stable/how-to/parametrize.html](https://docs.pytest.org/en/stable/how-to/parametrize.html) | One test, many inputs (exercise T.2) | Go deeper |
| **pytest: How to monkeypatch**<br>[docs.pytest.org/en/stable/how-to/monkeypatch.html](https://docs.pytest.org/en/stable/how-to/monkeypatch.html) | Replacing functions and settings in tests (exercise T.4) | Go deeper |

## Exercises

Exercises T.2 to T.4 start from a test file with the first test already written. `./course.sh check T.3` runs your tests and, for T.3, also checks that they **catch** a planted bug.

:::ex Simple | T.1 | Run and break
Run `test_i_pricing.py`. Then change `apply_discount` to `amount * (1 - percent)` (a real bug from Chapter 10) and run the tests again.
**Done when:** You've seen the tests pass, then fail with a message showing `-1800 != 180`, then pass again after you undo the change.
:::

:::ex Simple | T.2 | Parametrize
Add a parametrized test for `apply_discount` with at least five cases, including 0%, 100% and a fractional percent.
**Done when:** All cases pass, and each appears on its own line with `pytest -v`.
:::

:::ex Medium | T.3 | Test your Chapter 0 code
Write `tests/test_ex_t3.py` for the three functions from exercise 0.4, with an edge case for each (empty text, a tie for most common word, an empty invoice). Import them with `from ex0_4_basics import word_count, most_common_word, invoice_total`; the kit puts `workspace/exercises` on Python's path for you.
**Done when:** At least nine tests pass, and one of them caught a real bug in your 0.4 code (or you can explain why none did).
:::

:::ex Medium | T.4 | Fake the network
Write a test for `max_temperature` in `ch00_http.py` that uses `monkeypatch` to replace `httpx.get` with a function that returns a fake response, so the test needs no internet. Test both a 200 answer and a 503 answer.
**Hint:** The fake response needs `status_code`, `text` and a `json()` method. The starter file includes a small `FakeResponse` class you can use.
**Done when:** Both tests pass with networking turned off.
:::
