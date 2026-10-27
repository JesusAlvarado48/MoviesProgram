from repository import MovieRepository
from service import MovieApplication

def main():
    repo = MovieRepository()
    try:
        app = MovieApplication(repo)
        app.run()
    finally:
        repo.close()

if __name__ == "__main__":
    main()