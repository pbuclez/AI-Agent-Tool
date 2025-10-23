#!/usr/bin/env python3
"""
A module that generates random programming jokes.
Contains a collection of 10 short, funny programming jokes and randomly selects one.
"""

import random


def get_random_joke():
    """
    Returns a random programming joke from a collection of 10 jokes.
    
    Returns:
        str: A random programming joke
    """
    jokes = [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
        "Why don't programmers like nature? It has too many bugs.",
        "What do you call a programmer from Finland? Nerdic.",
        "Why do Java developers wear glasses? Because they can't C#!",
        "What's a programmer's favorite hangout place? The Foo Bar.",
        "Why did the programmer quit his job? He didn't get arrays.",
        "What do you call a programmer who doesn't comment their code? A silent partner.",
        "Why do programmers hate nature? It has too many bugs and not enough documentation.",
        "What's the object-oriented way to become wealthy? Inheritance."
    ]
    
    return random.choice(jokes)


def get_all_jokes():
    """
    Returns all jokes in the collection.
    
    Returns:
        list: A list of all programming jokes
    """
    return [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
        "Why don't programmers like nature? It has too many bugs.",
        "What do you call a programmer from Finland? Nerdic.",
        "Why do Java developers wear glasses? Because they can't C#!",
        "What's a programmer's favorite hangout place? The Foo Bar.",
        "Why did the programmer quit his job? He didn't get arrays.",
        "What do you call a programmer who doesn't comment their code? A silent partner.",
        "Why do programmers hate nature? It has too many bugs and not enough documentation.",
        "What's the object-oriented way to become wealthy? Inheritance."
    ]


def main():
    """
    Main function to demonstrate the joke generator.
    """
    print("🎭 Random Programming Joke Generator 🎭")
    print("=" * 40)
    print(f"Here's your random joke: {get_random_joke()}")
    print("\nAll available jokes:")
    for i, joke in enumerate(get_all_jokes(), 1):
        print(f"{i}. {joke}")


if __name__ == "__main__":
    main()
