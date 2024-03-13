from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .family_tree import Person


def netwrokx(main_member: Person) -> None:
    import matplotlib.pyplot as plt
    import networkx as nx

    G = nx.DiGraph()

    def add_person_to_graph(person: Person):
        G.add_node(person.id, label=person.name)
        if person.has_spouse():
            G.add_edge(person.id, person.get_spouse().id, label="Spouse")
            G.add_node(person.get_spouse().id, label=person.get_spouse().name)
        if person.has_children():
            for child in person.get_children():
                G.add_edge(person.id, child.id, label="Child")
                add_person_to_graph(child)

    add_person_to_graph(main_member)

    pos = nx.kamada_kawai_layout(G)  # You can use other layout options as well
    labels = nx.get_edge_attributes(G, "label")
    node_labels = nx.get_node_attributes(G, "label")

    nx.draw(G, pos, with_labels=True, labels=node_labels)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.show()


def graphviz(
    main_member: Person,
    *,
    filename: str = "family_tree.png",
) -> None:
    from graphviz import Digraph

    dot = Digraph(comment="Family Tree")

    def add_person_to_graph(person: Person):
        dot.node(str(person.id), label=person.name)
        if person.has_spouse():
            dot.node(str(person.get_spouse().id), label=person.get_spouse().name)
            dot.edge(str(person.id), str(person.get_spouse().id), label="Spouse")
        if person.has_children():
            for child in person.get_children():
                dot.node(str(child.id), label=child.name)
                dot.edge(str(person.id), str(child.id), label="Child")
                add_person_to_graph(child)

    add_person_to_graph(main_member)
    dot.render(filename, format="png", cleanup=True)


def mermaid(main_member: Person) -> str:
    """Returns a mermaid formatted string to represent a family tree."""
    mermaid = ""
    top_level_decleration = ["graph TD;"]

    def add_person_to_mermaid(person: Person):
        nonlocal mermaid

        if person.has_spouse():
            spouse = person.get_spouse()
            top_level_decleration.append(f"  {spouse.id}>{spouse.name}];")
            mermaid += f"\n  {person.id} --> |Spouse| {spouse.id};"

        if person.has_children():
            top_level_decleration.append(f"  {person.id}[[{person.name}]];")
            for child in person.get_children():
                mermaid += f"\n  {person.id} --> |Child| {child.id};"
                add_person_to_mermaid(child)
        else:
            top_level_decleration.append(f"  {person.id}([{person.name}]);")

    add_person_to_mermaid(main_member)
    return "\n".join(top_level_decleration) + "\n" + mermaid
