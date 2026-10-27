from repository import MovieRepository
from ui import UI

class MovieApplication:
    def __init__(self, repository: MovieRepository):
        self.repo = repository

    def run(self) -> None:
        UI.show_introduction()
        while True:
            UI.show_menu()
            choice = UI.get_menu_choice()

            if choice == "1":
                self.view_all_movies()
            elif choice == "2":
                self.view_movies_by_category()
            elif choice == "3":
                self.view_movies_by_year()
            elif choice == "4":
                self.add_movie()
            elif choice == "5":
                self.delete_movie()
            elif choice == "6":
                self.search_movie()
            elif choice == "7":
                print("\nThank you for using the Movie List Program. Goodbye!")
                break
            else:
                print("\nError: Invalid option. Please select a number between 1 and 7.")

    def view_all_movies(self) -> None:
        movies = self.repo.get_all_movies()
        UI.display_movies_paginated(movies)

    def view_movies_by_category(self) -> None:
        categories = self.repo.get_categories()
        UI.display_categories(categories)
        cat_id = UI.get_integer_input("Enter Category ID: ")
        if cat_id is None:
            return
        
        if not self.repo.category_exists(cat_id):
            print("\nError: Invalid Category ID.")
            return

        movies = self.repo.get_movies_by_category(cat_id)
        UI.display_movies_paginated(movies)

    def view_movies_by_year(self) -> None:
        year = UI.get_integer_input("Enter release year: ")
        if year is None:
            return
        movies = self.repo.get_movies_by_year(year)
        UI.display_movies_paginated(movies)

    def add_movie(self) -> None:
        title = UI.get_string_input("Enter movie name/title: ")
        if not title or title == "^" or title.lower() == "exit":
            return

        year = UI.get_integer_input("Enter release year: ")
        if year is None:
            return

        duration = UI.get_integer_input("Enter duration in minutes: ")
        if duration is None:
            return

        categories = self.repo.get_categories()
        UI.display_categories(categories)
        cat_id = UI.get_integer_input("Enter Category ID: ")
        if cat_id is None:
            return

        if not self.repo.category_exists(cat_id):
            print("\nError: Invalid Category ID. Database remains unchanged.")
            return

        self.repo.add_movie(title, year, duration, cat_id)
        print(f"\nSuccess: Movie '{title}' added successfully!")

    def delete_movie(self) -> None:
        movie_id = UI.get_integer_input("Enter Movie ID to delete: ")
        if movie_id is None:
            return

        movie = self.repo.get_movie_by_id(movie_id)
        if not movie:
            print("\nError: Movie ID does not exist. Database remains unchanged.")
            return

        success = self.repo.delete_movie(movie_id)
        if success:
            print("\nSuccess: Deleted the following movie:")
            UI.print_movie_header()
            UI.print_movie_row(movie)
        else:
            print("\nError: Could not delete movie.")

    def search_movie(self) -> None:
        query = UI.get_string_input("Enter title to search (full or partial): ")
        if not query or query == "^" or query.lower() == "exit":
            return

        movies = self.repo.search_movies_by_title(query)
        if not movies:
            print(f"\nNo movies found matching '{query}'.")
        else:
            UI.display_movies_paginated(movies)