import os
import time
import sqlite3
from prettytable import PrettyTable
from colorama import Fore, Style

def read_words_from_file(file_name):
    try:
        with open(file_name, 'r') as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.RED}Error:{Style.RESET_ALL} File '{file_name}' not found.")
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
        print(f"\n{Fore.BLUE}Words File Menu:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1.{Style.RESET_ALL} Add a word")
        print(f"{Fore.CYAN}2.{Style.RESET_ALL} Remove a word")
        print(f"{Fore.CYAN}3.{Style.RESET_ALL} Show current words")
        print(f"{Fore.CYAN}4.{Style.RESET_ALL} Back to main menu")
        choice = input(f"{Fore.YELLOW}Choose an option:{Style.RESET_ALL} ")

        if choice == "1":
            new_word = input(f"{Fore.GREEN}Enter the word to add:{Style.RESET_ALL} ").strip()
            if new_word:
                with open(file_name, 'a') as file:
                    file.write(new_word + "\n")
                print(f"{Fore.GREEN}Word '{new_word}' added.{Style.RESET_ALL}")
        elif choice == "2":
            words = read_words_from_file(file_name)
            print(f"{Fore.BLUE}Current words:{Style.RESET_ALL}")
            for idx, word in enumerate(words, start=1):
                print(f"{idx}. {word}")
            try:
                to_remove = int(input(f"{Fore.YELLOW}Enter the number of the word to remove:{Style.RESET_ALL} "))
                if 1 <= to_remove <= len(words):
                    removed_word = words.pop(to_remove - 1)
                    with open(file_name, 'w') as file:
                        file.write("\n".join(words) + "\n")
                    print(f"{Fore.GREEN}Word '{removed_word}' removed.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Invalid choice.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Please enter a valid number.{Style.RESET_ALL}")
        elif choice == "3":
            words = read_words_from_file(file_name)
            print(f"{Fore.BLUE}Current words:{Style.RESET_ALL}")
            for word in words:
                print(word)
        elif choice == "4":
            break
        else:
            print(f"{Fore.RED}Invalid option. Please try again.{Style.RESET_ALL}")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    initialize_database()

    words_file = "words.txt"  # Name of the file containing the words
    repetitions_per_word = 2  # Number of times each word will be practiced

    while True:
        print(f"\n{Fore.MAGENTA}Typing Trainer Menu:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1.{Style.RESET_ALL} Practice words")
        print(f"{Fore.CYAN}2.{Style.RESET_ALL} View all records")
        print(f"{Fore.CYAN}3.{Style.RESET_ALL} Modify words file")
        print(f"{Fore.CYAN}4.{Style.RESET_ALL} Exit")
        choice = input(f"{Fore.YELLOW}Choose an option:{Style.RESET_ALL} ")

        if choice == "1":
            words = read_words_from_file(words_file)
            if not words:
                print(f"{Fore.RED}No words found for practice. Make sure the file is not empty.{Style.RESET_ALL}")
                continue

            print(f"\n{Fore.GREEN}Starting practice session!{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Press Enter when you are ready to start...{Style.RESET_ALL}")

            results = []

            for word in words:
                print(f"\n{Fore.CYAN}Practicing the word: '{word}'{Style.RESET_ALL}")
                times = []
                accuracies = []
                previous_attempt = ""
                attempts = 0

                while attempts < repetitions_per_word:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    if previous_attempt:
                        print(f"{Fore.YELLOW}Previous attempt: {previous_attempt}{Style.RESET_ALL}")
                    print(f"{Fore.MAGENTA}Repetition {attempts + 1}/{repetitions_per_word} / {word}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}Start typing now!{Style.RESET_ALL}")

                    start_time = time.time()
                    user_input = input(f"{Fore.CYAN}>>> {Style.RESET_ALL}")
                    end_time = time.time()

                    elapsed_time = end_time - start_time
                    accuracy = calculate_accuracy(word, user_input)

                    if user_input.strip() == word:
                        times.append(elapsed_time)
                        accuracies.append(accuracy)
                        attempts += 1
                    else:
                        print(f"{Fore.RED}Incorrect! The attempt does not count. Try again.{Style.RESET_ALL}")

                    previous_attempt = user_input

                    print(f"{Fore.GREEN}Results for the current attempt:{Style.RESET_ALL}")
                    print(f"{Fore.YELLOW}Time taken:{Style.RESET_ALL} {elapsed_time:.2f} seconds")
                    print(f"{Fore.YELLOW}Accuracy:{Style.RESET_ALL} {accuracy:.2f}%\n")

                average_time = sum(times) / repetitions_per_word
                average_accuracy = sum(accuracies) / repetitions_per_word
                wpm = (len(word) * repetitions_per_word / 5) / (sum(times) / 60)

                print(f"\n{Fore.GREEN}Summary for '{word}':{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Average time:{Style.RESET_ALL} {average_time:.2f} seconds")
                print(f"{Fore.YELLOW}Average accuracy:{Style.RESET_ALL} {average_accuracy:.2f}%")
                print(f"{Fore.YELLOW}Words per minute (WPM):{Style.RESET_ALL} {wpm:.2f}\n")

                update_word_record(word, wpm, average_accuracy)

                results.append((word, average_accuracy, wpm))

            table = PrettyTable()
            table.field_names = ["Word", "Average Accuracy (%)", "WPM"]
            for word, accuracy, wpm in results:
                table.add_row([word, f"{accuracy:.2f}", f"{wpm:.2f}"])

            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"\n{Fore.MAGENTA}Final Results for this session:{Style.RESET_ALL}")
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

            print(f"\n{Fore.BLUE}All Records:{Style.RESET_ALL}")
            print(record_table)

        elif choice == "3":
            modify_words_file(words_file)

        elif choice == "4":
            print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}")
            break

        else:
            print(f"{Fore.RED}Invalid option. Please try again.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()

