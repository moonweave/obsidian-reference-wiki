# First-user beta test

This protocol measures whether a researcher can reach a useful first Reference
route without maintainer intervention. Automated smoke tests do not satisfy
this human gate.

## Test boundary

- Use a private temporary Vault or a copy made for the test.
- Use one PDF the tester is authorized to read.
- Do not publish or commit the extracted Markdown.
- The maintainer may observe but must not explain the preset or file structure
  until the task ends.

## Fifteen-minute task

1. Ask the skill to set up a literature or reference wiki without naming a
   preset. Confirm that the first choice is notes only, searchable library, or
   knowledge network and that no file is created yet.
2. Select `searchable-library`, state whether the Vault is private/shared and
   how it synchronizes, then provide the exact temporary Vault and one PDF.
3. Read the proposed Blueprint. In the tester's own words, identify the
   canonical PDF, parsed full text, Paper dossier, and promoted knowledge notes.
4. Approve only the one-paper pilot. Open the result in Obsidian and follow
   `Reference Index -> Paper -> Source Text manifest`.
5. Run the printed `check_notes.py` and `check_source_text.py` commands. Inspect
   every formula/image warning against the PDF before accepting a claim.

## Acceptance record

Record these fields for every tester:

```text
Tester ID:
OS / Python / Obsidian:
Selected preset:
Time to approved Blueprint:
Time to resolving first Paper route:
Needed maintainer explanation: yes/no + where
Understood canonical vs derived vs dossier vs promoted note: yes/no
Both checkers passed: yes/no
Formula/image warnings understood: yes/no
P0 data-loss or sharing issue:
P1 blocked first route:
Confusing wording:
One improvement:
```

## Public-v1 human gate

The human gate passes only after at least three first-time researchers complete
the task, at least two finish without maintainer explanation, all can explain
the four representation layers, no P0/P1 issue remains, and the median time to
a resolving first Paper route is at most fifteen minutes. Until then, describe
the release as a technical beta even when all automated gates pass.
