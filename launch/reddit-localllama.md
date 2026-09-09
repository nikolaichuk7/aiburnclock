# r/LocalLLaMA

Title: Coding agent that answers "where is this in my code" with file and line, with the network cable unplugged: Ollama llama3.2:3b + a local index + 120 lines of Python

Body:
Retrieval 0.06–0.10 s, generation 3–8 s on a laptop, no cloud key, no telemetry. The trick is not the model; it is what the model reads. A local search engine (XERJ, Apache-2.0, single Rust binary, Elasticsearch-compatible API) indexes the folder once, the loop asks it "where", and the 3B model only ever sees the passage the pointer names instead of whole files. On my codebase that is 16–47× less text per answer than the grep-and-read approach, which is why a 3B model is enough for "where is X / how does Y work" questions.

Repo with the loop and a README: github.com/nikolaichuk7/xerj-offline. [GIF: Wi-Fi off, question, answer with file:line.]

This is the configuration a ship, an embassy, a hospital or a classified network needs; I built it to prove the point that the reading, not the model, is the cost.
