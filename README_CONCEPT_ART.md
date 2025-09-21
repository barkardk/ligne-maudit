# Adding Concept Art to Your Maginot RPG

## Quick Setup

1. **Save your concept art** as PNG or JPG files in this folder:
   ```
   assets/images/backgrounds/
   ```

2. **Supported filenames** (the game will try these in order):
   - `maginot_concept.png`
   - `maginot_concept.jpg`
   - `bunker_exterior.png`
   - `ff9_style_bunker.png`

3. **Recommended specs**:
   - Resolution: 1024x768 (or higher, will be scaled)
   - Format: PNG for transparency, JPG for smaller files
   - Style: FF9 pre-rendered background aesthetic

## AI Art Generation Prompts

### For Midjourney/DALL-E:
```
Final Fantasy IX style pre-rendered background, concrete Maginot Line bunker exterior, grassy field, atmospheric lighting, painted textures, game environment art, 1024x768 aspect ratio
```

### For Stable Diffusion:
```
ff9 style, final fantasy ix, pre-rendered background, maginot line bunker, concrete fortification, grassy landscape, atmospheric perspective, warm lighting, detailed painted textures, game art, high detail
Negative: blurry, low quality, modern, futuristic
```

## File Organization

```
maginot_rpg/
├── assets/
│   ├── images/
│   │   └── backgrounds/
│   │       ├── maginot_concept.png     <- Put your AI art here
│   │       ├── bunker_exterior.jpg     <- Alternative filename
│   │       └── ...
│   ├── backgrounds/
│   │   ├── maginot_exterior.py         <- Procedural fallback
│   │   └── image_loader.py             <- Handles loading
```

## How It Works

1. **Game starts** → Checks for concept art files
2. **If found** → Loads and scales to 1024x768
3. **If not found** → Uses procedural background as fallback
4. **Optional** → Can blend concept art with procedural elements

## Tips

- **Test different ratios**: The game will scale your art to fit
- **Keep originals**: Save high-res versions for future use
- **Layer approach**: You can blend AI art with procedural elements
- **Multiple versions**: Try different lighting/time of day versions

## Next Steps

1. Generate concept art using AI tools
2. Save to `assets/images/backgrounds/maginot_concept.png`
3. Run the game - it will automatically use your art!
4. Iterate and refine based on how it looks in-game