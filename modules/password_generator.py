# modules/password_generator.py
# v1.1: Foundations & Efficiency (Generator Optimization)

import os
import itertools
from tqdm import tqdm
try:
    from modules.utils import RichConsole, ResultSaver
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from modules.utils import RichConsole, ResultSaver

console = RichConsole.get_console()
saver = ResultSaver("wordlist")

def generate_base_variations(word):
    """Yields basic casing variations."""
    yield word.lower()
    yield word.upper()
    yield word.capitalize()

def generate_special_variations(base_iter):
    """Yields variations with special chars."""
    special_chars = ['!', '@', '#', '$', '123', '2024', '2025']
    for word in base_iter:
        yield word
        for char in special_chars:
            yield f"{word}{char}"
            yield f"{char}{word}"

def generate_combinations(words):
    """Yields combinations of two words."""
    if len(words) < 2: return
    for p in itertools.permutations(words, 2):
        yield f"{p[0]}{p[1]}"
        yield f"{p[0]}_{p[1]}"
        yield f"{p[0]}.{p[1]}"

def main():
    RichConsole.print_banner("Smart Wordlist Generator v1.1")
    
    input_str = console.input("[info]Enter keywords (comma separated): [/info]")
    keywords = [k.strip() for k in input_str.split(',') if k.strip()]
    
    if not keywords:
        console.print("[error][!] No keywords provided.[/error]")
        return
        
    savename = saver.save_text("custom", []) # Just to get a path, we will stream write
    if not savename:
        savename = os.path.join(saver.results_dir, "custom_wordlist.txt")
        
    console.print(f"\n[info][*] Generating and streaming to: {savename}[/info]")
    
    count = 0
    seen = set()
    
    try:
        with open(savename, 'w', encoding='utf-8') as f:
            # 1. Base variations
            for k in keywords:
                for var in generate_special_variations(generate_base_variations(k)):
                    if var not in seen:
                        f.write(var + '\n')
                        seen.add(var)
                        count += 1
            
            # 2. Combinations
            for combo in generate_combinations(keywords):
                 for var in generate_special_variations(generate_base_variations(combo)):
                    if var not in seen:
                        f.write(var + '\n')
                        seen.add(var)
                        count += 1
                        
            # 3. Leet speak (Simple example)
            leet_map = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5'}
            # Convert existing seen items to leet
            # Note: We iterate over a copy of 'seen' to avoid modifying while iterating, 
            # but for memory safety with massive lists, we might want to skip this or handle differently.
            # For v1.1 we will just do a pass on keywords.
            for k in keywords:
                leet_word = k.lower()
                for char, sub in leet_map.items():
                    leet_word = leet_word.replace(char, sub)
                if leet_word not in seen:
                    f.write(leet_word + '\n')
                    seen.add(leet_word)
                    count += 1

    except Exception as e:
        console.print(f"[error][!] Error during generation: {e}[/error]")
        
    console.print(f"\n[success]✅ Generation Complete! {count} words written.[/success]")

if __name__ == "__main__":
    main()