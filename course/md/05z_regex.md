# Interlude: Regular Expressions

A model hands your tool the order id `A1001; DROP TABLE`. A trace you're about to store contains an API key. The latency you need is buried in a noisy log line. Each time, you need to say exactly what text looks like, and regular expressions are how code says it. This interlude teaches only the patterns those three jobs need; `EXTRA_PRACTICE.md` in the course kit has the broader tutorial.

**Prerequisites:** Chapter 0 and the Python interlude (strings).

## Learning objectives

By the end of this interlude you can:

- Read and write simple patterns with digits, words, sets, repetition and groups.
- Choose between `re.search`, `re.findall`, `re.sub` and `re.fullmatch`.
- Validate a tool input, extract values from logs and hide secrets.
- Explain why regex is the wrong tool for security checks such as path validation.

## Why this interlude

Chapter 6's search tool, the citation checker in exercise 6.4, Chapter 11's web-page cleaner and Chapter 28's trace redaction all use **regular expressions** (regex): short patterns that match text. Regex has a reputation for being unreadable, and long patterns earn it. You only need to read and write short ones.

## R.1 The pieces

@@code i_regex.py

Table: The pieces of a regular expression
| Pattern | Matches | Example |
| --- | --- | --- |
| `abc` | The literal text | `ERROR` |
| `\d` | One digit | `\d\d` matches `42` |
| `\w` | One letter, digit or underscore | `\w+` matches `order_1` |
| `\s` / `\S` | Whitespace / anything except whitespace | `\S+` matches one word |
| `.` | Any single character | `a.c` matches `abc` |
| `+`, `*`, `?` | One or more / zero or more / optional | `\d+ms` |
| `{n}` | Exactly n times | `\d{4}` matches a year |
| `[A-Z]` | One character from a set | `[A-Z]\d+` matches `A1001` |
| `^` / `$` | Start / end of a line (with `re.MULTILINE`) | `^ERROR` |
| `( )` | Capture this part | `order=(\w+)` |
| `a\|b` | Either | `ERROR\|WARN` |

## R.2 The four functions

Table: The four `re` functions
| Function | Returns | Use for |
| --- | --- | --- |
| `re.search(p, text)` | The first match, or `None` | "Does it contain…?" |
| `re.findall(p, text)` | A list of all matches (or of the captured groups) | Extracting values |
| `re.sub(p, new, text)` | Text with matches replaced | Hiding secrets in logs |
| `re.fullmatch(p, text)` | A match only if the whole text fits | Validating a tool input, such as an order id |

Write patterns as raw strings, such as `r"\d+"`, so Python leaves the backslashes alone.

:::warn Don't over-trust regex for security
A regex that looks for `..` in a path is easy to get around, as Chapter 6 shows. Use regex to find and extract text. For security, resolve the path instead.
:::

## Key takeaways

- Patterns are built from literals, `\d` `\w` `\s`, sets, repetition, anchors and groups.
- `search` finds, `findall` extracts, `sub` replaces, `fullmatch` validates a whole input.
- Write patterns as raw strings (`r"..."`).
- Use regex to find and extract text, never as a security check.

In Chapter 6 your agent gets a folder of 20 notes and must answer from them, finding the right lines and citing each one.

## Learn more

Start with these. `RESOURCES.md` in the course kit has all 4 links for this chapter, including the **Go deeper** reading, ready to click.

| Resource | What you'll find |
| --- | --- |
| **RegexOne**<br>[regexone.com](https://regexone.com) | Interactive beginner lessons, one idea at a time |
| **regex101**<br>[regex101.com](https://regex101.com) | Test a pattern and see each part explained (choose the Python flavor) |

## Exercises

Each exercise starts from a file with the function names already in place. Run `./course.sh check R.1` (R.2, ...) to check your answer.

:::ex Simple | R.1 | Extract from logs
Using the log in `i_regex.py`, write patterns that extract: every timestamp; every service name; every latency number as an integer.
**Done when:** You get three lists, and the latencies are `[800, 812]`.
:::

:::ex Simple | R.2 | Mask secrets
Write `mask(text)` that replaces anything that looks like an API key (`sk-` followed by at least 10 letters, digits or dashes) with `sk-***`.
**Done when:** It masks keys inside longer sentences and leaves `sk-` on its own unchanged.
:::

:::ex Medium | R.3 | Parse citations
Write `citations(text)` that returns every `(file:line)` citation in a text, such as `(work/plan.md:12)`, as `(file, line_number)` pairs. Chapter 6 and exercise 6.4 use exactly this.
**Done when:** It finds citations with folders, dots and dashes in file names, and ignores `(see page 12)`.
:::
