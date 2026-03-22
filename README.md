# Character Tag Enhancer Extension

## Description
Automatically replaces character names in prompts with detailed Danbooru-style tags/or Caption(default to danboru but you can activate the caption mode and it'll ignore the danbogu tags field and only use the caption field !) for consistent character generation.
(Work both on the Webui and as endpoint by Exemple if you had an app/website or anything make an api request to A111/forgeNeo to generate an image this extensions will still work and update the prompt before the image actually start generating so it should work in every situation smoothly.)

## Features
- Character alias support (multiple names for same character)
- JSON database for easy character management
- Web UI integration with toggle controls
- Test interface for tag enhancement
- Compatible with SillyTavern workflows or any kind of api call made to the webui
(Ignore the danboru tags it's because i'm using An image generation model that accept danboru tags and caption so even in caption mode I use those.)
<img width="1641" height="589" alt="image" src="https://github.com/user-attachments/assets/15625da9-0f5e-4575-9398-1ce6b26aec6d" />
As you can see in my danboru mode it can even inject Lora, honestly you can even use it for item,object and concept.
<img width="1604" height="570" alt="image" src="https://github.com/user-attachments/assets/a51671de-5fdd-416f-ac45-2a33dd58ed23" />



-A save setting button,Forge neo don't really natively support to turn on and off option easely, so every time you change any of the option on top you gotta save.

## Installation
1. Clone or download this extension to `stable-diffusion-webui/extensions/`
2. A already filled character file is included but you have to move it to your root installation stable-diffusion-webui/ or ForgeNEO/ or whatever your A1111 related root folder is, that's where the extensions look for it.
3. Restart AUTOMATIC1111 WebUI
4. Find "Character Tag Enhancer" section in generation interface
----
Disclaimer: Character manager app is a standalone app it don't need your image instance to be runned to be used but you can also use it as the same time as there is a refresh button 
<img width="3289" height="1246" alt="image" src="https://github.com/user-attachments/assets/f22f757c-2ea7-4e86-8b86-a00e13aeaa0f" />

To run it well just run character_manager.py(or run_app.bat same thing) you can move this folder somewhere else if u want too.
You can change the setting for the folder where it save the files and of course dowload it manually if needed.


## Usage
1. Enable "Enable Tag Enhancement" checkbox
2. Enter character names in prompt (e.g., "tsunade drinking sake")
3. Extension automatically replaces with detailed tags
4. Use test interface to preview enhancements

## Database Management
Edit `character_supplements.json` to add your own characters:
I added a character manager app ! but you can still edit the json manually using the right format

{
  "naruto_uzumaki": {
    "aliases": ["naruto", "naruto uzumaki"],
    "tags": "naruto_(series), 1boy, blonde hair, ninja",
    "caption": "Naruto Uzumaki looking determined"
  },
  "sasuke_uchiha": {
    "aliases": ["sasuke", "uchiha sasuke"],
    "tags": "naruto_(series), 1boy, black hair, sharingan"
  }
}

<img width="3293" height="1255" alt="image" src="https://github.com/user-attachments/assets/3334b3cc-dc9e-4635-80b3-2882063fc08a" />



