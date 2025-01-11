import os
import time
import sqlite3
from prettytable import PrettyTable

def read_words_from_file(file_name):
    try:
        with open(file_name, 'r') as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
        return []

def calculate_accuracy(original, user_input):
    original = original.replace(" ", "")
    user_input = user_input.replace(" ", "")
    errors = sum(1 for o, e in zip(original, user_input) if o != e)
    errors += abs(len(original) - len(user_input))
    return max(0, 100 - (errors / len(original) * 100))

def initialize_database():
    conn = sqlite3.connect("typing_records.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS records (
                        word TEXT PRIMARY KEY,
                        best_wpm REAL,
                        best_accuracy REAL
                    )''')
    conn.commit()
    conn.close()

def get_word_record(word):
    conn = sqlite3.connect("typing_records.db")
    cursor = conn.cursor()
    cursor.execute("SELECT best_wpm, best_accuracy FROM records WHERE word = ?", (word,))
    record = cursor.fetchone()
    conn.close()
    return record

def update_word_record(word, wpm, accuracy):
    conn = sqlite3.connect("typing_records.db")
    cursor = conn.cursor()
    existing_record = get_word_record(word)

    if existing_record:
        best_wpm, best_accuracy = existing_record
        if wpm > best_wpm or accuracy > best_accuracy:
            cursor.execute('''UPDATE records 
                              SET best_wpm = ?, best_accuracy = ?
                              WHERE word = ?''', 
                           (max(wpm, best_wpm), max(accuracy, best_accuracy), word))
    else:
        cursor.execute("INSERT INTO records (word, best_wpm, best_accuracy) VALUES (?, ?, ?)", (word, wpm, accuracy))

    conn.commit()
    conn.close()

def modify_words_file(file_name):
    while True:
        print("\nWords File Menu:")
        print("1. Add a word")
        print("2. Remove a word")
        print("3. Show current words")
        print("4. Back to main menu")
        choice = input("Choose an option: ")

        if choice == "1":
            new_word = input("Enter the word to add: ").strip()
            if new_word:
                with open(file_name, 'a') as file:
                    file.write(new_word + "\n")
                print(f"Word '{new_word}' added.")
        elif choice == "2":
            words = read_words_from_file(file_name)
            print("Current words:")
            for idx, word in enumerate(words, start=1):
                print(f"{idx}. {word}")
            try:
                to_remove = int(input("Enter the number of the word to remove: "))
                if 1 <= to_remove <= len(words):
                    removed_word = words.pop(to_remove - 1)
                    with open(file_name, 'w') as file:
                        file.write("\n".join(words) + "\n")
                    print(f"Word '{removed_word}' removed.")
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "3":
            words = read_words_from_file(file_name)
            print("Current words:")
            for word in words:
                print(word)
        elif choice == "4":
            break
        else:
            print("Invalid option. Please try again.")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    initialize_database()

    words_file = "words.txt"  # Name of the file containing the words
    repetitions_per_word = 2  # Number of times each word will be practiced

    while True:
        print("\nTyping Trainer Menu:")
        print("1. Practice words")
        print("2. View all records")
        print("3. Modify words file")
        print("4. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            words = read_words_from_file(words_file)
            if not words:
                print("No words found for practice. Make sure the file is not empty.")
                continue

            print("\nStarting practice session!")
            input("Press Enter when you are ready to start...")

            results = []

            for word in words:
                print(f"\nPracticing the word: '{word}'")
                times = []
                accuracies = []
                previous_attempt = ""
                attempts = 0

                while attempts < repetitions_per_word:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    if previous_attempt:
                        print(f"Previous attempt: {previous_attempt}")
                    print(f"Repetition {attempts + 1}/{repetitions_per_word} / {word}")
                    print("Start typing now!")

                    start_time = time.time()
                    user_input = input(">>> ")
                    end_time = time.time()

                    elapsed_time = end_time - start_time
                    accuracy = calculate_accuracy(word, user_input)

                    if user_input.strip() == word:
                        times.append(elapsed_time)
                        accuracies.append(accuracy)
                        attempts += 1
                    else:
                        print("Incorrect! The attempt does not count. Try again.")

                    previous_attempt = user_input

                    print(f"Results for the current attempt:")
                    print(f"Time taken: {elapsed_time:.2f} seconds")
                    print(f"Accuracy: {accuracy:.2f}%\n")

                average_time = sum(times) / repetitions_per_word
                average_accuracy = sum(accuracies) / repetitions_per_word
                wpm = (len(word) * repetitions_per_word / 5) / (sum(times) / 60)

                print(f"\nSummary for '{word}':")
                print(f"Average time: {average_time:.2f} seconds")
                print(f"Average accuracy: {average_accuracy:.2f}%")
                print(f"Words per minute (WPM): {wpm:.2f}\n")

                update_word_record(word, wpm, average_accuracy)

                results.append((word, average_accuracy, wpm))

            table = PrettyTable()
            table.field_names = ["Word", "Average Accuracy (%)", "WPM"]
            for word, accuracy, wpm in results:
                table.add_row([word, f"{accuracy:.2f}", f"{wpm:.2f}"])

            os.system('cls' if os.name == 'nt' else 'clear')
            print("\nFinal Results for this session:")
            print(table)

        elif choice == "2":
            conn = sqlite3.connect("typing_records.db")
            cursor = conn.cursor()
            cursor.execute("SELECT word, best_wpm, best_accuracy FROM records")
            records = cursor.fetchall()
            conn.close()

            record_table = PrettyTable()
            record_table.field_names = ["Word", "Best WPM", "Best Accuracy (%)"]
            for word, best_wpm, best_accuracy in records:
                record_table.add_row([word, f"{best_wpm:.2f}", f"{best_accuracy:.2f}"])

            print("\nAll Records:")
            print(record_table)

        elif choice == "3":
            modify_words_file(words_file)

        elif choice == "4":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()

