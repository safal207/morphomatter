# Experiment 027 — Open-ended Material Universe

## Purpose

Explore whether MorphoMatter can discover classes of self-organizing virtual materials without a human preselecting the final material design.

This is not a claim of creating physical matter. It is a computational search over synthetic material laws and transition landscapes.

## Core question

Instead of asking:

"Which parameter values make this material work?"

ask:

"What classes of materials naturally emerge when the system explores a space of possible properties and interactions?"

## Search space

A virtual material genome may contain:

- particle properties;
- interaction rules;
- interface parameters;
- environment response;
- memory characteristics;
- anisotropy/directionality.

Example:

```
Material genome
    |
    +-- particle
    +-- interaction
    +-- interface
    +-- environment coupling
    +-- memory
```

## Evolutionary discovery loop

```
Generate materials
        |
        v
Simulate transitions
        |
        v
Measure structure + stability
        |
        v
Select promising systems
        |
        v
Mutate / recombine properties
        |
        v
New material candidates
```

## Fitness landscape

Avoid optimizing only for maximum order.

Candidate score should include:

```
Fitness =
(order * stability * adaptability)
/
(intervention + complexity)
```

Desired systems:

- organize naturally;
- remain stable;
- recover after perturbation;
- work across multiple environments.

## Open-ended discovery questions

1. Do different evolutionary runs converge to similar material classes?

2. Do unexpected combinations of properties outperform hand-designed systems?

3. Are there universal transition strategies across different material families?

4. Does causal discovery improve evolution speed?

## Connection to previous MorphoMatter layers

```
Material properties
        |
Environment
        |
Interaction landscape
        |
Transition surfaces
        |
Structure
        |
Memory
        |
Causal graph
        |
Active discovery
        |
Open-ended material search
```

## Interpretation boundary

Results would describe properties of a synthetic computational universe. They would not establish a real laboratory material without experimental validation.

## Future extension

Combine Experiment 027 with:

- causal material scientist;
- active experiment selection;
- world models;
- fractal transition analysis.

Goal:

Create a computational laboratory where AI discovers transition principles rather than only optimizing fixed recipes.
