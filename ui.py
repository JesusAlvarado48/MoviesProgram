from typing import List, Optional
from models import Movie, Category

class UI:
    NAME_WIDTH = 50

    @staticmethod
    def show_introduction() -> None:
        print("==================================================")
        print("          Welcome to the Movie List Program        ")
        print("==================================================")
        print("Manage your movie database with ease. You can view,")
        print("search, add, and delete movies.")
        print("\nNavigation:")
        print("- Select a numbered option from the command menu.")
        print("- Type 'exit' or '^' at any prompt to cancel an operation.")
        print("==================================================\n")

    @staticmethod
    def show_menu() -> None:
        print("\n--- Command Menu ---")
        print("1. View all movies")
        print("2. View movies by category")
        print("3. View movies by year")
        print("4. Add a movie")
        print("5. Delete a movie (Movie ID required)")
        print("6. Search movie by title")
        print("7. Exit program")

    @staticmethod
    def get_menu_choice() -> str:
        return input("Please select an option: ").strip()

    @staticmethod
    def format_title(title: str) -> str:
        if len(title) > UI.NAME_WIDTH:
            return title[:UI.NAME_WIDTH - 3] + "..."
        return title.ljust(UI.NAME_WIDTH)

    @staticmethod
    def print_movie_header() -> None:
        header = f"{'ID':<6} {'Name':<{UI.NAME_WIDTH}} {'Year':<6} {'Mins':<6} {'Category':<15}"
        print("-" * len(header))
        print(header)
        print("-" * len(header))

    @staticmethod
    def print_movie_row(movie: Movie) -> None:
        formatted_name = UI.format_title(movie.title)
        category_str = movie.category_name if movie.category_name else ""
        print(f"{str(movie.id):<6} {formatted_name} {str(movie.year):<6} {str(movie.duration):<6} {category_str:<15}")

    @staticmethod
    def display_movies_paginated(movies: List[Movie]) -> None:
        if not movies:
            print("\nNo movies found.")
            return

        chunk_size = 10
        total_movies = len(movies)
        for i in range(0, total_movies, chunk_size):
            chunk = movies[i:i + chunk_size]
            UI.print_movie_header()
            for movie in chunk:
                UI.print_movie_row(movie)
            print("-" * (6 + UI.NAME_WIDTH + 6 + 6 + 15 + 4))

            if i + chunk_size < total_movies:
                while True:
                    choice = input("Press [Enter] for next 10 movies or '^' to return to menu: ").strip()
                    if choice == "":
                        break
                    elif choice == "^" or choice.lower() == "exit":
                        return
                    else:
                        print("Invalid input. Press Enter to continue or '^' to stop.")

    @staticmethod
    def display_categories(categories: List[Category]) -> None:
        print("\n--- Available Categories ---")
        for cat in categories:
            print(f"[{cat.id}] {cat.name}")
        print("----------------------------")

    @staticmethod
    def get_integer_input(prompt: str) -> Optional[int]:
        while True:
            val = input(prompt).strip()
            if val.lower() == "exit" or val == "^":
                return None
            try:
                return int(val)
            except ValueError:
                print("Error: Please enter a valid whole number (or 'exit' / '^' to cancel).")

    @staticmethod
    def get_string_input(prompt: str) -> Optional[str]:
        val = input(prompt).strip()
        if val.lower() == "exit" or val == "^":
            return None
        return val