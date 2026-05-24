# Contributing to Karmac Dashboard

First of all — thank you for your interest in contributing to Karmac! Every contribution, no matter how small, helps move the project forward.

---

## Who Can Contribute?

Everyone is welcome. You don't need to be an expert developer to contribute to Karmac. There are many ways to help:

- **Developers** — write code, fix bugs, build new panels
- **Designers** — improve the UI, suggest visual enhancements
- **Translators** — help bring Karmac to new languages
- **Testers** — run Karmac on different hardware and report issues
- **Writers** — improve documentation, guides, and the wiki
- **Ideas** — suggest features or improvements via GitLab Issues

---

## Code of Conduct

Karmac is a welcoming, inclusive project. We ask that all contributors:

- Be respectful and constructive in all communications
- Welcome newcomers and be patient with those still learning
- Focus on the project and its goals, not personal disagreements
- Give credit where credit is due

---

## Getting Started

### Prerequisites

Before contributing code, make sure you have the following installed:

- Python 3.10 or higher
- PySide6 (Qt for Python)
- Git

### Setting Up Your Development Environment

1. Fork the repository on GitLab
2. Clone your fork to your local machine:
   ```
   git clone https://gitlab.com/Team.Karmac/Karmac-dashboard.git
   ```
3. Navigate into the project directory:
   ```
   cd Karmac-dashboard
   ```
4. Install the required dependencies:
   ```
   pip install PySide6
   ```
5. Run Karmac locally to make sure everything works before making changes

---

## How to Submit a Contribution

### Reporting Bugs

1. Check GitLab Issues to make sure the bug hasn't already been reported
2. Open a new Issue with a clear title and description
3. Include your Linux distribution, desktop environment, and hardware where relevant
4. Steps to reproduce the bug are extremely helpful

### Suggesting Features

1. Open a new Issue and label it as a feature request
2. Describe the feature clearly — what it does and why it would benefit Karmac users
3. Check existing Issues first to avoid duplicates

### Submitting Code

1. Open an Issue first to discuss the change before writing code — this avoids wasted effort
2. Create a new branch for your change:
   ```
   git checkout -b feature/your-feature-name
   ```
3. Write clean, readable, well-commented Python code
4. Test your changes thoroughly before submitting
5. Submit a Merge Request (MR) with a clear description of what you changed and why
6. Reference the related Issue in your MR description

---

## Code Style Guidelines

- Follow PEP 8 Python style conventions
- Use clear, descriptive variable and function names
- Comment your code where the intent isn't immediately obvious
- Keep functions small and focused on a single task
- No unnecessary dependencies — keep Karmac lean

---

## Translations

Karmac launches in English and welcomes community translations. If you would like to translate Karmac into another language:

1. Open an Issue indicating which language you would like to add
2. We will provide guidance on how translation files are structured
3. All translators are credited within the application

---

## Questions?

If you have any questions, open an Issue on GitLab and label it as a question. We're happy to help.

---

*Thank you for helping make Karmac better for everyone.*

— Team Karmac