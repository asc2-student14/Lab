# API Reference

## Core Classes

### BaristBot

Main robot controller class.

```python
class BaristaBot:
    def __init__(self, config_path: str)
    def brew_coffee(self, recipe: str, size: str) -> bool
    def clean_system(self) -> bool
    def get_status(self) -> dict
```

#### Methods

**brew_coffee(recipe, size)**
- `recipe`: Recipe name (e.g., "espresso", "latte", "cappuccino")
- `size`: Cup size ("small", "medium", "large")
- Returns: `True` if successful, `False` if error

**clean_system()**
- Runs automated cleaning cycle
- Duration: ~5 minutes
- Returns: `True` when complete

**get_status()**
- Returns system status dictionary:
  - `beans_level`: Percentage of bean hopper (0-100)
  - `water_level`: Percentage of water reservoir (0-100)
  - `milk_level`: Percentage of milk reservoir (0-100)
  - `temperature`: Current boiler temperature (°C)
  - `grinder_status`: "ready" | "grinding" | "maintenance"

### RecipeManager

Handles coffee recipe definitions and customizations.

```python
class RecipeManager:
    def load_recipes(self, recipe_dir: str) -> bool
    def get_recipe(self, name: str) -> Recipe
    def validate_recipe(self, recipe: Recipe) -> bool
```

## Error Codes

- `E001`: Insufficient beans
- `E002`: Water reservoir empty
- `E003`: Grinder malfunction
- `E004`: Temperature too low
- `E005`: Milk reservoir empty