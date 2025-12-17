import csv
import sys

from util import Node, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set(),
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set(),
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    # base case, source is the target, don't need to do any work
    if source == target:
        return []

    # make a source node and add it to the frontier
    start_node = Node(state=source, parent=None, action=None)
    # Frontier represents Nodes we have discovered but not yet explored
    # BFS to get the shortest path, use a queue frontier (fifo)
    frontier = QueueFrontier()
    frontier.add(start_node)

    # place to keep track of things we've seen already
    explored_nodes = set()
    # Loop until we find the target or exhaust the frontier
    while not frontier.empty():
        # get the next node to explore
        current_node = frontier.remove()
        # mark this node as explored
        explored_nodes.add(current_node.state)
        # get the neighbors for the current node
        for movie_id, neighbor_person_id in neighbors_for_person(current_node.state):
            # if we've already fully explored this, or it exists in the frontier to be explored, we can skip it
            if neighbor_person_id in explored_nodes or frontier.contains_state(
                neighbor_person_id
            ):
                continue
            # Otherwise create a new node for this neighbor
            # Set the parent to the current node, and which movie got us here
            neighbor_node = Node(
                state=neighbor_person_id, parent=current_node, action=movie_id
            )
            # check if we achieved our goal
            if neighbor_node.state == target:
                # We found the target, so we can build out the path to return
                path = []
                # this loop is a little weird but works to backtrack from the target to source
                while (
                    neighbor_node.parent is not None
                ):  # while we haven't reached the source
                    # add the movie and person to our path list
                    path.append((neighbor_node.action, neighbor_node.state))
                    # move up to the parent node so we can continue adding to our
                    # path list until we reach the source (e.g. the parent is None)
                    neighbor_node = neighbor_node.parent
                # reverse the path to get it from source to target and return it
                path.reverse()
                return path
            # They are not the target, so add them to the frontier to explore and continue our loop
            frontier.add(neighbor_node)
    # At this point we've exhausted the frontier without finding the target so we can return None
    return None


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
