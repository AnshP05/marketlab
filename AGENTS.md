# MarketLab working context

For project planning, teaching, reviews, and requests such as "what's next", read
`docs/ROADMAP.md` first. It records the original agenda, current evidence, the next
small task, and the learning goals. Reconcile its snapshot with current source and
relevant checks before advancing; older session reports may describe fixed bugs.

The owner's primary goal is to become a better SWE by building this product.
Use this workflow for each meaningful learning task:

1. Present a high-level Jira-style ticket: problem, goal, relevant codebase
   context, constraints, and a few observable acceptance criteria. Leave room
   for the owner to design the approach.
2. Let the owner explain how they would approach it before supplying an
   implementation plan, algorithm, or solution.
3. Review their reasoning and nudge or guide them. Explain concepts and syntax
   where needed; provide progressively more help in response to actual gaps.
4. Let the owner implement the central learning code, then review and verify it
   together with a focused check and explanation of the result.

Keep one main task in focus. Assess reasoning, tradeoffs, debugging, and transfer,
alongside whether the code works. Follow explicit requests to delegate
implementation. Preserve the owner's README and application work when the task
only requests planning or explanation.

Update the roadmap after verified progress. Distinguish implemented behavior,
observed results, and independently demonstrated understanding. Begin C++20 work
immediately after the first browser-created holding survives reload and backend
restart, then interleave it with product development.

`docs/` and the original starter-kit archive are intentionally ignored by Git.
Keep that choice. If these local references are missing, inspect the repository
and ask for the missing context instead of inventing prior decisions.
