# Interlude: Regular Expressions

Agents often need to find exact text: an error code, a timestamp, a file-and-line citation. Regular expressions are the standard way to describe that kind of text in code. This short interlude teaches you enough to read and write simple patterns, and you'll practice by pulling values out of a log and hiding API keys.

**Prerequisites:** Chapter 0 and the Python interlude (strings).

## Learning objectives

By the end of this interlude you can:

- Read and write simple regular expressions with digits, words, sets, repetition and groups.
- Choose between `re.search`, `re.findall`, `re.sub` and `re.match`.
- Extract values from logs and hide secrets in text.
- Explain why regex is the wrong tool for security checks such as path validation.

## Why this interlude

Chapter 6's search tool, Chapter 8's table checks and Chapter 11's citation checker all use **regular expressions** (regex): short patterns that match text. You don't need to master them. You need to read and write simple ones.

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
| `re.match(p, text)` | A match only at the very start | Parsing a fixed format |

Always write patterns as raw strings, such as `r"\d+"`, so Python doesn't treat the backslashes specially.

:::warn Don't over-trust regex for security
A regex that checks for `..` in a path can be bypassed (Chapter 6). Use regex to find and extract text. For security checks, use proper tools, such as resolving paths.
:::

## Key takeaways

- A pattern is built from a few pieces: literals, `\d` `\w` `\s`, sets, repetition, anchors and groups.
- `search` finds, `findall` extracts, `sub` replaces and `match` checks the start.
- Write patterns as raw strings (`r"..."`).
- Use regex to find and extract text, never as a security check.

With these pieces you can read the patterns in the chapters ahead. Next, Chapter 6 puts them to work: you'll build an agent that lists, searches and reads a folder of notes, and cites exactly where each answer came from.

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

:::ex Medium | R.4 | Error codes
Write a pattern that finds error codes like `ERR-4471` but not `ERR-44` or `XERR-4471`, and explain why embedding-based search (Chapter 18) might confuse `ERR-4471` with `ERR-4417` while this pattern can't.
**Hint:** `\b` matches a word boundary.
**Done when:** Your pattern passes five examples you write, and your explanation is two sentences.
:::
