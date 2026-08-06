# Workflow usability test

This protocol measures whether a researcher can reach a useful first Reference
route without maintainer intervention. It is an optional product-evaluation
protocol, not a prerequisite for installation or use.

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

Record these fields for each session:

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

## Review criteria

Treat any data-loss or unintended-sharing issue as a release-blocking defect.
Treat a blocked first route as a workflow defect. Use completion time,
explanation needs, and confusing wording to prioritize later improvements.
Automated smoke tests and observed usability sessions measure different parts
of the product and should be recorded separately.
