# Using SNES/PS1 Sprite Sheets in Your Maginot RPG

## Quick Setup

1. **Save your sprite sheet** as a PNG file in:
   ```
   assets/images/sprites/
   ```

2. **Supported filenames** (the game will try these automatically):
   - `protagonist.png` (recommended)
   - `character.png`
   - `player.png`
   - `hero.png`
   - `main_character.png`

3. **Common SNES/PS1 frame sizes** (auto-detected):
   - 16x24 pixels (small SNES style)
   - 24x32 pixels (medium)
   - 32x32 pixels (square)
   - 32x48 pixels (tall)
   - 48x48 pixels (larger)

## Sprite Sheet Layout

The system expects a standard RPG sprite sheet layout:

```
Row 0: [Walk Down 1] [Walk Down 2] [Walk Down 3] [Walk Down 4]
Row 1: [Walk Left 1] [Walk Left 2] [Walk Left 3] [Walk Left 4]
Row 2: [Walk Right 1] [Walk Right 2] [Walk Right 3] [Walk Right 4]
Row 3: [Walk Up 1] [Walk Up 2] [Walk Up 3] [Walk Up 4]
```

## Features

### **Automatic Detection:**
- Tries multiple common filenames
- Auto-detects frame sizes
- Extracts walking animations for all 4 directions
- Scales sprites 4x for visibility

### **Animation States:**
- `idle`: Standing still (uses first down-facing frame)
- `walk_down`: Walking down animation
- `walk_left`: Walking left animation
- `walk_right`: Walking right animation
- `walk_up`: Walking up animation

### **Smart Fallback:**
- If no sprite sheet found, uses procedural sprites
- Maintains same animation interface
- No code changes needed

## Examples of Compatible Sprite Sheets

### **Final Fantasy Style:**
- 16x24 or 24x32 pixel frames
- 4-frame walking cycles
- Standard directional layout

### **Secret of Mana Style:**
- 24x32 or 32x32 pixel frames
- Smooth walking animations
- Character facing 4 directions

### **Chrono Trigger Style:**
- 24x32 pixel frames
- Detailed character sprites
- Classic JRPG animation

## Testing Your Sprite Sheet

1. Place your sprite sheet in `assets/images/sprites/protagonist.png`
2. Run the game
3. Look for console message: "Using sprite sheet for protagonist animations"
4. Character should now use your custom animations!

## Troubleshooting

### **If sprite sheet isn't loading:**
- Check filename matches exactly
- Ensure PNG format
- Verify sprite sheet is in correct directory
- Look at console messages for details

### **If animations look wrong:**
- Try different frame sizes in the code
- Check sprite sheet layout matches expected format
- Ensure frames are evenly spaced

### **Custom Frame Sizes:**
If your sprite sheet uses different dimensions, edit:
```python
frame_sizes = [
    (your_width, your_height),  # Add your custom size
    # ... existing sizes
]
```

## Advanced Usage

### **Custom Animation Sequences:**
You can modify the loader to extract different animation patterns:

```python
# Custom animation extraction
attack_frames = sprite_sheet.get_animation_frames(0, 4, 3, 'horizontal')
animation_manager.add_animation('attack', attack_frames, speed=100)
```

### **Multiple Character Sheets:**
- Add more character files with different names
- System will use first one found
- Fallback to procedural if none available

The system is designed to work with most standard SNES/PS1 RPG sprite sheets out of the box!