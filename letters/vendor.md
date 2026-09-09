# To an AI vendor's developer relations / partnerships (Anthropic, Cursor)

Subject: Your customers' reading bill, measured, and a plugin that cuts it

Dear {NAME},

Customers of {VENDOR} pay for every byte an agent loads into context. On a production codebase I measured 16 to 47 times more bytes read than used for the same answers when the agent searched by reading. A local index answering "where is it" first removed most of it. The AI Burn Clock (aiburnclock.org) publishes the method, the sources and the sliders; {VENDOR}'s published figure is in Table 1 with the scenario beside it.

The remedy is a plugin for {PRODUCT} (github.com/nikolaichuk7/xerj-plugins) built on an open-source local index (github.com/xerj-org/xerj). Customers who read less pay less per answer and run more answers; that is the argument for listing it in your directory and for a joint measurement on a public codebase. I can share the measurement script and run it on any repository you name.

Serhii Nikolaichuk, maintainer · hello@aiburnclock.org
