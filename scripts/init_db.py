import os
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / 'emata.db'


def main() -> None:
    if DB.exists():
        DB.unlink()
    print(f'Reset database at: {DB}')


if __name__ == '__main__':
    main()
