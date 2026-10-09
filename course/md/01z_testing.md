# Interlude: Testing with pytest

Make one small slip in a discount function and 10% off a $200 order comes out as −$1,800. Python runs it without complaint. A three-line test catches it at once, and from Chapter 2 on your code changes often enough that you'll want that safety net everywhere. You'll start by breaking code on purpose, because watching a test catch a bug is the quickest way to start trusting tests. Then you'll learn to test even code that reads files or calls the network.

**Prerequisites:** Chapter 0 and the Python interlude.

## Learning objectives

By the end of this interlude you can:

- Write a pytest test that checks a function's result with `assert`.
- Use `parametrize`, `pytest.raises`, `tmp_path` and `monkeypatch`.
- Explain why you test tools directly and replace the model with a stand-in.

## Why this interlude

A **test** is a small program that checks your code does what you think it does. With agents, tests matter twice: in Chapter 10 an agent uses them to know it has fixed a bug, and in Chapter 27 you test the agent itself.

## T.1 A test is a function that asserts

pytest finds files named `test_*.py`, runs every function named `test_*` and reports which `assert` statements failed. Here's a module to test:

@@code i_pricing.py

And its tests:

@@code test_i_pricing.py

Run them with `./course.sh pytest -q test_i_pricing.py`. A dot means a test passed. An `F` means it failed, and pytest shows you the values that didn't match.

## T.2 The five patterns you'll use

Table: The five pytest patterns
| Pattern | Use it when | In the file |
| --- | --- | --- |
| Plain `assert` | Checking one input and output | `test_ten_percent_off` |
| `@pytest.mark.parametrize` | Running the same check on many examples | `test_parse_price` |
| `pytest.raises` | Checking that bad input raises an error | `test_rejects_bad_percent` |
| `tmp_path` fixture | The code reads or writes files | `test_save_receipt` |
| `monkeypatch` | Swapping something slow, costly or random (a network call, the model) for a stand-in | `test_replace_a_function`; exercise T.4 |

A **fixture** is something pytest prepares for a test and cleans up afterward. You ask for one by naming it as a parameter: `def test_x(tmp_path):` gets a fresh temporary folder.

:::tip Test the model-free parts
Model answers vary from run to run, so test your **tools** directly (they're ordinary functions) and swap in a scripted fake model when you test the loop, as the book's solution tests do.
:::

## T.3 Good tests

- **One behavior per test**, with a name that says what it checks.
- **Arrange, act, assert**: set up inputs, call the code, check the result.
- **Test edges**: empty input, zero, huge numbers, missing fields.
- **Make them fast.** You'll run a one-second suite often and a slow one rarely.

## Key takeaways

- A test is a function named `test_*` that asserts; pytest finds and runs it.
- `parametrize`, `pytest.raises`, `tmp_path` and `monkeypatch` cover almost every test in this book.
- Test the model-free parts directly; script a fake model to test the loop.

Keep pytest close. Chapter 2 gives the model its first tool, and a tool is an ordinary function you can test exactly the way you tested `apply_discount`.

## Learn more

Start with these. `RESOURCES.md` in the course kit has all 4 links for this chapter, including the **Go deeper** reading.

| Resource | What you'll find |
| --- | --- |
| **pytest: Get started**<br>[docs.pytest.org/en/stable/getting-started.html](https://docs.pytest.org/en/stable/getting-started.html) | Install, write and run your first tests |
| **Real Python: Effective testing with pytest**<br>[realpython.com/pytest-python-testing](https://realpython.com/pytest-python-testing/) | A friendly tour of fixtures, marks and parametrize |

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
Write `tests/test_ex_t3.py` for the three functions from exercise 0.4, with an edge case for each (empty text, a tie for most common word, an empty invoice). Import them with `from ex0_4_basics import word_count, most_common_word, invoice_total`; the kit puts `workspace/exercises` on Python's path.
**Done when:** At least nine tests pass, and one of them caught a real bug in your 0.4 code (or you can explain why none did).
:::

:::ex Medium | T.4 | Fake the network
Write a test for `max_temperature` in `ch00_http.py` that uses `monkeypatch` to replace `httpx.get` with a function that returns a fake response, so the test needs no internet. Test both a 200 answer and a 503 answer.
**Hint:** The fake response needs `status_code`, `text` and a `json()` method. The starter file includes a small `FakeResponse` class you can use.
**Done when:** Both tests pass with networking turned off.
:::
