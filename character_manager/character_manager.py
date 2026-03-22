import gradio as gr
import json
import os
import sys
from datetime import datetime
import copy
from collections import OrderedDict

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class CharacterManager:
    def __init__(self):
        self.character_data = {}
        
        # 🔥 All 3 save locations
        self.path_a1111 = r"C:\Aithing\Image generation\Data\Packages\Stable Diffusion WebUI Forge - Neo\character_supplements.json"
        self.path_comfyui = r"C:\Aithing\Image generation\Data\Packages\ComfyUI\character_supplements.json"
        self.path_local = r"C:\Aithing\character_manager\character_supplements.json"
        
        # Default primary path (A1111)
        self.primary_path = self.path_a1111
        self.current_file = self.primary_path if os.path.exists(self.primary_path) else self.path_local
        self.backup_data = {}
    
    def load_json_file(self, file_path):
        """Load character data from JSON file"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.character_data = json.load(f, object_pairs_hook=OrderedDict)
                self.backup_data = copy.deepcopy(self.character_data)
                self.current_file = file_path
                char_count = len([k for k in self.character_data.keys() if not k.startswith('_')])
                return f"✅ Loaded {char_count} characters from {file_path}"
            else:
                return f"❌ File not found: {file_path}"
        except Exception as e:
            return f"❌ Error loading file: {str(e)}"
    
    def save_json_file(self, file_path, create_backup=False):
        """Save character data to single JSON file
        
        Args:
            file_path: Path to save the JSON file
            create_backup: If True, create a backup before saving (only for local folder)
        """
        try:
            # Only create backups if requested (local folder only)
            if create_backup and os.path.exists(file_path):
                backup_path = f"{file_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                with open(file_path, 'r', encoding='utf-8') as f:
                    backup_content = f.read()
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(backup_content)
                
                # Cleanup: keep only 2 most recent backups
                self._cleanup_old_backups(file_path, max_backups=2)
            
            file_dir = os.path.dirname(file_path)
            if file_dir and not os.path.exists(file_dir):
                os.makedirs(file_dir)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.character_data, f, indent=2, ensure_ascii=False)
            
            self.current_file = file_path
            character_count = len([k for k in self.character_data.keys() if not k.startswith('_')])
            return f"✅ Saved {character_count} characters to {os.path.basename(file_path)}"
        except Exception as e:
            return f"❌ Error saving file: {str(e)}"
    
    def _cleanup_old_backups(self, file_path, max_backups=2):
        """Remove old backup files, keeping only the most recent ones"""
        try:
            backup_dir = os.path.dirname(file_path) or '.'
            base_name = os.path.basename(file_path)
            
            # Find all backup files for this JSON
            backup_files = []
            for f in os.listdir(backup_dir):
                if f.startswith(base_name + ".backup."):
                    full_path = os.path.join(backup_dir, f)
                    backup_files.append((full_path, os.path.getmtime(full_path)))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Delete old backups beyond the limit
            for old_backup, _ in backup_files[max_backups:]:
                os.remove(old_backup)
        except Exception:
            pass  # Silently ignore cleanup errors
    
    def save_to_all_locations(self):
        """🔥 NEW: Save to all 3 locations (A1111, ComfyUI, Local)"""
        results = []
        
        # Save to A1111
        try:
            result_a1111 = self.save_json_file(self.path_a1111)
            results.append(f"📂 A1111: {result_a1111}")
        except Exception as e:
            results.append(f"📂 A1111: ❌ {str(e)}")
        
        # Save to ComfyUI
        try:
            result_comfyui = self.save_json_file(self.path_comfyui)
            results.append(f"📂 ComfyUI: {result_comfyui}")
        except Exception as e:
            results.append(f"📂 ComfyUI: ❌ {str(e)}")
        
        # Save to Local (with backup)
        try:
            result_local = self.save_json_file(self.path_local, create_backup=True)
            results.append(f"📂 Local: {result_local}")
        except Exception as e:
            results.append(f"📂 Local: ❌ {str(e)}")
        
        return "\n".join(results)
    
    def save_to_a1111(self):
        """Save only to A1111"""
        return self.save_json_file(self.path_a1111)
    
    def save_to_comfyui(self):
        """🔥 NEW: Save only to ComfyUI"""
        return self.save_json_file(self.path_comfyui)
    
    def save_to_local(self):
        """Save only to local folder (with backup)"""
        return self.save_json_file(self.path_local, create_backup=True)
    
    def get_character_list(self, search_query=""):
        """Generate formatted character list for display with search filter"""
        if not self.character_data:
            return "No characters loaded. Please load a JSON file or create a new one."
        
        lines = []
        search_lower = search_query.lower() if search_query else ""
        
        for key, value in self.character_data.items():
            if key.startswith('_comment'):
                category_name = value.replace('=', '').strip()
                lines.append(f"\n## 📁 {category_name}\n")
            elif key.startswith('_template'):
                continue
            else:
                if search_lower:
                    key_match = search_lower in key.lower()
                    alias_match = any(search_lower in alias.lower() for alias in value.get("aliases", []))
                    tag_match = search_lower in value.get("tags", "").lower()
                    if not (key_match or alias_match or tag_match):
                        continue
                
                aliases = ", ".join(value.get("aliases", []))
                tags = value.get("tags", "")
                lines.append(f"### 👤 **{key}**")
                lines.append(f"**Aliases:** {aliases}")
                lines.append(f"**Tags:** {tags[:150]}{'...' if len(tags) > 150 else ''}")
                lines.append("---")
        
        return "\n".join(lines) if lines else "No characters found matching your search."
    
    def get_categories(self):
        """Get list of category names for dropdown"""
        categories = [("📁 At Beginning", "_beginning")]
        
        for key, value in self.character_data.items():
            if key.startswith('_comment'):
                category_name = value.replace('=', '').strip()
                categories.append((f"📁 {category_name}", key))
        
        categories.append(("📁 At End", "_end"))
        return categories
    
    def get_category_list_for_deletion(self):
        """🔥 NEW: Get list of categories for deletion dropdown"""
        categories = []
        
        for key, value in self.character_data.items():
            if key.startswith('_comment') and not key.startswith('_comment_header') and not key.startswith('_comment_usage'):
                category_name = value.replace('=', '').strip()
                categories.append((f"📁 {category_name}", key))
        
        return categories if categories else [("No categories to delete", "")]
    
    def add_character(self, name, aliases, tags, caption="", category="_end"):
        """Add a new character under specified category"""
        if not name.strip():
            return "❌ Character name is required"
        
        name = name.strip()
        
        if name in self.character_data:
            return f"❌ Character '{name}' already exists"
        
        alias_list = [alias.strip() for alias in aliases.split(',') if alias.strip()]
        if not alias_list:
            alias_list = [name]
        
        new_character = {
            "aliases": alias_list,
            "tags": tags.strip(),
            "caption": caption.strip()
        }
        
        if category == "_beginning":
            new_data = OrderedDict()
            new_data[name] = new_character
            new_data.update(self.character_data)
            self.character_data = new_data
        elif category == "_end":
            self.character_data[name] = new_character
        else:
            new_data = OrderedDict()
            found_category = False
            
            for key, value in self.character_data.items():
                new_data[key] = value
                
                if key == category and not found_category:
                    new_data[name] = new_character
                    found_category = True
            
            if not found_category:
                new_data[name] = new_character
            
            self.character_data = new_data
        
        return f"✅ Added character '{name}' with {len(alias_list)} aliases"
    
    def edit_character(self, old_name, new_name, aliases, tags, caption=""):
        """Edit an existing character"""
        if not old_name.strip():
            return "❌ Original character name is required"
        
        old_name = old_name.strip()
        new_name = new_name.strip() if new_name.strip() else old_name
        
        if old_name not in self.character_data:
            return f"❌ Character '{old_name}' not found"
        
        alias_list = [alias.strip() for alias in aliases.split(',') if alias.strip()]
        if not alias_list:
            alias_list = [new_name]
        
        new_data = OrderedDict()
        
        for key, value in self.character_data.items():
            if key == old_name:
                new_data[new_name] = {
                    "aliases": alias_list,
                    "tags": tags.strip(),
                    "caption": caption.strip()
                }
            elif key == new_name and old_name != new_name:
                return f"❌ Character '{new_name}' already exists"
            else:
                new_data[key] = value
        
        self.character_data = new_data
        return f"✅ Updated character '{new_name}'"
    
    def delete_character(self, name):
        """Delete a character"""
        if not name.strip():
            return "❌ Character name is required"
        
        name = name.strip()
        
        if name not in self.character_data:
            return f"❌ Character '{name}' not found"
        
        del self.character_data[name]
        return f"✅ Deleted character '{name}'"
    
    def add_category(self, category_name, position="end"):
        """Add a category comment"""
        if not category_name.strip():
            return "❌ Category name is required"
        
        comment_key = f"_comment_{category_name.lower().replace(' ', '_')}"
        comment_value = f"===== {category_name.upper()} ====="
        
        if position == "end":
            self.character_data[comment_key] = comment_value
        else:
            new_data = OrderedDict()
            new_data[comment_key] = comment_value
            new_data.update(self.character_data)
            self.character_data = new_data
        
        return f"✅ Added category '{category_name}'"
    
    def delete_category(self, category_key):
        """🔥 NEW: Delete a category comment"""
        if not category_key or category_key not in self.character_data:
            return "❌ Category not found"
        
        if not category_key.startswith('_comment'):
            return "❌ Can only delete category comments"
        
        category_name = self.character_data[category_key].replace('=', '').strip()
        del self.character_data[category_key]
        
        return f"✅ Deleted category '{category_name}'"
    
    def get_character_names(self):
        """Get list of character names for dropdown"""
        return [key for key in self.character_data.keys() if not key.startswith('_')]
    
    def get_character_details(self, name):
        """Get character details for editing"""
        if not name or name not in self.character_data:
            return "", "", "", ""
        
        char_data = self.character_data[name]
        aliases = ", ".join(char_data.get("aliases", []))
        tags = char_data.get("tags", "")
        caption = char_data.get("caption", "")
        return name, aliases, tags, caption
        
    def upgrade_database_with_captions(self):
        """🔥 NEW: Add empty 'caption' field to all existing characters if missing"""
        if not self.character_data:
            return "❌ No characters loaded to upgrade."
            
        count = 0
        for key, value in self.character_data.items():
            if not key.startswith('_') and isinstance(value, dict):
                if 'caption' not in value:
                    value['caption'] = ""
                    count += 1
        return f"✅ Upgraded {count} characters with missing 'caption' fields. Remember to save!"
    
    def export_data(self):
        """Export character data as JSON string"""
        try:
            return json.dumps(self.character_data, indent=2, ensure_ascii=False)
        except Exception as e:
            return f"Error exporting data: {str(e)}"
    
    def import_data(self, json_text, category="_end"):
        """Import character data from JSON string"""
        try:
            imported_data = json.loads(json_text, object_pairs_hook=OrderedDict)
            
            for key, value in imported_data.items():
                if not key.startswith('_') and isinstance(value, dict):
                    if 'aliases' not in value or 'tags' not in value:
                        return f"❌ Invalid structure for character '{key}'"
            
            conflicts = []
            for key in imported_data.keys():
                if key in self.character_data and not key.startswith('_'):
                    conflicts.append(key)
            
            if conflicts:
                return f"❌ Conflicts with existing characters: {', '.join(conflicts[:5])}"
            
            if category == "_end":
                self.character_data.update(imported_data)
            elif category == "_beginning":
                new_data = OrderedDict()
                new_data.update(imported_data)
                new_data.update(self.character_data)
                self.character_data = new_data
            else:
                new_data = OrderedDict()
                found_category = False
                
                for key, value in self.character_data.items():
                    new_data[key] = value
                    
                    if key == category and not found_category:
                        new_data.update(imported_data)
                        found_category = True
                
                if not found_category:
                    new_data.update(imported_data)
                
                self.character_data = new_data
                
            char_count = len([k for k in imported_data.keys() if not k.startswith('_')])
            return f"✅ Imported {char_count} characters successfully"
        except json.JSONDecodeError:
            return "❌ Invalid JSON format"
        except Exception as e:
            return f"❌ Import error: {str(e)}"

# Initialize the character manager
manager = CharacterManager()

# Try to load from A1111 first
if os.path.exists(manager.path_a1111):
    default_status = manager.load_json_file(manager.path_a1111)
elif os.path.exists(manager.path_local):
    default_status = manager.load_json_file(manager.path_local)
else:
    default_status = "⚠️ No existing files found. Create new database or load file."

def create_ui():
    with gr.Blocks(title="Character Database Manager", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🎭 Character Database Manager")
        gr.Markdown("**Syncs to 3 locations:** A1111 (Primary) | ComfyUI | Local Backup")
        
        with gr.Tab("📋 Character List & Search"):
            with gr.Row():
                with gr.Column(scale=2):
                    search_box = gr.Textbox(
                        label="🔍 Search Characters",
                        placeholder="Search by name, alias, or tags...",
                        elem_id="search_box"
                    )
                    
                    character_display = gr.Markdown(
                        value=manager.get_character_list(),
                        label="Characters"
                    )
                
                with gr.Column(scale=1):
                    gr.Markdown("### 🔄 Actions")
                    refresh_btn = gr.Button("🔄 Refresh List", variant="secondary")
                    clear_search_btn = gr.Button("🗑️ Clear Search", variant="secondary")
                    
                    gr.Markdown("### 💾 Quick Save")
                    # 🔥 Save to all 3 locations
                    save_all_btn = gr.Button("⚡ Save to ALL (A1111 + ComfyUI + Local)", variant="primary", size="lg")
                    
                    with gr.Row():
                        save_a1111_btn = gr.Button("💾 A1111", variant="secondary")
                        save_comfyui_btn = gr.Button("💾 ComfyUI", variant="secondary")
                        save_local_btn = gr.Button("💾 Local", variant="secondary")
                    
                    gr.Markdown("### � Download")
                    download_btn = gr.Button("📥 Download character_supplements.json", variant="primary", size="lg")
                    download_file = gr.File(label="Download Ready", visible=False)
                    
                    gr.Markdown("### �📁 File Operations")
                    file_path = gr.Textbox(
                        value=manager.current_file,
                        label="Current File",
                        placeholder="Enter JSON file path",
                        interactive=True
                    )
                    load_btn = gr.Button("📂 Load File", variant="secondary")
                    save_custom_btn = gr.Button("💾 Save to Custom Path", variant="secondary")
                    new_file_btn = gr.Button("📄 New File", variant="secondary")
                    
                    file_status = gr.Textbox(
                        value=default_status,
                        label="Status",
                        interactive=False,
                        lines=4
                    )
        
        with gr.Tab("➕ Add Character"):
            gr.Markdown("### Add New Character")
            with gr.Row():
                with gr.Column():
                    add_name = gr.Textbox(label="Character Name", placeholder="e.g., sasuke_uchiha")
                    add_aliases = gr.Textbox(
                        label="Aliases (comma-separated)",
                        placeholder="e.g., sasuke, uchiha sasuke, sasuke from naruto",
                        lines=2
                    )
                    add_tags = gr.Textbox(
                        label="Tags",
                        lines=4,
                        placeholder="e.g., sasuke_uchiha, naruto_(series), 1boy, black_hair, ninja, detailed_face"
                    )
                    add_caption = gr.Textbox(
                        label="Caption (Optional)",
                        lines=2,
                        placeholder="e.g., 1boy, sasuke uchiha, looking at viewer"
                    )
                    
                    add_category = gr.Dropdown(
                        choices=manager.get_categories(),
                        label="📁 Add to Category",
                        value="_end",
                        interactive=True
                    )
                    
                    refresh_categories_btn = gr.Button("🔄 Refresh Categories", variant="secondary", size="sm")
                    
                    with gr.Row():
                        add_btn = gr.Button("➕ Add Character", variant="primary")
                        add_save_all_btn = gr.Button("➕💾 Add & Save ALL", variant="primary")
                    
                    add_status = gr.Textbox(label="Status", interactive=False, lines=3)
        
        with gr.Tab("✏️ Edit Character"):
            gr.Markdown("### Edit Existing Character")
            with gr.Row():
                with gr.Column():
                    edit_select = gr.Dropdown(
                        choices=manager.get_character_names(),
                        label="Select Character to Edit",
                        interactive=True,
                        allow_custom_value=False
                    )
                    
                    with gr.Row():
                        load_char_btn = gr.Button("📥 Load Character", variant="secondary", scale=2)
                        refresh_dropdown_btn = gr.Button("🔄 Refresh", variant="secondary", scale=1)
                    
                    edit_name = gr.Textbox(label="Character Name")
                    edit_aliases = gr.Textbox(label="Aliases (comma-separated)", lines=2)
                    edit_tags = gr.Textbox(label="Tags", lines=4)
                    edit_caption = gr.Textbox(label="Caption (Optional)", lines=2)
                    
                    with gr.Row():
                        edit_btn = gr.Button("✏️ Update Character", variant="primary")
                        delete_btn = gr.Button("🗑️ Delete Character", variant="stop")
                    
                    edit_save_all_btn = gr.Button("✏️💾 Update & Save ALL", variant="primary")
                    
                    edit_status = gr.Textbox(label="Status", interactive=False, lines=3)
        
        with gr.Tab("📁 Categories"):
            gr.Markdown("### Manage Categories")
            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### ➕ Add Category")
                    category_name = gr.Textbox(label="Category Name", placeholder="e.g., Anime Characters")
                    category_position = gr.Radio(
                        choices=["end", "beginning"],
                        value="end",
                        label="Insert Position"
                    )
                    add_category_btn = gr.Button("📁 Add Category", variant="primary")
                    
                    gr.Markdown("---")
                    
                    # 🔥 NEW: Delete category section
                    gr.Markdown("#### 🗑️ Delete Category")
                    delete_category_select = gr.Dropdown(
                        choices=manager.get_category_list_for_deletion(),
                        label="Select Category to Delete",
                        interactive=True
                    )
                    
                    with gr.Row():
                        refresh_delete_list_btn = gr.Button("🔄 Refresh List", variant="secondary")
                        delete_category_btn = gr.Button("🗑️ Delete Category", variant="stop")
                    
                    category_status = gr.Textbox(label="Status", interactive=False, lines=3)
        
        with gr.Tab("⚙️ Settings"):
            gr.Markdown("### File Paths Configuration")
            with gr.Row():
                with gr.Column():
                    a1111_path_display = gr.Textbox(
                        label="🎯 A1111 Extension Path",
                        value=manager.path_a1111,
                        interactive=True
                    )
                    
                    comfyui_path_display = gr.Textbox(
                        label="🎯 ComfyUI Extension Path",
                        value=manager.path_comfyui,
                        interactive=True
                    )
                    
                    local_path_display = gr.Textbox(
                        label="🎯 Local Backup Path",
                        value=manager.path_local,
                        interactive=True
                    )
                    
                    with gr.Row():
                        update_paths_btn = gr.Button("💾 Update Paths", variant="primary")
                        test_paths_btn = gr.Button("🔍 Test All Paths", variant="secondary")
                        
                    gr.Markdown("### 🛠️ Database Tools")
                    upgrade_json_btn = gr.Button("🌟 Upgrade JSON Database (Add Captions)", variant="secondary")
                    upgrade_status = gr.Textbox(label="Upgrade Status", interactive=False, lines=2)
                    
                    path_status = gr.Textbox(label="Path Status", interactive=False, lines=5)
                    
                    gr.Markdown("### About")
                    gr.Markdown(f"""
                    **Current File:** `{os.path.basename(manager.current_file)}`
                    
                    **Sync Strategy:**
                    - **Primary:** A1111 (auto-loads on startup)
                    - **Secondary:** ComfyUI (synced on save)
                    - **Backup:** Local folder (always synced)
                    
                    **Quick Save ALL:** Updates all 3 locations with one click!
                    """)
        
        with gr.Tab("📥 Bulk Import"):
            gr.Markdown("### 📥 Bulk Import Characters")
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("#### JSON Data")
                    import_input = gr.Textbox(
                        label="Characters JSON Data",
                        lines=15,
                        placeholder='{\n  "character_name": {\n    "aliases": ["alias1", "alias2"],\n    "tags": "tag1, tag2",\n    "caption": "optional"\n  }\n}'
                    )
                    
                    import_category = gr.Dropdown(
                        choices=manager.get_categories(),
                        label="📁 Add to Category",
                        value="_end",
                        interactive=True
                    )
                    
                    refresh_import_categories_btn = gr.Button("🔄 Refresh Categories", variant="secondary", size="sm")
                    
                    with gr.Row():
                        import_btn = gr.Button("📥 Import Characters", variant="primary")
                        import_save_all_btn = gr.Button("📥💾 Import & Save ALL", variant="primary")
                        
                    import_status = gr.Textbox(label="Import Status", interactive=False, lines=3)
                
                with gr.Column(scale=1):
                    gr.Markdown("#### 📝 Instructions & Format")
                    gr.Markdown("""
                    Paste your characters directly in JSON format.
                    
                    **Rules:**
                    - Each character MUST have `aliases` (list) and `tags` (string).
                    - `caption` is optional but helpful for Caption Mode.
                    - Proper JSON syntax is required (use double quotes `"`).
                    
                    **Example Format:**
                    ```json
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
                    ```
                    """)
        
        # Event handlers
        def refresh_display():
            char_list = manager.get_character_list()
            char_names = manager.get_character_names()
            categories = manager.get_categories()
            delete_categories = manager.get_category_list_for_deletion()
            return char_list, gr.Dropdown(choices=char_names), gr.Dropdown(choices=categories), gr.Dropdown(choices=delete_categories)
        
        def save_all_handler():
            """🔥 Save to all 3 locations"""
            status = manager.save_to_all_locations()
            return status, manager.path_local
        
        def save_a1111_handler():
            status = manager.save_to_a1111()
            return status, manager.path_a1111
        
        def save_comfyui_handler():
            status = manager.save_to_comfyui()
            return status, manager.path_comfyui
        
        def save_local_handler():
            status = manager.save_to_local()
            return status, manager.path_local
        
        def download_json_handler():
            """Generate JSON file for download"""
            import tempfile
            # Create a temp file with the JSON content
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, "character_supplements.json")
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(manager.character_data, f, indent=2, ensure_ascii=False)
            return gr.File(value=temp_path, visible=True)
        
        def search_characters(query):
            return manager.get_character_list(query)
        
        def clear_search():
            return "", manager.get_character_list()
        
        def load_file(file_path):
            status = manager.load_json_file(file_path)
            char_names = manager.get_character_names()
            categories = manager.get_categories()
            delete_categories = manager.get_category_list_for_deletion()
            return status, manager.get_character_list(), gr.Dropdown(choices=char_names), gr.Dropdown(choices=categories), gr.Dropdown(choices=delete_categories), file_path
        
        def save_custom_file(file_path):
            status = manager.save_json_file(file_path)
            return status, file_path
        
        def create_new_file(file_path):
            manager.character_data = OrderedDict([
                ("_comment_header", "===== CHARACTER DATABASE ====="),
                ("_comment_usage", "Add your characters below")
            ])
            char_names = manager.get_character_names()
            categories = manager.get_categories()
            delete_categories = manager.get_category_list_for_deletion()
            return "✅ Created new character database", manager.get_character_list(), gr.Dropdown(choices=char_names), gr.Dropdown(choices=categories), gr.Dropdown(choices=delete_categories)
        
        def add_character_handler(name, aliases, tags, caption, category):
            status = manager.add_character(name, aliases, tags, caption, category)
            char_names = manager.get_character_names()
            categories = manager.get_categories()
            return status, manager.get_character_list(), gr.Dropdown(choices=char_names), gr.Dropdown(choices=categories), "", "", "", ""
        
        def add_and_save_all_handler(name, aliases, tags, caption, category):
            """🔥 Add character and save to all 3 locations"""
            add_status = manager.add_character(name, aliases, tags, caption, category)
            if add_status.startswith("✅"):
                save_status = manager.save_to_all_locations()
                combined_status = f"{add_status}\n\n{save_status}"
            else:
                combined_status = add_status
            
            char_names = manager.get_character_names()
            categories = manager.get_categories()
            return combined_status, manager.get_character_list(), gr.Dropdown(choices=char_names), gr.Dropdown(choices=categories), "", "", "", "", manager.path_local
        
        def load_character_handler(char_name):
            name, aliases, tags, caption = manager.get_character_details(char_name)
            return name, aliases, tags, caption
        
        def edit_character_handler(old_name, new_name, aliases, tags, caption):
            status = manager.edit_character(old_name, new_name, aliases, tags, caption)
            char_names = manager.get_character_names()
            return status, manager.get_character_list(), gr.Dropdown(choices=char_names, value=new_name if status.startswith("✅") else None)
        
        def edit_and_save_all_handler(old_name, new_name, aliases, tags, caption):
            """🔥 Edit character and save to all 3 locations"""
            edit_status = manager.edit_character(old_name, new_name, aliases, tags, caption)
            if edit_status.startswith("✅"):
                save_status = manager.save_to_all_locations()
                combined_status = f"{edit_status}\n\n{save_status}"
            else:
                combined_status = edit_status
            
            char_names = manager.get_character_names()
            return combined_status, manager.get_character_list(), gr.Dropdown(choices=char_names, value=new_name if edit_status.startswith("✅") else None), manager.path_local
        
        def delete_character_handler(name):
            status = manager.delete_character(name)
            char_names = manager.get_character_names()
            return status, manager.get_character_list(), gr.Dropdown(choices=char_names), "", "", "", ""
        
        def add_category_handler(category_name, position):
            status = manager.add_category(category_name, position)
            categories = manager.get_categories()
            delete_categories = manager.get_category_list_for_deletion()
            return status, manager.get_character_list(), "", gr.Dropdown(choices=categories), gr.Dropdown(choices=delete_categories)
        
        def delete_category_handler(category_key):
            """🔥 NEW: Delete category"""
            status = manager.delete_category(category_key)
            categories = manager.get_categories()
            delete_categories = manager.get_category_list_for_deletion()
            return status, manager.get_character_list(), gr.Dropdown(choices=categories), gr.Dropdown(choices=delete_categories)
        
        def refresh_delete_list():
            """🔥 NEW: Refresh delete category list"""
            delete_categories = manager.get_category_list_for_deletion()
            return gr.Dropdown(choices=delete_categories)
        
        def import_handler(json_text, category):
            status = manager.import_data(json_text, category)
            char_names = manager.get_character_names()
            categories = manager.get_categories()
            delete_categories = manager.get_category_list_for_deletion()
            return status, manager.get_character_list(), gr.Dropdown(choices=char_names), gr.Dropdown(choices=categories), gr.Dropdown(choices=delete_categories)
            
        def import_and_save_all_handler(json_text, category):
            import_status = manager.import_data(json_text, category)
            if import_status.startswith("✅"):
                save_status = manager.save_to_all_locations()
                combined_status = f"{import_status}\n\n{save_status}"
            else:
                combined_status = import_status
            
            char_names = manager.get_character_names()
            categories = manager.get_categories()
            delete_categories = manager.get_category_list_for_deletion()
            return combined_status, manager.get_character_list(), gr.Dropdown(choices=char_names), gr.Dropdown(choices=categories), gr.Dropdown(choices=delete_categories)
        
        def refresh_dropdown_only():
            char_names = manager.get_character_names()
            return gr.Dropdown(choices=char_names)
        
        def refresh_categories_only():
            categories = manager.get_categories()
            return gr.Dropdown(choices=categories)
        
        def update_paths(a1111, comfyui, local):
            """Update all paths"""
            manager.path_a1111 = a1111
            manager.path_comfyui = comfyui
            manager.path_local = local
            return f"✅ Paths updated!\nA1111: {a1111}\nComfyUI: {comfyui}\nLocal: {local}"
        
        def test_paths(a1111, comfyui, local):
            """Test if all paths exist or can be created"""
            results = []
            
            for name, path in [("A1111", a1111), ("ComfyUI", comfyui), ("Local", local)]:
                if os.path.exists(path):
                    results.append(f"✅ {name}: File exists at {path}")
                else:
                    dir_path = os.path.dirname(path)
                    if os.path.exists(dir_path):
                        results.append(f"⚠️ {name}: Directory exists, file will be created on save")
                    else:
                        results.append(f"❌ {name}: Directory does not exist: {dir_path}")
            
            return "\n\n".join(results)
        
        # Wire up events
        search_box.change(search_characters, inputs=search_box, outputs=character_display)
        clear_search_btn.click(clear_search, outputs=[search_box, character_display])
        refresh_btn.click(refresh_display, outputs=[character_display, edit_select, add_category, delete_category_select])
        
        # 🔥 Save buttons
        save_all_btn.click(save_all_handler, outputs=[file_status, file_path])
        save_a1111_btn.click(save_a1111_handler, outputs=[file_status, file_path])
        save_comfyui_btn.click(save_comfyui_handler, outputs=[file_status, file_path])
        save_local_btn.click(save_local_handler, outputs=[file_status, file_path])
        
        # 📥 Download button
        download_btn.click(download_json_handler, outputs=download_file)
        
        refresh_dropdown_btn.click(refresh_dropdown_only, outputs=edit_select)
        refresh_categories_btn.click(refresh_categories_only, outputs=add_category)
        
        load_btn.click(
            load_file,
            inputs=file_path,
            outputs=[file_status, character_display, edit_select, add_category, delete_category_select, file_path]
        )
        
        save_custom_btn.click(save_custom_file, inputs=file_path, outputs=[file_status, file_path])
        
        new_file_btn.click(
            create_new_file,
            inputs=file_path,
            outputs=[file_status, character_display, edit_select, add_category, delete_category_select]
        )
        
        add_btn.click(
            add_character_handler,
            inputs=[add_name, add_aliases, add_tags, add_caption, add_category],
            outputs=[add_status, character_display, edit_select, add_category, add_name, add_aliases, add_tags, add_caption]
        )
        
        add_save_all_btn.click(
            add_and_save_all_handler,
            inputs=[add_name, add_aliases, add_tags, add_caption, add_category],
            outputs=[add_status, character_display, edit_select, add_category, add_name, add_aliases, add_tags, add_caption, file_path]
        )
        
        load_char_btn.click(
            load_character_handler,
            inputs=edit_select,
            outputs=[edit_name, edit_aliases, edit_tags, edit_caption]
        )
        
        edit_btn.click(
            edit_character_handler,
            inputs=[edit_select, edit_name, edit_aliases, edit_tags, edit_caption],
            outputs=[edit_status, character_display, edit_select]
        )
        
        edit_save_all_btn.click(
            edit_and_save_all_handler,
            inputs=[edit_select, edit_name, edit_aliases, edit_tags, edit_caption],
            outputs=[edit_status, character_display, edit_select, file_path]
        )
        
        delete_btn.click(
            delete_character_handler,
            inputs=edit_select,
            outputs=[edit_status, character_display, edit_select, edit_name, edit_aliases, edit_tags, edit_caption]
        )
        
        add_category_btn.click(
            add_category_handler,
            inputs=[category_name, category_position],
            outputs=[category_status, character_display, category_name, add_category, delete_category_select]
        )
        
        # 🔥 NEW: Delete category events
        delete_category_btn.click(
            delete_category_handler,
            inputs=delete_category_select,
            outputs=[category_status, character_display, add_category, delete_category_select]
        )
        
        refresh_delete_list_btn.click(refresh_delete_list, outputs=delete_category_select)
        
        # Settings events
        update_paths_btn.click(
            update_paths,
            inputs=[a1111_path_display, comfyui_path_display, local_path_display],
            outputs=path_status
        )
        
        test_paths_btn.click(
            test_paths,
            inputs=[a1111_path_display, comfyui_path_display, local_path_display],
            outputs=path_status
        )
        
        def upgrade_database_handler():
            return manager.upgrade_database_with_captions()
            
        upgrade_json_btn.click(
            upgrade_database_handler,
            outputs=[upgrade_status]
        )
        
        # Bulk Import events
        refresh_import_categories_btn.click(refresh_categories_only, outputs=import_category)
        
        import_btn.click(
            import_handler,
            inputs=[import_input, import_category],
            outputs=[import_status, character_display, edit_select, add_category, delete_category_select]
        )
        
        import_save_all_btn.click(
            import_and_save_all_handler,
            inputs=[import_input, import_category],
            outputs=[import_status, character_display, edit_select, add_category, delete_category_select]
        )
        
        return app

if __name__ == "__main__":
    app = create_ui()
    print("🎭 Character Database Manager - Ultimate Edition")
    print("=" * 60)
    print(f"📂 A1111:   {manager.path_a1111}")
    print(f"📂 ComfyUI: {manager.path_comfyui}")
    print(f"📂 Local:   {manager.path_local}")
    print("=" * 60)
    print(f"📂 Current: {manager.current_file}")
    print("🌐 Starting web interface at http://0.0.0.0:7862 (accessible via Tailscale)")
    print("⏹️ Press Ctrl+C to stop the application")
    app.launch(
        server_name="0.0.0.0",
        server_port=7862,
        share=False,
        quiet=False
    )
