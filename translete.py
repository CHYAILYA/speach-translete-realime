import speech_recognition as sr
from googletrans import Translator
import tkinter as tk
from tkinter import ttk
import time
import threading
from langdetect import detect, LangDetectException
from tkinter import PhotoImage

popup_file_path = "popup_text.txt"

recognizer = sr.Recognizer()
translator = Translator()

source_language = 'auto'  # Default source language set to auto-detect
selected_language = "id"  # Default translation language is Indonesian

SUPPORTED_LANGUAGES = [
    'en', 'id', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh-cn', 'ar', 'tr', 'pl', 'nl', 'sv', 'da', 'fi', 'no', 'cs', 'sk', 'ro', 'hu', 'el', 'th', 'ms'
]

def detect_and_force_language(text):
    """
    Detects the language using langdetect and forces language based on known keywords.
    If the detection is inaccurate, it can be forced to a more appropriate language.
    """
    global source_language
    try:
        detected_lang = detect(text)  # Using langdetect for better detection
        print(f"Detected Source Language: {detected_lang}")

        if detected_lang not in SUPPORTED_LANGUAGES:
            print(f"Detected unsupported language: {detected_lang}. Defaulting to 'en'.")
            detected_lang = 'en'

        # If detected language is not accurate, set it to the default language
        if detected_lang == 'sw':  # Swahili detection error case
            detected_lang = 'id'  # Defaulting to Indonesian if Swahili is detected by mistake

        return detected_lang
    except LangDetectException as e:
        print(f"Error detecting language: {e}. Defaulting to 'en'.")
        return 'en'


def translate_speech(root, label_translation, label_listening, label_error):
    global selected_language, source_language
    while True:
        try:
            with sr.Microphone() as source:
                # Indicate that the system is listening
                label_listening.config(text="Listening... Please speak now.", fg="blue")
                root.update_idletasks()

                # Adjust the recognizer sensitivity to ambient noise more effectively
                recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for ambient noise, with a 1-second duration
                audio = recognizer.listen(source, phrase_time_limit=None)  # Remove timeout for indefinite listening

                # Recognize speech
                try:
                    # Dynamically set language for better accuracy
                    language_code = selected_language if source_language == 'auto' else source_language
                    text = recognizer.recognize_google(audio, language=language_code)  # Dynamically set language

                    print(f"Teks asli: {text}")

                    if len(text.strip()) == 0:
                        label_error.config(text="Error: No speech detected.", fg="red")
                        label_translation.config(text="")  # Reset translation text
                        continue

                    # Detect language if needed
                    if source_language == 'auto':  # Detect language if needed
                        source_language = detect_and_force_language(text)

                    # Translate to the selected language
                    if source_language in SUPPORTED_LANGUAGES:
                        label_listening.config(text="Processing... Translating...", fg="green")
                        root.update_idletasks()

                        translated = translator.translate(text, src=source_language, dest=selected_language)
                        print(f"Terjemahan: {translated.text}")

                        # Save to file
                        with open(popup_file_path, "w", encoding="utf-8") as f:
                            f.write(f"Teks Asli: {text}\nTerjemahan: {translated.text}")

                        # Update translation label with text wrapping
                        label_translation.config(state="normal")  # Enable editing to insert text
                        label_translation.delete(1.0, tk.END)  # Clear existing text
                        label_translation.insert(tk.END, f"Teks Asli: {text}\nTerjemahan: {translated.text}")
                        label_translation.config(state="disabled")  # Disable editing mode to prevent modification

                        label_listening.config(text="Listening... Please speak now.", fg="blue")  # Reset Listening label after processing
                    else:
                        print(f"Unsupported source language: {source_language}. Defaulting to 'en'.")
                        source_language = 'en'

                except sr.UnknownValueError:
                    label_error.config(text="Error: Could not understand speech.", fg="red")
                    label_translation.config(text="")  # Reset translation text
                except sr.RequestError as e:
                    label_error.config(text=f"Error: {e}", fg="red")
                    label_translation.config(text="")  # Reset translation text
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    label_error.config(text=f"Unexpected error: {e}", fg="red")
                    label_translation.config(text="")  # Reset translation text

        except Exception as e:
            label_error.config(text=f"Error: {e}", fg="red")
            label_translation.config(text="")  # Reset translation text


def create_popup():
    def update_language(event):
        global selected_language
        selected_language = language_combobox.get()
        print(f"Bahasa terpilih: {selected_language}")

    def update_source_language(event):
        global source_language
        source_language_input = source_language_combobox.get()
        if source_language_input == "auto":
            source_language = 'auto'
        else:
            # Convert language to supported code format
            language_map = {
                "Indonesia": "id", "English": "en", "Spanish": "es", "French": "fr", "German": "de",
                "Italian": "it", "Portuguese": "pt", "Russian": "ru", "Japanese": "ja", "Korean": "ko",
                "Chinese (Simplified)": "zh-cn", "Arabic": "ar", "Turkish": "tr", "Polish": "pl", "Dutch": "nl",
                "Swedish": "sv", "Danish": "da", "Finnish": "fi", "Norwegian": "no", "Czech": "cs", "Slovak": "sk",
                "Romanian": "ro", "Hungarian": "hu", "Greek": "el", "Thai": "th", "Malay": "ms"
            }
            source_language = language_map.get(source_language_input, 'en')  # Default to 'en' if not found
        print(f"Bahasa sumber: {source_language}")

    root = tk.Tk()
    root.title("Translation Results")

    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack()

    tk.Label(frame, text="Pilih Bahasa Sumber:", font=("Helvetica", 12)).grid(row=0, column=0, padx=5, pady=5)

    # Dropdown untuk memilih bahasa sumber
    source_language_combobox = ttk.Combobox(frame, values=[ 
        "auto", "Indonesia", "English", "Spanish", "French", "German", "Italian", "Portuguese", "Russian", "Japanese", "Korean", "Chinese (Simplified)", "Arabic", "Turkish", "Polish", "Dutch", "Swedish", "Danish", "Finnish", "Norwegian", "Czech", "Slovak", "Romanian", "Hungarian", "Greek", "Thai", "Malay"
    ], font=("Helvetica", 12))
    source_language_combobox.set("auto")  # Bahasa sumber default
    source_language_combobox.grid(row=0, column=1, padx=5, pady=5)
    source_language_combobox.bind("<<ComboboxSelected>>", update_source_language)

    tk.Label(frame, text="Pilih Bahasa Tujuan:", font=("Helvetica", 12)).grid(row=1, column=0, padx=5, pady=5)

    # Dropdown untuk memilih bahasa tujuan
    language_combobox = ttk.Combobox(frame, values=[ 
        "Indonesia", "English", "Spanish", "French", "German", "Italian", "Portuguese", "Russian", "Japanese", "Korean", "Chinese (Simplified)", "Arabic", "Turkish", "Polish", "Dutch", "Swedish", "Danish", "Finnish", "Norwegian", "Czech", "Slovak", "Romanian", "Hungarian", "Greek", "Thai", "Malay"
    ], font=("Helvetica", 12))
    language_combobox.set("Indonesia")  # Bahasa default
    language_combobox.grid(row=1, column=1, padx=5, pady=5)
    language_combobox.bind("<<ComboboxSelected>>", update_language)

    # Use a Text widget with vertical scroll for displaying long translations
    label_translation = tk.Text(frame, height=10, width=50, font=("Helvetica", 12), wrap="word", state="disabled")
    label_translation.grid(row=2, column=0, columnspan=2)

    label_listening = tk.Label(frame, text="Listening...", font=("Helvetica", 12), padx=20, pady=10)
    label_listening.grid(row=3, column=0, columnspan=2)

    label_error = tk.Label(frame, text="", font=("Helvetica", 12), fg="red", padx=20, pady=10)
    label_error.grid(row=4, column=0, columnspan=2)

    # Periksa file secara berkala untuk pembaruan
    def update_popup():
        while True:
            try:
                with open(popup_file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                label_translation.config(state="normal")  # Enable editing to insert text
                label_translation.delete(1.0, tk.END)  # Clear existing text
                label_translation.insert(tk.END, content)
                label_translation.config(state="disabled")  # Disable editing mode to prevent modification
                root.update_idletasks()
                root.update()
            except Exception as e:
                print(f"Error reading popup text file: {e}")
            time.sleep(1)

    popup_thread = threading.Thread(target=update_popup, daemon=True)
    popup_thread.start()

    # Start speech recognition thread
    speech_thread = threading.Thread(target=translate_speech, args=(root, label_translation, label_listening, label_error), daemon=True)
    speech_thread.start()

    root.mainloop()

if __name__ == "__main__":
    create_popup()
