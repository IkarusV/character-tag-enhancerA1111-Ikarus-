# Character Tag Enhancer for AUTOMATIC1111
Interface:
<img width="1574" height="692" alt="image" src="https://github.com/user-attachments/assets/157b2312-d946-4c11-8505-647fb6820a45" />


Character list:
<img width="1251" height="513" alt="image" src="https://github.com/user-attachments/assets/e5e9337f-5aca-444c-a5fb-1119e235dad5" />

A powerful extension for AUTOMATIC1111 Stable Diffusion WebUI that automatically replaces character names in prompts with detailed Danbooru-style tags.

![Tag Enhancer Demo](https://img.shields.io/badge/AUTOMATIC1111-Extension-blue)
![Python](https://img.shields.io/badge/Python-3.7+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- **🎯 Smart Character Detection**: Detects character names anywhere in your prompt, even when surrounded by other words
- **🔧 Generalized Matching**: Matches "red konan" or "naruko from village uzumaki" automatically  
- **🛡️ Single Replacement**: Prevents duplicate character tag insertions in the same prompt
- **🌍 Natural Names**: Converts underscored names to natural spacing (konan_akatsuki → konan akatsuki)
- **📚 Extensive Database**: Pre-loaded with 100+ characters from Naruto, Fairy Tail, Food Wars, Avatar, and more
- **⚡ Real-time Testing**: Built-in test interface to verify tag enhancement before generation
- **🔄 Hot Reload**: Update character database without restarting AUTOMATIC1111

## 🚀 Installation

### Method 1: AUTOMATIC1111 Extension Manager (Recommended)

1. Open AUTOMATIC1111 WebUI
2. Go to **Extensions** tab
3. Click **Install from URL**
4. Enter: `https://github.com/IkarusV/character-tag-enhancerA1111-Ikarus-/tree/main`( I think...)
5. Click **Install**
6. ***Very important*** Put character_supplements.json in your *root stable diffusion webui forge folder*(You should find it in your extension folder, sorry for the hastle you can change it if you want in the extension i just got lazy to go into to many folder each time i wanted to change it.)
7. Restart AUTOMATIC1111
8. Tell me if it work for you.

### Method 2: Manual Installation

1. Navigate to your AUTOMATIC1111 directory
2. Open `extensions` folder
3. Clone this repository: git clone https://github.com/IkarusV/character-tag-enhancerA1111-Ikarus-/tree/main ( or just download the whole folder and put it in your extensions.)
4. ***Very important*** Move/put character_supplements.json into your root *stable diffusion webui forge folder*.
5. Restart AUTOMATIC1111
6. Tell me if it work for you !

## 🎮 Usage

### Basic Usage

1. **Enable the extension** in the Scripts dropdown at the bottom of the generation interface
2. **Write natural prompts** like:
- `"beautiful konan with blue hair"`
- `"naruko from village uzumaki eating ramen"`
- `"red hair tsunade in hokage robes"`
3. Thing get replaced, tsunade get replaced by her tags, if you have a hokage robes in your list, it'll also be replaced etc.

More details about the replacing feature below. 

🎯 Perfect for Story-Based AI Applications

Ideal for apps like SillyTavern, AI Roguelike, and other narrative AI tools that generate prompts for AUTOMATIC1111.
The Problem

When LLMs generate image prompts during stories, they mention character names ("D.Va adjusting her headset", "Naruto eating ramen") but don't know the proper visual tags needed for good image generation.
The Solution

This extension automatically converts character mentions into detailed personalised tags and lora, in my list it's mainly danbooru tags.

Key Benefits

    ✅ Works with ANY character: Anime, Game characters, or your custom OCs

    ✅ Works with ANY concept: Object, Location, Word, or any of your idea of it.

    ✅ Multiple characters per prompt: Each gets replaced with proper tags

    ✅ No prompt engineering needed: No need to cram character descriptions into system prompts

    ✅ LoRA-friendly: Perfect for custom characters with specific training

Use Cases

    Story RPGs: Characters appear naturally in generated scenes(Sillytavern, or even any thing that connect to A111.)

    Interactive Fiction: Dynamic character-based image generation

    Custom Character Stories: Your OCs get proper visual representation

    Multi-Character Scenes: Handle complex scenes with multiple characters seamlessly, don't replace tags more than once, is very flexible but avoid mistake as long as your alias as done correctly.

### Enhanced Matching Examples

| Input | Output |
|-------|--------|
| `red konan` | `konan, naruto_(series), 1girl, blue_hair, amber_eyes, paper_jutsu, akatsuki_member, detailed_face` |
| `naruko from village uzumaki` | `naruko uzumaki, naruto_(series), 1girl, blonde_hair, blue_eyes, long_hair, twintails, whisker_markings, orange_jumpsuit, detailed_face` |
| `tsunade the fifth hokage` | `tsunade, naruto_(series), 1girl, blonde_hair, large_breasts, hokage_robe, medical_ninja, amber_eyes, detailed_face, masterpiece` |

### Settings

- **Enable Tag Enhancement**: Turn the extension on/off
- **Keep Original Names**: Preserve original character names alongside detailed tags
- **Use Natural Names**: Convert underscores to spaces in output tags(May be only useful in very specific use cases, don't recommend using it if you don't need it. I use this with another one of my extension that use a open api compatible llm to convert thing into tags...that's why sometime i need this extensions.)

## 📊 Supported Characters

### Current personal Database Includes:

- **Naruto Series**: 25+ characters (Naruto, Sasuke, Sakura, Hinata, Tsunade, Konan, etc.)
- **Fairy Tail**: 10+ characters (Lucy, Erza, Wendy, Juvia, etc.)  
- **Food Wars**: 5+ characters (Erina, Alice, Megumi, etc.)
- **Avatar**: 8+ characters (Korra, Katara, Azula, Toph, etc.)
- **Custom Characters**: Easy to add your own, even object or places anything can be replaced or be an alias after all.

I'll include it just for an exemple or people wanna check if the extension work, but you can delete all of it and made one yourself just use the name files and structure when it come to name alias and all that, or just erase my characters and put yours, but know it won't work without it...it's possible to directly put character in the extension, but i found it very messy and choose to not do it.

## ⚙️ Configuration

### Adding Custom Characters(or then again object,location,anything that you want to be replaced.)

1. Edit `character_supplements.json` in the extension folder
2. Add your character following this format:

"character_key": {
"aliases": [
"character name",
"nickname",
"alternate name"
],
"tags": "character_name, series_name, 1girl, hair_color, eye_color, clothing, detailed_face, masterpiece"
},


### Example Character(Custom character same principle just put name and Alias and tags.)

  "oboro (taimanin asagi)": {
    "aliases": [
      "Oboro",
      "oboro taimanin",
      "Oboro Taimanin",
      "taimanin oboro",
      "Taimanin Oboro",
      "oboro from taimanin",
      "Oboro from Taimanin"
    ],
    "tags": "oboro \\(taimanin asagi\\), taimanin \\(series\\), 1girl, lips, purple hair, large breasts, thighs, sweat, lipstick,"
  },

  the rought format is:
  "character_key": {
"aliases": ["name1", "name2", "nickname"],
"tags": "character_name, series, 1girl/1boy, features, clothing, detailed_face"
},


## 🧪 Testing

Use the built-in test interface:

1. Open the extension settings
2. Enter test prompts in the **Test Input** field
3. Click **Test Enhancement** to see results
4. Adjust your character database as needed

## 🔧 Advanced Features

### Generalized Matching Logic

The extension uses smart matching rules:

- **Single words**: Match anywhere (`"konan"` matches both `"red konan"` and `"konan red"`)
- **Multi-words**: Must appear in order but can be separated (`"naruko uzumaki"` matches `"naruko from village uzumaki"`)
- **No fuzzy matching**: Eliminates false positives while maintaining flexibility

It's made that way to avoid mixing tags together as it only read each tags separed it's made only to enchant a tag list already made or simplify making one so you can store all of your character in one place, not having them all separed across multible website and app when it come to their appearance.

### Natural Name Conversion(Not really useful for most, just usefull for a llm pipeline eventually.)

Automatically converts:
- `naruko_uzumaki` → `naruko uzumaki`
- `konan_akatsuki` → `konan akatsuki`  
- `sailor_moon` → `sailor moon`

## 📁 File Structure

character-tag-enhancer/
├── tag_enhancer.py # Main extension script
├── character_supplements.json # Character database exemple,if you want to make a new files yourself make sure to give it the same name as this files.
├── README.md # This file
└── LICENSE # MIT License


## 🤝 Contributing

If you wanna help, add feature or have any opinion to make this better i'm all ears or even just sharing characters or even location or place I call it character but you can even use it to have all of your favorite lora packed in one word.:

1. **Add Characters**: Submit character database entries for popular anime, games, or comics
2. **Report Issues**: Found a bug? Create an issue with detailed reproduction steps
3. **Feature Requests**: I don't really plan to add anything, as I did it for my setup exactly and some feature could wrong my usecases but i'll be open to listen if people are interested in my extension !
4. **Code Improvements**: Submit pull requests with enhancements or fork me...dunno i'm new on github uploeading xD so maybe also explain to me if you know more than me xD.

### Character Submission Format

When submitting characters for other people or your own list, please follow this format:

"character_key": {
"aliases": ["name1", "name2", "nickname"],
"tags": "character_name, series, 1girl/1boy, features, clothing, detailed_face"
},


## 🐛 Troubleshooting

### Common Issues

**Extension doesn't appear in Scripts dropdown**
- Restart AUTOMATIC1111 after installation
- Check console for error messages

**Characters not being replaced**
- Verify character exists in `character_supplements.json`
- Test using the built-in test interface
- Check that enhancement is enabled

**Tags look wrong**
- Update character database entries
- Use "Test Enhancement" to verify output

### Getting Help

I'm not a pro, i'm stumbling arround out of stuborness but if I can help in a reasonable amount of effort and time, i'll be sure to give it a crack.

1. Check the Issues page
2. Create a new issue with:
   - Your input prompt
   - Expected vs actual output
   - Console error messages (if any)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- AUTOMATIC1111 team for Stable Diffusion WebUI
- Stability matrix team, their app helped me so much getting into local image generation.
- Danbooru community for tag standardization
- Me too lazy to replace tag myself and choosed to learn how to do all this.

## 🔗 Links

- [AUTOMATIC1111 WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- [Danbooru Tags](https://www.downloadmost.com/NoobAI-XL/danbooru-character/)

---
**Made for myself, to go with my own open ai compatible llm tag converter, it grab prompt even from api request so be it a game or sillytavern or anywhere that use A1111 should work in theory.**

***If somebody really want, i don't mind sharing my other extension that go really well with this one, it was basically made for it.***
