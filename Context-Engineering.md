- Context Engineering

It is the practice of designing systems to effectively supply LLMs with the right information, tools, and formatting, in the right way and at the right time, to successfully complete a task

- Mitigating and Avoiding Context Failures

- a. Context Poisoning: Hallucination or error makes it into context with repeated reference

- b. Context Distraction: Context is too long so model overfocuses on context neglecting previously learned during the training phase

- c. Context Confusion: Superfluous (Unnecessary/irrelevant) information in the context is used by the model and this generates a low quality response

- d. Context Clash: Accruing new information and tools in the context which contradicts with information already present in the prompt

- Note: It's all about Information Management and context influences the LLM output response

- Methods to Fix Context Failures

- 1. Context Offloading

It is the act of storing information outside the LLM's context using a tool/database to store and manage data

- 2. RAG (Retrieval Augmented Generation)

It is the act of selectively adding relevant information to help LLM generate a better response

- 3. Tool Loadout

It is the act of selecting only relevant tool definitions to add to your context

- 4. Context Pruning

It is the act of removing irrelevant, unneeded information from the context

- 5. Context Summarization

It is the act of combining the accrued context into a condensed memory

- 6. Context Quarantine

It is the act of isolating contexts into their dedicated threads each used separately by one or more LLM's 
- Note: Be Careful with Context Pruning and Context Summarization as information can be lost with these methods and it is difficult to retrace which information is lost in cases of vast amounts of data

