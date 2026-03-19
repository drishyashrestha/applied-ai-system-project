# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").
  -> The game looks simply as a guessing number game which generates random answer for each try.
-> First bug: There is a typeerror for some input, it takes in duplicate results & also invalid input reduces our attempt inspite getting being invalid like strings.
-> Second bug: New game button doesnot work meaning after winning a game it's infinitely showing "you won".
-> Third bug: Range doesn't show accurate one when switching difficulty or the actual answer is not within the range.
-> Fourth bug: Score is random as it's going up for incorrect guesses sometimes.

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
  Claude Code & Copilot
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
  Used claude code to refactor the type error lofic into logic utils and checked by passing the test cases 
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
  AI was not able to correctly suggest the remaining bugs and I had to point it out by running the app

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
-> I manually tried the app and testing my inputting invalid inputs and validating with my logic.
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
-> I ran the "python -m pytest" which showed 3 passed in 0.06s
- Did AI help you design or understand any tests? How?
-> Yes indeed, Claude created a new pytest  folder which I removed later as I already had a test folder.
---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
-> The secret number kept changing in the original app because
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
- What change did you make that finally gave the game a stable secret number?
-> for
```if "secret" not in st.session_state:         # line 86
    st.session_state.secret = random.randint(low, high)
```

This only generates a new secret when it's NOT already in session_state — so it's stable across reruns. BUT when you **switch difficulty**, `low` and `high` change to a different range while the old secret stays.
Store difficulty in session_state. On each rerun, compare. If changed → reset everything.
---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  -> Using git for tracking every step is crucial and using standard comments as well. 
- What is one thing you would do differently next time you work with AI on a coding task?
-> Through experience, I have learned to use plan mode first then execute or switch to agent mode which give better picture for both AI model and developer.
- In one or two sentences, describe how this project changed the way you think about AI generated code.
-> I think I got the glimpse of how new AI engineering would work or the entire way of engineering would change later as being proficient in using AI for developing is way efficient than coding yourself.
