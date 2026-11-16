# Ring Timer

A desktop app for running countdown timers side by side. Built with Python and GTK 3.
Each timer is a card with a circular progress ring that drains as time runs out and shifts from green to yellow to red along the way.

<img width="1075" height="778" alt="image" src="https://github.com/user-attachments/assets/faf5b5b2-9de9-42bc-abe9-61b4eae20bc4" />

## Requirements

- Python **3.10+**
- GTK 3 with PyGObject
- pycairo
- pygame

## Running from source

```bash
python3 src/main.py
```

When run from source, timers are saved to `src/save_file.json`.
