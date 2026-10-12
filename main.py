# =====================================================================
# SMART QUIZ PRO - Core Python Project
# Modules Used: json, random, os, time, datetime (Standard Python Libraries)
# =====================================================================

import json         # JSON files ko read aur write karne ke liye
import random       # Questions aur options ko shuffle (mix) karne ke liye
import os           # Terminal ki screen clear karne ke liye
import time         # Program ko thodi der pause (sleep) karne ke liye
import datetime     # Score save karte waqt date aur time nikalne ke liye

# ===================== CONSTANTS & CONFIG =====================
# Constants ko capital letters mein likhte hain (Good Practice)
QUESTION_FILE = "question_bank.json"
SCORE_FILE = "highscores.json"
BATCH_SIZE = 5      # Har 5 question ke baad user se continue karne ko puchega

# Professional exit messages ki list
EXIT_LINES = [
    "Thank you for using SmartQuizPro. Keep practicing!",
    "Session complete. Review your weak areas and try again.",
    "Great effort! Consistency is the key to success.",
    "Goodbye! Wishing you the best for your exams."
]

# ===================== UTILITY FUNCTIONS =====================
def clear_screen():
    # Agar Windows (nt) hai toh 'cls', Mac/Linux hai toh 'clear' command chalayega
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    # User jab tak Enter na dabaye, screen ruki rahegi
    input("\nPress Enter to continue...")


# ===================== QUESTION CLASS (UNIT 3: OOPs) =====================
# Ye class ek single question ko represent karti hai. Isme data variables aur methods hain.
class Question:
    def __init__(self, data):
        # Constructor (__init__) jo JSON dictionary data ko object properties me set karega
        self.q = data.get("q", "")
        self.type = data.get("type", "mcq")
        self.difficulty = data.get("difficulty", "Medium")
        self.options = data.get("options", [])
        self.ans = data.get("ans", "")
        self.explanation = data.get("explanation", "")

    def check_answer(self, user_input):
        # Answer check karne ka logic
        if self.type == "mcq":
            # MCQ ke liye space hata ke aur upper case karke match karenge (e.g. ' a ' == 'A')
            return user_input.strip().upper() == self.ans.strip().upper()
        else:
            # One-word ke liye space hata ke lower case karke match karenge
            return user_input.strip().lower() == self.ans.strip().lower()

    def display(self, number):
        # Question aur difficulty ko screen par print karega
        print(f"\nQ{number}  [{self.difficulty}]  [{self.type.upper()}]")
        print(f"   {self.q}")
        if self.type == "mcq":
            for opt in self.options:
                print(f"   {opt}")


# ===================== QUESTION BANK CLASS (UNIT 4: File Handling) =====================
# Ye class JSON file se saare questions utha kar memory mein load karti hai.
class QuestionBank:
    def __init__(self, filename):
        self.filename = filename
        self.data = {}
        self.load()

    def load(self):
        # Exception Handling (Unit 4): Agar file na mile toh program crash nahi hoga
        try:
            # "r" matlab read mode. File open karke json.load se dictionary me daalenge
            with open(self.filename, "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            print(f"\nCritical Error: File '{self.filename}' is missing!")
            exit()  # Program band kar dega
        except json.JSONDecodeError:
            print(f"\nCritical Error: '{self.filename}' contains invalid JSON format.")
            exit()

    def get_units(self):
        # Dictionary ki keys return karega (Unit names)
        return list(self.data.keys())

    def get_topics(self, unit):
        # Specific unit ke andar ki keys return karega (Topic names)
        return list(self.data[unit].keys())

    def get_questions(self, unit, topic):
        # Json ke list item ko Question Object me convert karke list banayega (List Comprehension)
        return [Question(q) for q in self.data[unit][topic]]


# ===================== SCORE MANAGER CLASS (UNIT 4: File Write) =====================
# Ye class highscores ko calculate karti hai aur doosri JSON file mein save karti hai.
class ScoreManager:
    def __init__(self, filename):
        self.filename = filename
        self.scores = {}
        self.load()

    def load(self):
        # Agar score file pehle se hai, toh usko read karo, warna khali dictionary bana lo
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    self.scores = json.load(f)
            except json.JSONDecodeError:
                self.scores = {}
        else:
            self.scores = {}

    def save(self):
        # File Handling: "w" mode me open karke data write karenge (indent=4 se format clean dikhega)
        with open(self.filename, "w") as f:
            json.dump(self.scores, f, indent=4)

    def add_score(self, unit, name, score, total):
        # Naye unit ke liye pehle khali list banayenge
        if unit not in self.scores:
            self.scores[unit] = []
            
        percentage = round((score / total) * 100, 2) if total > 0 else 0
        
        # Naya record dictionary format me append karenge
        self.scores[unit].append({
            "name": name,
            "score": score,
            "total": total,
            "percentage": percentage,
            "date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
        })
        
        # Sort function se percentage ke hisaab se descending order (high to low) me sort karenge
        # [:5] ka matlab sirf Top 5 scores hi file me rahenge
        self.scores[unit] = sorted(
            self.scores[unit],
            key=lambda x: x["percentage"],
            reverse=True
        )[:5]
        self.save()

    def display_leaderboard(self):
        # Leaderboard UI print karne ka function
        clear_screen()
        print("=" * 70)
        print("                    UNIT-WISE LEADERBOARD")
        print("=" * 70)
        if not self.scores:
            print("\nNo highscores recorded yet. Play a quiz to set a record!")
            return
            
        for unit, entries in self.scores.items():
            print(f"\n{unit}")
            print("-" * 70)
            # Formatting strings: <6 ka matlab left-align with 6 spaces
            print(f"{'Rank':<6}{'Name':<18}{'Score':<10}{'%':<10}{'Date':<20}")
            print("-" * 70)
            for i, e in enumerate(entries, 1):
                score_str = f"{e['score']}/{e['total']}"
                pct_str = f"{e['percentage']}%"
                print(f"{i:<6}{e['name']:<18}{score_str:<10}{pct_str:<10}{e['date']:<20}")


# ===================== QUIZ ENGINE CLASS =====================
# Ye class actual game loop chalati hai (Questions dikhana, check karna, score update karna)
class QuizEngine:
    def __init__(self, player_name, questions, unit, topic):
        self.player = player_name
        self.questions = questions
        self.unit = unit
        self.topic = topic
        self.score = 0
        self.attempted = 0

    def ask_question(self, question, number):
        question.display(number)
        
        # User se input lena
        try:
            user_input = input("\nYour Answer: ").strip()
        except KeyboardInterrupt:
            # Agar user ne Ctrl+C daba diya to crash nahi hoga
            print("\n\nQuiz interrupted by user.")
            return True

        if not user_input:
            print("Empty answer detected! Marked as incorrect.")
            is_correct = False
        else:
            is_correct = question.check_answer(user_input)

        if is_correct:
            print(f"Status: Correct! ✅")
            self.score += 1
        else:
            print(f"Status: Incorrect ❌ | Right Answer: {question.ans}")

        print(f"Explanation: {question.explanation}")
        print("-" * 70)
        return False

    def run(self):
        # random module se questions ki list ko shuffle kar diya
        random.shuffle(self.questions)
        total = len(self.questions)
        
        if total == 0:
            print("Notice: No questions available in this topic.")
            return

        clear_screen()
        print("=" * 70)
        print(f"  Quiz Started: {self.unit} -> {self.topic}")
        print(f"  Player: {self.player}  |  Total Questions: {total}")
        print("=" * 70)
        time.sleep(1.5)

        batch_count = 0
        # for loop (Unit 2): har question pe iterate karega
        for i, question in enumerate(self.questions, 1):
            self.attempted += 1
            interrupted = self.ask_question(question, i)
            if interrupted:
                break
            batch_count += 1

            # Har 5 questions (BATCH_SIZE) ke baad user choice (continue/quit)
            if batch_count == BATCH_SIZE and i < total:
                print(f"\nCurrent Progress: {self.score}/{self.attempted} correct")
                choice = input("Do you want to continue to the next batch? (Y/N): ").strip().lower()
                if choice != 'y':
                    break
                batch_count = 0
                clear_screen()

        self.show_result()

    def show_result(self):
        # Quiz khatam hone ke baad final scorecard
        print("\n" + "=" * 70)
        print("                         QUIZ COMPLETED")
        print("=" * 70)
        print(f"Player Name : {self.player}")
        print(f"Unit Name   : {self.unit}")
        print(f"Topic Name  : {self.topic}")
        print(f"Final Score : {self.score}/{self.attempted}")
        
        if self.attempted > 0:
            pct = round((self.score / self.attempted) * 100, 2)
            print(f"Accuracy    : {pct}%")
            if pct >= 80:
                print("Performance : Outstanding!")
            elif pct >= 60:
                print("Performance : Good Job. Keep revising.")
            else:
                print("Performance : Needs more practice.")
        print("=" * 70)


# ===================== MAIN APP / SYSTEM CONTROLLER =====================
# Ye class main menu handle karti hai aur poore project ko jode (integrate) rakhti hai
class SmartQuizApp:
    def __init__(self):
        self.bank = QuestionBank(QUESTION_FILE)
        self.scores = ScoreManager(SCORE_FILE)

    def show_header(self):
        clear_screen()
        print("=" * 70)
        print("                SMART QUIZ PRO - Interactive Learning")
        print("=" * 70)

    def main_menu(self):
        # Infinite loop (while True): jab tak user 3 (Exit) na dabaye, menu chalta rahega
        while True:
            self.show_header()
            print("[1] Play Quiz")
            print("[2] View Unit-wise Leaderboard")
            print("[3] Exit Application")
            print("=" * 70)
            
            try:
                choice = input("Enter your choice (1-3): ").strip()
                if choice == '1':
                    self.start_quiz()
                elif choice == '2':
                    self.scores.display_leaderboard()
                    pause()
                elif choice == '3':
                    # Random module se exit message select karega
                    print("\n" + random.choice(EXIT_LINES) + "\n")
                    break
                else:
                    print("Invalid choice! Please enter 1, 2, or 3.")
                    time.sleep(1)
            except KeyboardInterrupt:
                # Ctrl+C dabane pe gracefully close hoga
                print("\n\n" + random.choice(EXIT_LINES) + "\n")
                break

    def start_quiz(self):
        # Quiz setup flow: Name -> Unit -> Topic
        try:
            self.show_header()
            name = input("Enter Player Name: ").strip()
            if not name:
                name = "Guest"

            units = self.bank.get_units()
            print("\nSelect an Academic Unit:")
            for i, u in enumerate(units, 1):
                print(f"  [{i}] {u}")
                
            unit_choice = int(input("\nEnter Unit Number: "))
            if unit_choice < 1 or unit_choice > len(units):
                print("Invalid unit selection.")
                time.sleep(1)
                return
            selected_unit = units[unit_choice - 1]

            topics = self.bank.get_topics(selected_unit)
            print(f"\nSelect a Topic from {selected_unit}:")
            for i, t in enumerate(topics, 1):
                print(f"  [{i}] {t}")
                
            topic_choice = int(input("\nEnter Topic Number: "))
            if topic_choice < 1 or topic_choice > len(topics):
                print("Invalid topic selection.")
                time.sleep(1)
                return
            selected_topic = topics[topic_choice - 1]

            questions = self.bank.get_questions(selected_unit, selected_topic)
            if not questions:
                print("Notice: No questions available for this specific topic.")
                time.sleep(1.5)
                return

            # Engine initialize karke run kiya
            quiz = QuizEngine(name, questions, selected_unit, selected_topic)
            quiz.run()

            # Result save kiya leaderboard me
            if quiz.attempted > 0:
                self.scores.add_score(selected_unit, name, quiz.score, quiz.attempted)
                print("\nRecord successfully saved to Leaderboard.")
            pause()
            
        except ValueError:
            print("Error: Please enter a valid numerical digit.")
            time.sleep(1)
        except Exception as e:
            print(f"Unexpected Error: {e}")
            time.sleep(1.5)

# ===================== SCRIPT ENTRY POINT =====================
# Program yahan se start hota hai
if __name__ == "__main__":
    try:
        app = SmartQuizApp()
        app.main_menu()
    except Exception as e:
        print(f"Fatal System Error: {e}")