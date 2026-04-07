# NavBot-X Isaac Lab

NavBot-X Isaac Lab is the next-phase continuation of my robotics reinforcement learning journey, extending beyond my earlier Gazebo-based navigation project into a more advanced simulation, cinematic robotics demo, and Physical AI direction.

This repository is intentionally built as a **flagship robotics simulation project** from the beginning. The goal is not only to create meaningful technical infrastructure, but also to build a project that looks premium, futuristic, and portfolio-ready at first glance.

---

## Project Identity

- **Project:** NavBot-X Isaac Lab
- **Scene:** Aegis Inspection Bay
- **Vehicle:** NavBot-X Rover
- **Mission:** Inspection Route Alpha

---

## Overview

**Aegis Inspection Bay** is a futuristic industrial inspection facility where the **NavBot-X Rover** performs monitoring and traversal runs through a clean, high-tech environment.

The project is designed around a layered development strategy:

- **Phase 1:** flagship visual identity, simulator-side environment build, premium rover concept, cinematic scripted demo
- **Phase 2:** task logic, control structure, richer scene interaction, inspection workflow expansion
- **Phase 3:** reinforcement learning environments, advanced autonomy, embodied intelligence extensions, gesture-based interaction, and broader Physical AI experimentation

---

## Why This Repository Exists

This is a **new repository**, separate from my earlier Gazebo / ROS 2 navigation project, because:

- the previous project already reached a strong milestone
- this new stack deserves its own identity
- the Isaac Sim / Isaac Lab direction is more advanced and visually ambitious
- presentation quality and recruiter-facing clarity matter

This repo is intended to represent a **next-generation flagship simulation project**, not just another continuation branch.

---

## Long-Term Technology Direction

This project is being developed with the following long-term stack direction in mind:

- Isaac Sim
- Isaac Lab
- Omniverse workflows
- Newton physics directions
- robotics simulation pipelines
- reinforcement learning environments
- NVIDIA NeMo Curator and data-centric AI tooling
- physics-informed learning directions
- future gesture-based or interactive control modes
- broader Physical AI experimentation

---

## Phase 1 Scope

Phase 1 focuses on establishing the project’s premium visual and simulator-side foundation:

- premium project identity
- clean repository architecture
- Aegis Inspection Bay scene
- NavBot-X Rover flagship concept design
- omnidirectional / mecanum-style rover wheel styling
- cinematic camera system
- scripted Inspection Route Alpha demo
- strong GitHub and portfolio presentation baseline

---

## Phase 1 Highlights

Current Phase 1 features include:

- custom **Aegis Inspection Bay** simulator scene
- premium black / blue / gold visual language
- flagship **NavBot-X Rover** concept with omnidirectional-style wheel modules
- cinematic camera workflow:
  - Hero camera
  - Route camera
  - Top camera
- scripted demo route for **Inspection Route Alpha**
- colored lighting rig for a premium futuristic presentation
- Isaac Sim application entry point for scene launch and cinematic playback

---

## Current Scene Direction

The visual design of **Aegis Inspection Bay** is built around:

- dark premium floor surfaces
- clean route markings
- cyan / electric-blue guidance accents
- warm gold contrast highlights
- compact but intentional industrial scene composition
- high readability for cinematic camera views
- controlled visual complexity for an 8 GB laptop GPU

---

## NavBot-X Rover Design Direction

The **NavBot-X Rover** is designed as a premium inspection rover concept with:

- matte black base body
- graphite-black paneling
- restrained gold trim accents
- electric blue and cyan lighting language
- omnidirectional / mecanum-style wheel modules
- compact sensor mast and premium product silhouette
- cinematic product-demo presentation

---

## Current Repository Structure

```text
navbot-x-isaac-lab/
├── README.md
├── .gitignore
├── pyproject.toml
├── setup.py
├── LICENSE
├── config/
│   └── extension.toml
├── source/
│   └── navbot_x_isaac_lab/
│       ├── __init__.py
│       ├── apps/
│       │   ├── __init__.py
│       │   └── aegis_app.py
│       ├── demo/
│       │   ├── __init__.py
│       │   ├── aegis_scene_builder.py
│       │   ├── inspection_mission.py
│       │   ├── layout_blueprint.py
│       │   ├── route_animator.py
│       │   └── scene_config.py
│       ├── tasks/
│       │   ├── __init__.py
│       │   └── navigation/
│       │       ├── __init__.py
│       │       ├── navigation_env.py
│       │       ├── navigation_env_cfg.py
│       │       └── agents/
│       │           ├── __init__.py
│       │           └── rl_games_ppo_cfg.yaml
│       ├── robots/
│       │   ├── __init__.py
│       │   └── mobile_base/
│       │       └── __init__.py
│       └── utils/
│           ├── __init__.py
│           └── paths.py
├── scripts/
│   ├── run_aegis_app.py
│   ├── play.py
│   ├── sanity_check.py
│   └── train.py
├── assets/
│   ├── usd/
│   ├── configs/
│   ├── scenes/
│   └── robots/
├── docs/
│   └── architecture/
│       ├── mission_route_alpha.md
│       ├── phase1_plan.md
│       ├── scene_spec.md
│       └── visual_identity.md
├── media/
│   ├── demo_clips/
│   ├── images/
│   ├── renders/
│   └── videos/
├── logs/
├── checkpoints/
└── experiments/
```