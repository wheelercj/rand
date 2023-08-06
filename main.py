import argparse
import enum
import os
import secrets
import sys
import textwrap

folder_path: str = os.path.dirname(__file__.replace("\\", "/"))

alphabet: set[str] = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
lower: set[str] = set("abcdefghijklmnopqrstuvwxyz")
upper: set[str] = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
number: set[str] = set("0123456789")
special: set[str] = set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")

all_chars: set[str] = alphabet | number | special


class CharCategories(enum.Enum):
    ALPHABET = "alphabet"
    LOWER = "lower"
    UPPER = "upper"
    NUMBER = "number"
    SPECIAL = "special"


def main():
    args: argparse.Namespace = parse_args()
    type_: str = args.type

    if type_ == "num":
        generate_number(args)
    elif type_ == "name":
        generate_names(args)
    elif type_ == "pass":
        generate_password(args)
    elif type_ == "choice":
        choose(args)
    elif type_ == "choices":
        choose_multiple(args)
    elif type_ == "shuffle":
        shuffle(args)
    else:
        raise ValueError("Invalid type")


def generate_number(args: argparse.Namespace) -> None:
    min_: int = args.min
    max_: int = args.max
    print(secrets.randbelow(max_ - min_ + 1) + min_)


def generate_names(args: argparse.Namespace) -> None:
    count: int = args.count
    with open(os.path.join(folder_path, "nouns.txt")) as nouns_file:
        nouns: list[str] = nouns_file.read().splitlines()
    with open(os.path.join(folder_path, "adjectives.txt")) as adjectives_file:
        adjectives: list[str] = adjectives_file.read().splitlines()
    for _ in range(count):
        print(secrets.choice(adjectives) + secrets.choice(nouns))


def generate_password(args: argparse.Namespace) -> None:
    length: int = args.length
    exclude: set[str] = set(args.exclude) if args.exclude else set()
    exclude_categories: list[str] = args.exclude_category or []
    include: set[str] = set(args.include) if args.include else set()
    include_categories: list[str] = args.include_category or []

    remaining_chars: set[str] = get_chosen_chars(
        exclude, exclude_categories, include, include_categories
    )
    if not remaining_chars:
        print("No characters were included or all were excluded")
        sys.exit(1)
    remaining_chars_list: list[str] = list(remaining_chars)

    password: list[str] = []
    for _ in range(length):
        password.append(secrets.choice(remaining_chars_list))
    print("".join(password))


def get_chosen_chars(
    exclude: set[str],
    exclude_categories: list[str],
    include: set[str],
    include_categories: list[str],
) -> set[str]:
    if (include or include_categories) and (exclude or exclude_categories):
        print("You cannot both include and exclude characters")
        sys.exit(1)

    remaining_chars: set[str] = set()
    if exclude or exclude_categories:
        remaining_chars = all_chars - exclude
        if CharCategories.ALPHABET.value in exclude_categories:
            remaining_chars -= alphabet
        if CharCategories.LOWER.value in exclude_categories:
            remaining_chars -= lower
        if CharCategories.UPPER.value in exclude_categories:
            remaining_chars -= upper
        if CharCategories.NUMBER.value in exclude_categories:
            remaining_chars -= number
        if CharCategories.SPECIAL.value in exclude_categories:
            remaining_chars -= special
        return remaining_chars
    elif include or include_categories:
        remaining_chars = include
        if CharCategories.ALPHABET.value in include_categories:
            remaining_chars |= alphabet
        if CharCategories.LOWER.value in include_categories:
            remaining_chars |= lower
        if CharCategories.UPPER.value in include_categories:
            remaining_chars |= upper
        if CharCategories.NUMBER.value in include_categories:
            remaining_chars |= number
        if CharCategories.SPECIAL.value in include_categories:
            remaining_chars |= special
        return remaining_chars
    else:
        return all_chars


def choose(args: argparse.Namespace) -> None:
    items: list[str] = args.items
    print(secrets.choice(items))


def choose_multiple(args: argparse.Namespace) -> None:
    items: list[str] = args.items
    count: int = args.count
    if count > len(items):
        print("Error: cannot choose more items than are available")
        sys.exit(1)

    chosen: list[str] = []
    while len(chosen) < count:
        choice: str = secrets.choice(items)
        if choice not in chosen:
            chosen.append(choice)
    print(" ".join(chosen))


def shuffle(args: argparse.Namespace) -> None:
    items: list[str] = args.items
    secrets.SystemRandom().shuffle(items)
    print(" ".join(items))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="rand",
        description=textwrap.dedent(
            """\
            Generate random text.
            """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="type", required=True)

    number_parser = subparsers.add_parser("num", help="Generate a random number")
    number_parser.add_argument(
        "min",
        type=int,
        help="Minimum possible number",
    )
    number_parser.add_argument(
        "max",
        type=int,
        help="Maximum possible number",
    )

    name_parser = subparsers.add_parser("name", help="Generate random names")
    name_parser.add_argument(
        "count",
        type=int,
        help="Number of names to generate",
    )

    pass_parser = subparsers.add_parser(
        "pass",
        help="Generate a random password",
        description=textwrap.dedent(
            """\
            You cannot both include and exclude characters or character categories.
            """
        ),
    )
    pass_parser.add_argument(
        "length",
        type=int,
        help="Length of password to generate",
    )
    pass_parser.add_argument(
        "-x",
        "--exclude",
        type=str,
        help="Characters to exclude from random password generation",
    )
    pass_parser.add_argument(
        "-xc",
        "--exclude-category",
        type=str,
        choices=[
            CharCategories.ALPHABET.value,
            CharCategories.LOWER.value,
            CharCategories.UPPER.value,
            CharCategories.NUMBER.value,
            CharCategories.SPECIAL.value,
        ],
        help="Character categories to exclude from random password generation",
        nargs="*",
    )
    pass_parser.add_argument(
        "-i",
        "--include",
        type=str,
        help="Characters to include in random password generation",
    )
    pass_parser.add_argument(
        "-ic",
        "--include-category",
        type=str,
        choices=[
            CharCategories.ALPHABET.value,
            CharCategories.LOWER.value,
            CharCategories.UPPER.value,
            CharCategories.NUMBER.value,
            CharCategories.SPECIAL.value,
        ],
        help="Character categories to include in random password generation",
        nargs="*",
    )

    choice_parser = subparsers.add_parser(
        "choice",
        help="Choose a random item from a list",
    )
    choice_parser.add_argument(
        "items",
        type=str,
        help="Items to choose from",
        nargs="+",
    )

    choices_parser = subparsers.add_parser(
        "choices",
        help="Choose multiple random items from a list without replacement",
    )
    choices_parser.add_argument(
        "count",
        type=int,
        help="Number of items to choose",
    )
    choices_parser.add_argument(
        "items",
        type=str,
        help="Items to choose from",
        nargs="+",
    )

    shuffle_parser = subparsers.add_parser(
        "shuffle",
        help="Shuffle a list",
    )
    shuffle_parser.add_argument(
        "items",
        type=str,
        help="Items to shuffle",
        nargs="+",
    )

    args: argparse.Namespace = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
