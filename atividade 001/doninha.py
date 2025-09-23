import random

# Target phrase
TARGET = "METHINKS IT IS LIKE A WEASEL"

# Parameters
NUM_PHRASES = 100
MUTATION_RATE = 0.05  # chance of mutation per character
generation = 0

# Alphabet
ALPHABET = "".join(chr(i) for i in range(65, 91)) + " "


def random_phrase(size):
    """Generates a random phrase of the given size."""
    return "".join(random.choice(ALPHABET) for _ in range(size))


def accuracy(candidate):
    """Returns the number of characters matching the target phrase."""
    matches = 0
    for c, t in zip(candidate, TARGET):
        if c == t:
            matches += 1
    return matches


def mutate(phrase, rate=0.05):
    """Applies random mutations to a phrase."""
    new_phrase = []
    for c in phrase:
        if random.random() < rate:
            new_phrase.append(random.choice(ALPHABET))
        else:
            new_phrase.append(c)
    return "".join(new_phrase)


def best_child(phrase, n=100):
    """Generates n children and returns the closest one to the target phrase."""
    children = [mutate(phrase, MUTATION_RATE) for _ in range(n)]
    return max(children, key=accuracy)


initial = input(
    "Enter the initial phrase (or press ENTER for a random one): "
)

if initial == "":
    initial = random_phrase(len(TARGET))
else:
    initial = initial.upper().ljust(len(TARGET))[:len(TARGET)]

# Main loop
while initial != TARGET:
    generation += 1
    initial = best_child(initial)
    print(f"Generation {generation}: {initial}")

print(f"Target reached in {generation} generations.")