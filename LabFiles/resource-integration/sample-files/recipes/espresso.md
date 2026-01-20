# Recipe: Classic Espresso

## Ingredients
- 18g freshly ground espresso beans
- 30ml hot water (90-96°C)

## Instructions

1. **Grind beans** to fine consistency (grind setting: 3)
2. **Dose grounds** into portafilter (18g ±0.5g)
3. **Tamp grounds** with 30lbs pressure
4. **Lock portafilter** into group head
5. **Extract shot** for 25-30 seconds
6. **Target volume** 30ml (double shot)

## Quality Indicators

- **Color**: Rich golden-brown crema
- **Texture**: Thick, velvety crema layer
- **Aroma**: Intense, nutty fragrance
- **Taste**: Balanced sweetness and acidity

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Sour taste | Under-extraction | Finer grind, longer shot |
| Bitter taste | Over-extraction | Coarser grind, shorter shot |
| Weak crema | Stale beans | Use fresh beans (7-21 days old) |
| Too fast flow | Grind too coarse | Adjust to finer setting |

## Robot Parameters

```json
{
  "grind_setting": 3,
  "dose_weight": 18.0,
  "tamp_pressure": 30,
  "water_temperature": 93,
  "extraction_time": 27,
  "target_volume": 30
}
```