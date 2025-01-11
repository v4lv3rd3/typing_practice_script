import os
import time
from prettytable import PrettyTable
from colorama import Fore, Back, Style


# Function to read words from a file
def read_words_from_file(file_name):
    try:
        with open(file_name, 'r') as file:
            return [line.strip() for line in file.readlines() if line.strip()]
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
        return []

def calculate_accuracy(original, user_input):
    # Ignore extra spaces when calculating accuracy
    original = original.replace(" ", "")
    user_input = user_input.replace(" ", "")
    errors = sum(1 for o, e in zip(original, user_input) if o != e)
    errors += abs(len(original) - len(user_input))
    return max(0, 100 - (errors / len(original) * 100))

def main():
    # Clear the screen before starting
    os.system('cls' if os.name == 'nt' else 'clear')

    words_file = "words.txt"  # Name of the file containing the words
    repetitions_per_word = 2  # Number of times each word will be practiced

    words = read_words_from_file(words_file)
    if not words:
        print("No words found for practice. Make sure the file is not empty.")
        return

    print("Welcome to the Typing Trainer!")
    print("Type the words you struggle with correctly as many times as indicated.\n")

    input("Press Enter when you are ready to start...")

    results = []

    for word in words:
        print(f"\nPracticing the word: '{word}'")
        times = []
        accuracies = []
        previous_attempt = ""
        attempts = 0

        while attempts < repetitions_per_word:
            # Clear the screen before each attempt
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
                print(Fore.RED + "INCORRECT! The attempt does not count. Try again.")

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

        results.append((word, average_accuracy, wpm))

    # Display results table
    table = PrettyTable()
    table.field_names = ["Word", "Average Accuracy (%)", "WPM"]
    for word, accuracy, wpm in results:
        table.add_row([word, f"{accuracy:.2f}", f"{wpm:.2f}"])

    os.system('cls' if os.name == 'nt' else 'clear')
    print("\nFinal Results:")
    print(table)

if __name__ == "__main__":
    main()

