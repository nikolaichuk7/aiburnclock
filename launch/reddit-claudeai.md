# r/ClaudeAI (and cross-post r/ChatGPTCoding)

Title: I measured how much Claude Code reads vs. what it needs to answer: 16× to 47×. Here is the plugin that prints your own number after every session.

Body:
Three questions on my production codebase, measured twice each: once with Claude Code doing its usual grep-open-read, once with a local index answering "where is it" first and Claude reading only the passage.

- "Where is the payment webhook signature verified?" 103,023 B of files vs 6,405 B through the index (16×)
- "How does an owner cancel a subscription?" 243,640 B vs 6,389 B (38×)
- "What happens when a dish photo is uploaded?" 241,859 B vs 5,101 B (47×)

Same answers, same file:line pointers. The difference is what got loaded into context and billed.

I packaged the setup as a Claude Code plugin: it adds a local search engine (XERJ, open source, one binary, runs on your machine) as memory, teaches Claude to retrieve before it reads, and at the end of the session prints a score card: bytes read through the index vs the whole files behind them, plus a PNG you can post. Counts only, nothing leaves the machine.

    /plugin marketplace add nikolaichuk7/xerj-plugins
    /plugin install xerj-memory@xerj-plugins

The site with the method, the sliders and the sources: aiburnclock.org. I'd like to see your ratios; post the card.
