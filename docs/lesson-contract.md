# The lesson contract

Every lesson in this repo has the same seven sections, in the same order, with
the same headings. No exceptions. If a lesson does not fit the shape, the lesson
is wrong, not the shape.

The contract exists for three reasons:

1. **Learning.** A fixed spine means the only new thing in lesson 9 is the idea
   in lesson 9. You are never also relearning where the answer lives.
2. **Sharing.** A reader who has read one lesson can navigate all of them.
3. **Honesty.** Sections 3 and 7 are the ones people skip. Making them mandatory
   is the whole discipline: a model is not a result until it has beaten
   something and admitted what it cannot do.

## The seven sections

### 1. The cricket question
One sentence a cricket fan would actually ask, with no ML vocabulary in it.
*"How many will they get from here?"* — not *"regress final score on powerplay
features."* If you cannot phrase it this way, you do not yet know what you are
modelling.

### 2. The data
Which table, at what grain, over what period. State the exclusions **and the
reason**: rain-affected games, super overs, innings shorter than N balls. A
filter without a reason is a bug waiting to be discovered by a reader.

### 3. The naive answer
The rule a commentator would give, scored on the same test set with the same
metric as the model. Use `cricketml.models.baselines`, or add one there.
**A lesson with no baseline does not get merged.**

### 4. The idea
The ML concept — in cricket first, then in maths. One paragraph of each. The
cricket paragraph must stand alone; the maths paragraph must be correct. Name
the assumption the method makes and whether cricket actually satisfies it.

### 5. Build it
The model. Short. Use `cricketml` helpers for the split — never
`train_test_split(shuffle=True)`, never a split that is not `temporal_split`,
`season_split` or `match_group_cv`. Fix the seed to `cricketml.SEED`.

### 6. Judge it
One results table via `regression_report_row` / `classification_report_row`,
baseline included as a row. Then read the table out loud in prose: *what* is
better, by *how much*, and whether that margin would survive a different season.

### 7. What it gets wrong
The failure modes. Where does it break — a chase, a rain-shortened game, a
debutant with no history, a new venue? Close by naming the concept that fixes
it, which is the next lesson. This section is what turns a pile of notebooks
into a curriculum.

## Fixed rules across all lessons

| Rule | Why |
|---|---|
| Split with `cricketml.evaluation.splits` only | Cricket data is temporal and grouped; a shuffled split invents skill that is not there |
| Seed is `cricketml.SEED` (1983) | A lesson re-run next year prints the numbers its prose quotes |
| Baseline before model, always | Complexity must be earned, not assumed |
| Probabilities, not labels, for classifiers | The threshold is a cricketing decision, not a default |
| Charts via `cricketml.viz.use_theme()` | Blue means the same thing in lesson 1 and lesson 15 |
| Cite the data under every published chart | `annotate_source()` |
| Notebook outputs stripped on commit | `nbstripout` runs in pre-commit; diffs stay readable |
| Reusable logic moves to `src/cricketml/` | If two lessons need it, it is not lesson code |

## Starting a new lesson

```bash
cp -r lessons/_template lessons/NN-short-slug
```

Replace `NN-short-slug` in the Colab badge (notebook title cell and `README.md`)
with the folder name, and point the data line at the end of the Colab setup cell
at this lesson's data (`tests/test_colab.py` checks the badge).

Then fill in the seven sections, add a row to the roadmap table in the top-level
`README.md`, and run `make check` before committing.
