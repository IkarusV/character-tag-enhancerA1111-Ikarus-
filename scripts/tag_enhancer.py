import modules.scripts as scripts
import modules.shared as shared
import gradio as gr
import json
import os
import re

class TagEnhancerScript(scripts.Script):
    def __init__(self):
        self.extension_dir = scripts.basedir()
        self.db_file = os.path.join(self.extension_dir, "character_supplements.json")
        self.config_file = os.path.join(self.extension_dir, "tag_enhancer_config.json")
        self.character_db = {}
        self.alias_lookup = {}
        self.character_name_map = {}
        
        # Default settings
        self.settings = {
            "enabled": True,
            "keep_original": False,
            "use_natural_names": True,
            "use_caption_mode": False
        }
        
        self.load_settings()
        self.load_character_database()
    
    def title(self):
        return "Character Tag Enhancer"
    
    def show(self, is_img2img):
        return scripts.AlwaysVisible
    
    def ui(self, is_img2img):
        with gr.Group():
            with gr.Accordion("Character Tag Enhancer", open=False, elem_id="tag_enhancer_accordion"):
                gr.HTML("✨ Automatically replace character names with detailed tags")
                
                with gr.Row():
                    enable_enhancement = gr.Checkbox(
                        label="Enable Tag Enhancement",
                        value=self.settings["enabled"],
                        elem_id="tag_enhancer_enable"
                    )
                    
                    keep_original = gr.Checkbox(
                        label="Keep Original Names",
                        value=self.settings["keep_original"],
                        elem_id="tag_enhancer_keep_original"
                    )
                    
                    use_natural_names = gr.Checkbox(
                        label="Use Natural Names (spaces)",
                        value=self.settings["use_natural_names"],
                        elem_id="tag_enhancer_natural_names"
                    )
                    
                    use_caption_mode = gr.Checkbox(
                        label="Caption Mode",
                        value=self.settings.get("use_caption_mode", False),
                        elem_id="tag_enhancer_caption_mode"
                    )
                
                with gr.Row():
                    reload_btn = gr.Button("Reload Database", variant="secondary")
                    save_settings_btn = gr.Button("💾 Save Settings", variant="primary")
                    test_btn = gr.Button("Test Enhancement", variant="secondary")
                
                with gr.Row():
                    test_input = gr.Textbox(
                        label="Test Input",
                        placeholder="Try: red konan, naruko from village uzumaki, akatsuki konan",
                        lines=2,
                        elem_id="tag_enhancer_test_input"
                    )
                
                with gr.Row():
                    test_output = gr.Textbox(
                        label="Enhanced Output",
                        interactive=False,
                        lines=3,
                        elem_id="tag_enhancer_test_output"
                    )
                
                with gr.Row():
                    status_text = gr.HTML(
                        value=f"✓ Loaded {len(self.character_db)} characters",
                        elem_id="tag_enhancer_status"
                    )
                
                # Event handlers
                reload_btn.click(
                    fn=self.reload_database_ui,
                    outputs=[status_text]
                )
                
                save_settings_btn.click(
                    fn=self.save_settings_ui,
                    inputs=[enable_enhancement, keep_original, use_natural_names, use_caption_mode],
                    outputs=[status_text]
                )
                
                test_btn.click(
                    fn=self.test_enhancement,
                    inputs=[test_input, enable_enhancement, keep_original, use_natural_names, use_caption_mode],
                    outputs=[test_output]
                )
        
        return [enable_enhancement, keep_original, use_natural_names, use_caption_mode]
    
    def before_process(self, p, enable_enhancement, keep_original, use_natural_names, use_caption_mode):
        """Called BEFORE the main processing - this is where we modify prompts"""
        # Always reload settings to get current enabled state
        self.load_settings()
        actual_enabled = self.settings.get("enabled", True)
        actual_keep_original = self.settings.get("keep_original", False)
        actual_use_natural_names = self.settings.get("use_natural_names", True)
        actual_use_caption_mode = self.settings.get("use_caption_mode", False)
        
        print(f"[TAG ENHANCER] before_process called! Enable: {enable_enhancement}")
        print(f"[TAG ENHANCER] 🔥 Enabled from SETTINGS: {actual_enabled}")
        print(f"[TAG ENHANCER] Enabled from UI param: {enable_enhancement}")
        
        if not actual_enabled:
            print("[TAG ENHANCER] Enhancement disabled")
            return
        
        if not p.prompt:
            print("[TAG ENHANCER] No prompt to enhance")
            return
        
        original_prompt = p.prompt
        print(f"[TAG ENHANCER] Original prompt: {original_prompt}")
        
        enhanced_prompt = self.enhance_tags(p.prompt, actual_keep_original, actual_use_natural_names, actual_use_caption_mode)
        
        # CRITICAL: Update both prompt fields
        p.prompt = enhanced_prompt
        
        # Update all_prompts if it exists and has content
        if hasattr(p, 'all_prompts') and p.all_prompts:
            print(f"[TAG ENHANCER] Updating p.all_prompts: {p.all_prompts}")
            p.all_prompts = [enhanced_prompt] * len(p.all_prompts)
        
        if original_prompt != enhanced_prompt:
            print(f"[TAG ENHANCER] SUCCESS! Enhanced: {original_prompt[:50]}... → {enhanced_prompt[:50]}...")
        else:
            print("[TAG ENHANCER] No changes made")
    
    def process(self, p, enable_enhancement, keep_original, use_natural_names, use_caption_mode):
        """Process method - kept for compatibility"""
        pass
    
    def load_settings(self):
        """Load settings from config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
                print(f"[TAG ENHANCER] Loaded settings - Enabled: {self.settings.get('enabled', 'NOT SET')}")
        except Exception as e:
            print(f"[TAG ENHANCER] Error loading settings: {e}")
    
    def save_settings_ui(self, enable_enhancement, keep_original, use_natural_names, use_caption_mode):
        """Save settings and return status"""
        try:
            self.settings.update({
                "enabled": enable_enhancement,
                "keep_original": keep_original,
                "use_natural_names": use_natural_names,
                "use_caption_mode": use_caption_mode
            })
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
            
            print(f"[TAG ENHANCER] Settings saved - Enabled: {enable_enhancement}")
            return f"✅ Tag Enhancer settings saved! Enabled: {enable_enhancement}"
        except Exception as e:
            return f"❌ Failed to save settings: {e}"
    
    def load_character_database(self):
        """Load character database from JSON file"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                
                self.character_db = {}
                self.character_name_map = {}
                
                for key, value in raw_data.items():
                    if key.startswith('_'):  # Skip comments
                        continue
                    
                    if isinstance(value, dict) and 'aliases' in value:
                        self.character_db[key] = value
                        
                        # Create natural name mapping
                        natural_name = key.replace('_', ' ')
                        self.character_name_map[key] = natural_name
                
                self.build_alias_lookup()
                print(f"[TAG ENHANCER] Successfully loaded {len(self.character_db)} characters")
                return True
            else:
                print(f"[TAG ENHANCER] Database file not found: {self.db_file}")
                return False
        except Exception as e:
            print(f"[TAG ENHANCER] Error loading database: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def build_alias_lookup(self):
        """Build fast alias lookup table with normalization"""
        self.alias_lookup = {}
        
        for char_key, char_data in self.character_db.items():
            for alias in char_data.get('aliases', []):
                normalized = self.normalize_tag(alias)
                self.alias_lookup[normalized] = (char_key, char_data['tags'])
    
    def normalize_tag(self, tag):
        """Normalize tag by lowercasing and unifying underscores and spaces"""
        if not tag:
            return ""
        
        # Lowercase, strip, replace underscores with spaces, collapse multiple spaces
        normalized = tag.lower().strip()
        normalized = normalized.replace('_', ' ')
        normalized = re.sub(r'\s+', ' ', normalized)
        return normalized
    
    def is_generalized_match(self, tag, alias):
        """
        🔥 FIXED: Check if all words from alias appear in tag as COMPLETE WORDS in the same order
        
        Uses word boundaries to prevent partial matches like:
        - 'ino' matching inside 'voluminous' ❌
        - 'Amy' matching inside 'steamy' ❌
        
        Examples:
        tag='red konan', alias='konan' → True (single word, anywhere)
        tag='konan red', alias='konan' → True (single word, anywhere)
        tag='voluminous hair', alias='ino' → False (no complete word 'ino')
        tag='steamy bathroom', alias='amy' → False (no complete word 'amy')
        tag='naruko from konoha uzumaki', alias='naruko uzumaki' → True (multi-word, in order)
        tag='uzumaki naruko', alias='naruko uzumaki' → False (multi-word, wrong order)
        """
        if not alias.strip():
            return False
        
        alias_words = alias.split()
        
        # Single word alias: check if it exists as a complete word
        if len(alias_words) == 1:
            # Use word boundary regex to match complete words only
            pattern = r'\b' + re.escape(alias_words[0]) + r'\b'
            return re.search(pattern, tag) is not None
        
        # Multiple words: must appear in order as complete words (but can be separated)
        search_start = 0
        
        for word in alias_words:
            # Look for this word as a complete word starting from where we left off
            pattern = r'\b' + re.escape(word) + r'\b'
            match = re.search(pattern, tag[search_start:])
            
            if not match:
                return False  # Word not found as complete word
            
            # Update search position to after this word
            search_start = search_start + match.end()
        
        return True
    
    def find_character_match(self, tag):
        """Find character match using generalized matching allowing separated alias words"""
        tag_normalized = self.normalize_tag(tag)
        
        # Check each character to see if any aliases match
        for char_key, char_data in self.character_db.items():
            for alias in char_data.get('aliases', []):
                alias_normalized = self.normalize_tag(alias)
                
                if self.is_generalized_match(tag_normalized, alias_normalized):
                    print(f"[TAG ENHANCER] Generalized match: '{tag}' matched alias '{alias}' for character '{char_key}'")
                    return (char_key, char_data['tags'])
        
        return None
    
    def convert_to_natural_names(self, tags_string, use_natural_names=True):
        """Convert underscored character names to natural names"""
        if not use_natural_names:
            return tags_string
        
        result = tags_string
        
        for underscored_name, natural_name in self.character_name_map.items():
            # Use word boundaries to replace exact matches
            pattern = r'\b' + re.escape(underscored_name) + r'\b'
            result = re.sub(pattern, natural_name, result, flags=re.IGNORECASE)
        
        return result
    
    def enhance_tags(self, prompt, keep_original=False, use_natural_names=True, use_caption_mode=False):
        """Enhanced tag processing with single replacement per character and generalized matching"""
        if not prompt:
            return prompt
            
        if use_caption_mode:
            # Create a list of all valid alias-caption pairs
            replacements = []
            for char_key, char_data in self.character_db.items():
                caption = char_data.get('caption', '')
                if not caption or not str(caption).strip():
                    continue
                for alias in char_data.get('aliases', []):
                    if alias and str(alias).strip():
                        replacements.append((str(alias).strip(), str(caption).strip(), char_key))
            
            # Sort replacements by alias length descending
            replacements.sort(key=lambda x: len(x[0]), reverse=True)
            
            result_prompt = prompt
            matched_chars = set()
            
            for alias, caption, char_key in replacements:
                if char_key in matched_chars:
                    continue
                
                # Check for match (word boundaries, case-insensitive)
                pattern = r'\b' + re.escape(alias) + r'\b'
                if re.search(pattern, result_prompt, re.IGNORECASE):
                    print(f"[TAG ENHANCER] Caption Mode Replacing: '{alias}' → '{caption}'")
                    replacement_str = f"{alias}, {caption}" if keep_original else caption
                    # Use lambda to prevent re.sub from parsing backslashes in replacement_str
                    result_prompt = re.sub(pattern, lambda m: replacement_str, result_prompt, count=1, flags=re.IGNORECASE)
                    matched_chars.add(char_key)
            
            return result_prompt
        
        tags = [tag.strip() for tag in prompt.split(',')]
        enhanced_tags = []
        matched_characters = set()  # Track which characters have already been matched
        
        for tag in tags:
            if not tag:
                continue
            
            # Find the first character that matches this tag
            match = None
            tag_normalized = self.normalize_tag(tag)
            
            # Check all characters to see if any aliases match
            for char_key, char_data in self.character_db.items():
                # Skip if we've already matched this character
                if char_key in matched_characters:
                    continue
                
                # Check all aliases for this character
                for alias in char_data.get('aliases', []):
                    alias_normalized = self.normalize_tag(alias)
                    
                    if self.is_generalized_match(tag_normalized, alias_normalized):
                        match = (char_key, char_data['tags'])
                        matched_characters.add(char_key)  # Mark this character as matched
                        print(f"[TAG ENHANCER] Replacing: '{tag}' → '{char_key}' (matched alias: '{alias}')")
                        break
                
                if match:
                    break  # Stop looking once we found a match
            
            if match:
                char_key, replacement_tags = match
                
                if keep_original:
                    enhanced_tags.append(tag)
                
                replacement_list = [t.strip() for t in replacement_tags.split(',')]
                enhanced_tags.extend(replacement_list)
            else:
                enhanced_tags.append(tag)
        
        # Remove duplicates while preserving order
        seen = set()
        final_tags = []
        
        for tag in enhanced_tags:
            if tag and tag not in seen:
                seen.add(tag)
                final_tags.append(tag)
        
        result = ', '.join(final_tags)
        
        # Convert to natural names if requested
        if use_natural_names:
            result = self.convert_to_natural_names(result)
        
        return result
    
    def reload_database_ui(self):
        """Reload database and return status"""
        success = self.load_character_database()
        
        if success:
            return f"✓ Reloaded {len(self.character_db)} characters"
        else:
            return "✗ Failed to reload database"
    
    def test_enhancement(self, test_input, enable_enhancement, keep_original, use_natural_names, use_caption_mode):
        """Test tag enhancement"""
        if not enable_enhancement:
            return "Enhancement disabled"
        
        if not test_input:
            return "Enter character names to test"
        
        enhanced = self.enhance_tags(test_input, keep_original, use_natural_names, use_caption_mode)
        return enhanced
