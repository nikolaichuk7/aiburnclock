# Show HN (post from Serhii's account, Wed morning 8–10am ET)

Title (80 chars max):
Show HN: I measured how much my coding agent reads vs. uses (16–47×), and a fix

URL: https://aiburnclock.org/

First comment (post immediately after submitting):

I asked a coding agent three ordinary questions on a production Next.js codebase ("where is the payment webhook signature verified?", "how does an owner cancel a subscription?", "what happens when a dish photo is uploaded?") and measured the bytes it pulled into context to answer each one, first the usual way (grep, open candidates, read them) and then with a local index answering "where is it" first.

Whole files behind the answers: 103,023 / 243,640 / 241,859 bytes. Through the index: 6,405 / 6,389 / 5,101 bytes. That is 16×, 38× and 47× less read for the same answers. The index was XERJ (open source, Apache-2.0, one Rust binary, Elasticsearch-compatible on port 9200); any index that returns passages instead of files should give the same effect.

The site prices the habit. The team table is four multiplications with every parameter on a slider; the world figure is Gartner's $2.59T AI spend forecast × three stated shares, labelled as a scenario, not a measurement. Table 1 applies the same factors to budgets that organisations published themselves (federal agencies, JPMorgan, Anthropic's run rate, Cursor), each row linked to its source. Treasury and USAspending figures are shown for scale and are not attributed to anything.

Things I'd like pushback on: the 63 % "avoidable share" comes from a published case study (2.7× fewer output tokens on real coding tasks, 1 − 1/2.7); my own three ratios would give 94–98 %, which I did not use. The inference share (25 %) and agent share (40 %) are estimates, and the sliders exist so you can argue with a factor rather than with me.

Everything is public: the pipeline and templates (github.com/nikolaichuk7/aiburnclock), data.json, the method page, and a Claude Code plugin that measures your own ratio at the end of every session (github.com/nikolaichuk7/xerj-plugins). Nothing leaves the machine; it counts bytes.
