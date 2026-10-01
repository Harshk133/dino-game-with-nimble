



# 🦖 Chrome Dino AI — Local Decision Model Experiment

An experiment exploring whether **local AI decision models running through Ollama** can control the Chrome Dino game in real time.

## 🎥 Demo

Watch the AI controlling Chrome Dino:

[Demo.mp4](https://github.com/user-attachments/assets/e62de538-9fc5-45b3-acb7-abea1ec5e154)

The project combines:

- 🖥️ Chrome Dino
- 📸 PyAutoGUI for screen capture
- 👁️ OpenCV for obstacle detection
- 🧠 Ollama decision models
- 🤖 Nimble / Tev1
- ⌨️ PyAutoGUI for keyboard automation
- 🐍 Python

The main goal of this project is not simply to make the Dino jump.

The goal is to investigate an important question:

> **Can a local AI decision model make decisions quickly enough to control a real-time environment?**

---

# 🎯 Project Idea

The initial idea was simple:

```text
Chrome Dino
     ↓
Screenshot
     ↓
OpenCV
     ↓
Extract game state
     ↓
AI Decision Model
     ↓
JUMP / DUCK / WAIT
     ↓
Keyboard
```

The AI receives a structured representation of the game state instead of the raw screenshot.

For example:

```json
{
  "game": "Chrome Dino",
  "dino": {
    "on_ground": true,
    "jumping": false
  },
  "obstacle": {
    "type": "cactus",
    "distance": 288,
    "height": 58,
    "width": 28
  }
}
```

The model then selects an action:

```text
JUMP
DUCK
WAIT
```

---

# 🧱 Architecture

```text
                Chrome Dino
                     │
                     ▼
              PyAutoGUI Screenshot
                     │
                     ▼
                  OpenCV
                     │
                     ▼
             Obstacle Detection
                     │
                     ▼
                Game State
                     │
                     ▼
              Ollama Decision Model
                     │
              ┌──────┼──────┐
              ▼      ▼      ▼
            JUMP    DUCK   WAIT
              │
              ▼
          PyAutoGUI
              │
              ▼
         Chrome Dino
```

---

# 🧪 Phase 1 — Nimble

The first model tested was **Nimble**, a local decision model available through Ollama.

The reasoning behind choosing Nimble was straightforward:

> If the task is decision making rather than text generation, a specialized decision model should theoretically be a good fit.

The model was given a structured game state and asked to choose between:

```text
jump
duck
wait
```

## Nimble test

The measured request was:

```text
HTTP status: 200
Response time: 17636 ms
```

Approximately:

```text
17.6 seconds
```

Nimble correctly returned:

```json
{
  "choice": "jump"
}
```

However, the response arrived far too late for the game.

---

# ❌ Why Nimble Was Not Suitable for the Reflex Loop

Chrome Dino is a real-time environment.

Suppose the obstacle is detected at:

```text
distance = 288 px
```

The controller sends the state to Nimble:

```text
288 px → Nimble
```

But the model takes approximately:

```text
17.6 seconds
```

to respond.

By that time:

```text
Dino → Cactus → 💀
```

The model may still return:

```text
JUMP
```

but the decision is no longer useful.

This demonstrated an important principle:

> **A correct decision that arrives too late is effectively an incorrect decision in a real-time system.**

---

# 🔄 Why Switch From Nimble to Tev1?

The next question was:

> Is there a smaller/faster decision model that can perform the same task?

This led to testing **Tev1**.

The goal was not simply to find a model with better reasoning.

The goal was to find a model with a better **latency-to-decision tradeoff**.

---

# 🧠 Tev1 0.8B

The first Tev1 model tested was:

```text
tev1:0.8b
```

The model was running entirely on the RTX 5050 GPU:

```text
PROCESSOR: 100% GPU
```

Measured response:

```text
2525 ms
```

After simplifying the input:

```text
2347 ms
```

So the approximate latency was:

```text
~2.35 seconds
```

Compared with Nimble:

```text
Nimble:      ~17.6 seconds
Tev1 0.8B:   ~2.35 seconds
```

That is roughly a **7.5× reduction in measured response time** in this particular setup.

However, 2.35 seconds was still too slow for a real-time reflex controller.

---

# 🧪 Tev1 Decision Quality Test

Latency wasn't the only problem.

We also tested whether Tev1 changed its decision according to obstacle distance.

Test states:

```text
distance = 400
distance = 300
distance = 250
distance = 200
distance = 150
distance = 100
```

The results were:

```text
400 → JUMP
300 → JUMP
250 → JUMP
200 → JUMP
150 → JUMP
100 → JUMP
```

The model's confidence remained low:

```text
~0.12–0.14
```

This suggested that simply providing distance wasn't enough for the model to learn the game's timing relationship.

---

# 🧪 Tev1 4B Q4_K_M

We also tested:

```text
tev1:4b-q4_K_M
```

The measured response time was:

```text
73224 ms
```

Approximately:

```text
73.2 seconds
```

The model returned:

```text
JUMP
```

but the response time made it unusable for this application.

This was an important reminder:

> **A larger model is not automatically a better model for a specific real-time task.**

---

# 📊 Benchmark Results

These are **measurements from this project**, not universal benchmarks.

Hardware and software configuration can significantly affect inference performance.

| Model | Approx. Runtime Size | Measured Latency | Suitable for Real-Time Reflex? |
|---|---:|---:|---|
| Nimble 9B | ~10 GB runtime | **17.64 s** | ❌ |
| Tev1 0.8B | ~893 MB | **2.35 s** | ❌ |
| Tev1 4B Q4_K_M | ~2.7 GB | **73.22 s** | ❌ |

### Hardware used

```text
CPU: Intel Core 7 240H
GPU: NVIDIA GeForce RTX 5050
VRAM: 8 GB
RAM: 24 GB DDR5
Runtime: Ollama
OS: Windows
```

---

# 🔀 The Conditions for Switching Models

The decision to switch from Nimble to Tev1 was based on **application requirements**, not simply model popularity or parameter count.

The following conditions were considered.

## Condition 1 — Latency

For a real-time game:

```text
Decision latency << reaction window
```

If:

```text
model latency > available reaction time
```

the model should not be placed directly in the control loop.

For example:

```text
Obstacle detected
       ↓
Available reaction time: ~500 ms
       ↓
Model latency: 2.3 seconds
       ↓
Model is too slow
```

---

## Condition 2 — Decision Reliability

A model should not only respond quickly.

It should also produce useful decisions.

For example:

```text
distance = 400 → WAIT
distance = 200 → JUMP
```

is more useful than:

```text
distance = 400 → JUMP
distance = 300 → JUMP
distance = 200 → JUMP
distance = 100 → JUMP
```

A model that produces the same action regardless of meaningful state changes may not be suitable for the task.

---

## Condition 3 — Hardware Compatibility

Local inference depends heavily on:

- GPU VRAM
- GPU compute performance
- CPU performance
- RAM
- model size
- quantization
- context length
- runtime configuration

For example, this machine has:

```text
RTX 5050
8 GB VRAM
```

Tev1 0.8B was able to run:

```text
100% GPU
```

while the larger Nimble model was split between CPU and GPU.

Therefore, **model size and hardware compatibility are important considerations when selecting a local model.**

---

## Condition 4 — Task Complexity

A language/decision model is useful when the task actually requires reasoning.

Chrome Dino is different.

The decision space is extremely small:

```text
JUMP
DUCK
WAIT
```

The environment can be represented using only a few numerical values:

```text
distance
height
width
speed
dino position
```

This means using a multi-billion-parameter language model may be unnecessary for the final controller.

---

# 🧠 What I Learned

The biggest lesson from this experiment was:

> **AI capability and AI usability are different things.**

A model can make the correct decision but still fail at the application if the decision arrives too late.

For real-time agents, the important metric isn't just:

```text
"What answer did the model give?"
```

It is:

```text
"How quickly did the model give a useful answer?"
```

---

# ⚡ Current Controller

The project currently has a working fast controller based on OpenCV.

The simplified logic is:

```python
if distance <= JUMP_DISTANCE:
    jump()
```

This reacts much faster than the language-model-based controller.

The experiment demonstrated that deterministic logic is currently much better suited to the critical reflex loop.

---

# 🚀 Future Architecture

Instead of:

```text
OpenCV
   ↓
LLM
   ↓
Keyboard
```

the next architecture will be:

```text
                 Chrome Dino
                      ↓
                  OpenCV
                      ↓
               Game State
                      ↓
              Fast Controller
                      ↓
                  JUMP
```

with AI operating at a higher level:

```text
                  Tev1
                   ↓
          Strategy / Analysis
                   ↓
             Fast Controller
                   ↓
                 JUMP
```

This creates a **hybrid architecture**:

```text
┌──────────────────────────────┐
│       AI / Strategy Layer    │
│                              │
│          Tev1 / LLM          │
│                              │
└──────────────┬───────────────┘
               │
               │ high-level decisions
               ▼
┌──────────────────────────────┐
│       Real-Time Layer        │
│                              │
│ OpenCV + Fast Controller     │
│                              │
└──────────────┬───────────────┘
               │
               ▼
            PyAutoGUI
               │
               ▼
          Chrome Dino
```

---

# 🔬 Next Experiment

The next goal is to build a **tiny specialized AI controller** rather than using a general-purpose language model.

Possible input:

```text
distance
obstacle width
obstacle height
obstacle velocity
Dino Y position
Dino jump state
```

Output:

```text
WAIT
JUMP
DUCK
```

A tiny neural network could potentially perform this classification much faster than a 0.8B language model.

The experiment will then compare:

```text
Rule-based Controller
        vs
Tiny Neural Network
        vs
Tev1 0.8B
        vs
Nimble 9B
```

using metrics such as:

- Decision latency
- Survival time
- Number of obstacles cleared
- Decision accuracy
- CPU/GPU utilization

---

# 🏁 Conclusion

This project started with a simple question:

> **Can a local AI decision model play Chrome Dino?**

The answer is:

**Yes, technically — but model latency becomes the limiting factor.**

Nimble produced valid decisions but was too slow.

Tev1 0.8B was substantially faster but still too slow for the critical reflex loop.

Tev1 4B Q4_K_M was significantly slower in this particular setup.

The experiment therefore shifted from:

> **"Which LLM should control the Dino?"**

to:

> **"What is the smallest and fastest intelligent controller that can make useful real-time decisions?"**

And that's where the next phase of the project begins. 🚀

---

## 📁 Project Structure

```text
dino-game-with-nimble/
│
├── detect.py
│
├── dino_controller.py
│
├── nimble_agent.py
│
├── nimble_connection_test.py
│
├── tev1_connection_test.py
│
├── tev1_fast_test.py
│
├── tev1_distance_test.py
│
├── tev1_4b_test.py
│
├── requirements.txt
│
└── README.md
```

---

## 🛠️ Technologies

- Python
- OpenCV
- PyAutoGUI
- Requests
- Ollama
- Nimble
- Tev1
- Chrome Dino
- NVIDIA CUDA/GPU acceleration

---

## ⚠️ Disclaimer About Benchmarks

All latency numbers in this README were measured during this experiment on the listed hardware and software environment.

They should **not** be interpreted as official benchmarks for Nimble or Tev1.

Actual performance can vary depending on:

- Hardware
- GPU VRAM
- CPU
- Ollama version
- Model quantization
- Context size
- Background processes
- Drivers
- Operating system
- Model/runtime configuration

The purpose of the measurements is to compare the models **within this particular experiment and environment**.
