# aiburnclock.org

A live estimate of how much money burns in AI on reading files nobody needed, from public sources with an open formula.

- `build.py` fetches Treasury (Debt to the Penny), USAspending (contracts naming AI, by FY / state / agency / recipient) and Census population, then renders `site/`: the national page, 51 state pages, the embed, `data.json`, methodology and press pages.
- `templates/` holds the pages. Every parameter of the estimate is a slider on the page with its source next to it.
- Deploy: `python3 build.py && npx wrangler pages deploy site --project-name aiburnclock`.

Built by the XERJ community. Not affiliated with any government agency. Corrections: hello@aiburnclock.org.
