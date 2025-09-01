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
        self.character_db = {}
        self.alias_lookup = {}
        self.character_name_map = {}  # Maps underscored names to natural names
        self.load_character_database()

    def title(self):
        return "Character Tag Enhancer"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Group():
            with gr.Accordion("Character Tag Enhancer", open=False, elem_id="tag_enhancer_accordion"):
                gr.HTML("<p>Automatically replace character names with detailed tags</p>")
                
                with gr.Row():
                    enable_enhancement = gr.Checkbox(
                        label="Enable Tag Enhancement", 
                        value=True,
                        elem_id="tag_enhancer_enable"
                    )
                    keep_original = gr.Checkbox(
                        label="Keep Original Names", 
                        value=False,
                        elem_id="tag_enhancer_keep_original"
                    )
                    use_natural_names = gr.Checkbox(
                        label="Use Natural Names (spaces)", 
                        value=True,
                        elem_id="tag_enhancer_natural_names"
                    )
                
                with gr.Row():
                    reload_btn = gr.Button("Reload Database", variant="secondary")
                    test_btn = gr.Button("Test Enhancement", variant="primary")
                
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
                        value=f"<span style='color: green;'>✓ Loaded {len(self.character_db)} characters</span>",
                        elem_id="tag_enhancer_status"
                    )

                # Event handlers
                reload_btn.click(
                    fn=self.reload_database_ui,
                    outputs=[status_text]
                )
                
                test_btn.click(
                    fn=self.test_enhancement,
                    inputs=[test_input, enable_enhancement, keep_original, use_natural_names],
                    outputs=[test_output]
                )

        return [enable_enhancement, keep_original, use_natural_names]

    def before_process(self, p, enable_enhancement, keep_original, use_natural_names):
        """Called BEFORE the main processing - this is where we modify prompts"""
        print(f"[TAG ENHANCER] before_process called! Enable: {enable_enhancement}")
        
        if not enable_enhancement:
            print("[TAG ENHANCER] Enhancement disabled")
            return

        if not p.prompt:
            print("[TAG ENHANCER] No prompt to enhance")
            return

        original_prompt = p.prompt
        print(f"[TAG ENHANCER] Original prompt: {original_prompt}")
        
        # Enhance the prompt
        enhanced_prompt = self.enhance_tags(p.prompt, keep_original, use_natural_names)
        
        # CRITICAL: Update both prompt fields
        p.prompt = enhanced_prompt
        
        # Update all_prompts if it exists and has content
        if hasattr(p, 'all_prompts') and p.all_prompts:
            print(f"[TAG ENHANCER] Updating p.all_prompts: {p.all_prompts}")
            p.all_prompts = [enhanced_prompt] * len(p.all_prompts)
        
        if original_prompt != enhanced_prompt:
            print(f"[TAG ENHANCER] SUCCESS! Enhanced: {original_prompt[:50]}... -> {enhanced_prompt[:50]}...")
        else:
            print("[TAG ENHANCER] No changes made")

    def process(self, p, enable_enhancement, keep_original, use_natural_names):
        """Process method - kept for compatibility"""
        pass

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
        Check if all words from alias appear in tag in the same order (but can be separated)
        
        Examples:
        tag='red konan', alias='konan' → True (single word, anywhere)
        tag='konan red', alias='konan' → True (single word, anywhere)
        tag='naruko from konoha uzumaki', alias='naruko uzumaki' → True (multi-word, in order)
        tag='uzumaki naruko', alias='naruko uzumaki' → False (multi-word, wrong order)
        tag='akatsuki konan walking', alias='konan akatsuki' → False (wrong order)
        tag='akatsuki konan walking', alias='konan' → True (single word found)
        """
        if not alias.strip():
            return False
        
        alias_words = alias.split()
        
        # Single word alias: just check if it exists anywhere in tag
        if len(alias_words) == 1:
            return alias_words[0] in tag
        
        # Multiple words: must appear in order (but can be separated)
        search_start = 0
        for word in alias_words:
            # Look for this word starting from where we left off
            word_pos = tag.find(word, search_start)
            if word_pos == -1:
                return False  # Word not found
            # Update search position to after this word
            search_start = word_pos + len(word)
        
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

    def enhance_tags(self, prompt, keep_original=False, use_natural_names=True):
        """Enhanced tag processing with single replacement per character and generalized matching"""
        if not prompt:
            return prompt

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
                        print(f"[TAG ENHANCER] Replacing: '{tag}' -> '{char_key}' (matched alias: '{alias}')")
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
            return f"<span style='color: green;'>✓ Reloaded {len(self.character_db)} characters</span>"
        else:
            return "<span style='color: red;'>✗ Failed to reload database</span>"

    def test_enhancement(self, test_input, enable_enhancement, keep_original, use_natural_names):
        """Test tag enhancement"""
        if not enable_enhancement:
            return "Enhancement disabled"
        
        if not test_input:
            return "Enter character names to test"
        
        enhanced = self.enhance_tags(test_input, keep_original, use_natural_names)
        return enhanced