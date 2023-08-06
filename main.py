import argparse
import enum
import secrets
import sys
import textwrap


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
    length: int = args.length
    exclude: set[str] = set(args.exclude) if args.exclude else set()
    exclude_categories: list[str] = args.exclude_category or []
    include: set[str] = set(args.include) if args.include else set()
    include_categories: list[str] = args.include_category or []

    if type_ == "name":
        generate_names(count=length)
    elif type_ == "pass":
        generate_password(
            length, exclude, exclude_categories, include, include_categories
        )
    else:
        raise ValueError("Invalid type")


def generate_names(count: int) -> None:
    with open("nouns.txt") as nouns_file:
        nouns: list[str] = nouns_file.read().splitlines()
    with open("adjectives.txt") as adjectives_file:
        adjectives: list[str] = adjectives_file.read().splitlines()
    for _ in range(count):
        print(secrets.choice(adjectives) + secrets.choice(nouns))


def generate_password(
    length: int,
    exclude: set[str],
    exclude_categories: list[str],
    include: set[str],
    include_categories: list[str],
) -> None:
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


def parse_args() -> argparse.Namespace:
    description: str = textwrap.dedent(
        """\
        Generate random text.
        
        You cannot both include and exclude characters or character categories.
        """
    )
    parser = argparse.ArgumentParser(
        prog="rand",
        description=description,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "type",
        type=str,
        choices=["name", "pass"],
        help="Type of random text to generate",
    )
    parser.add_argument(
        "length",
        type=int,
        help="Length of text to generate",
    )
    parser.add_argument(
        "-x",
        "--exclude",
        type=str,
        help="Characters to exclude from random password generation",
    )
    parser.add_argument(
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
    parser.add_argument(
        "-i",
        "--include",
        type=str,
        help="Characters to include in random password generation",
    )
    parser.add_argument(
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
    args: argparse.Namespace = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
