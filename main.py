# Enhanced Disaster Rescue Planner (Final Version)


import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import heapq
import random


class DisasterResponsePlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("AI-Based Disaster Response Planner")
        self.root.geometry("1300x750")
        self.root.configure(bg="#2c3e50")

        # Graph representation
        self.graph = nx.Graph()
        self.locations = {}
        self.heuristics = {}

        # NEW FEATURES
        self.blocked_edges = set()
        self.danger_zones = ["Stranded Zone 1", "Stranded Zone 3"]

        # Build graph
        self.build_disaster_scenario()

        # Setup UI
        self.setup_ui()

    def build_disaster_scenario(self):
        """Build graph for disaster network"""

        locations_data = {
            "Command Center": (0, 0),
            "North Shelter": (2, 4),
            "South Shelter": (2, -3),
            "East Shelter": (5, 1),
            "West Shelter": (-4, 1),
            "Hospital A": (3, 2),
            "Hospital B": (-2, -2),
            "Fire Station": (1, 3),
            "Police Base": (-1, -1),
            "Stranded Zone 1": (4, 4),
            "Stranded Zone 2": (-3, 3),
            "Stranded Zone 3": (4, -2),
            "Stranded Zone 4": (-3, -3),
            "Resource Depot": (6, 0),
            "Temporary Camp": (-5, 0)
        }

        for name, coords in locations_data.items():
            self.locations[name] = coords
            self.graph.add_node(name, pos=coords)

        edges = [
            ("Command Center", "North Shelter", 4),
            ("Command Center", "South Shelter", 3),
            ("Command Center", "East Shelter", 5),
            ("Command Center", "West Shelter", 4),
            ("Command Center", "Hospital A", 3),
            ("Command Center", "Hospital B", 2),
            ("Command Center", "Fire Station", 2),
            ("Command Center", "Police Base", 1),
            ("North Shelter", "Stranded Zone 1", 2),
            ("East Shelter", "Stranded Zone 1", 3),
            ("East Shelter", "Stranded Zone 3", 3),
            ("West Shelter", "Stranded Zone 2", 2),
            ("South Shelter", "Stranded Zone 3", 2),
            ("South Shelter", "Stranded Zone 4", 3),
            ("Hospital A", "Stranded Zone 1", 4),
            ("Hospital B", "Stranded Zone 2", 3),
            ("Fire Station", "Stranded Zone 1", 3),
            ("Police Base", "Stranded Zone 2", 4),
            ("Resource Depot", "East Shelter", 2),
            ("Temporary Camp", "West Shelter", 2),
            ("Stranded Zone 1", "Stranded Zone 2", 5),
            ("Stranded Zone 3", "Stranded Zone 4", 4)
        ]

        for u, v, w in edges:
            self.graph.add_edge(u, v, weight=w)

        safe_zones = [
            "North Shelter", "South Shelter", "East Shelter",
            "West Shelter", "Hospital A", "Hospital B",
            "Temporary Camp", "Resource Depot"
        ]

        for node in self.graph.nodes():
            min_dist = float('inf')
            node_pos = self.locations[node]

            for sz in safe_zones:
                sz_pos = self.locations[sz]
                dist = ((node_pos[0] - sz_pos[0]) ** 2 +
                        (node_pos[1] - sz_pos[1]) ** 2) ** 0.5
                min_dist = min(min_dist, dist)

            self.heuristics[node] = min_dist

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # LEFT PANEL
        left_panel = tk.Frame(main_frame, bg="#34495e", width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)

        tk.Label(
            left_panel,
            text="🚨 AI Disaster Response Planner",
            font=("Arial", 16, "bold"),
            bg="#34495e",
            fg="white"
        ).pack(pady=15)

        # SOURCE
        tk.Label(
            left_panel,
            text="📍 Rescue Team Location:",
            font=("Arial", 11),
            bg="#34495e",
            fg="white"
        ).pack(anchor=tk.W, padx=10, pady=(10, 0))

        self.source_var = tk.StringVar(value="Command Center")

        source_combo = ttk.Combobox(
            left_panel,
            textvariable=self.source_var,
            values=list(self.locations.keys()),
            width=30
        )
        source_combo.pack(padx=10, pady=5)

        # DESTINATION
        tk.Label(
            left_panel,
            text="🎯 Affected Area / Goal:",
            font=("Arial", 11),
            bg="#34495e",
            fg="white"
        ).pack(anchor=tk.W, padx=10, pady=(10, 0))

        self.dest_var = tk.StringVar(value="Stranded Zone 1")

        dest_combo = ttk.Combobox(
            left_panel,
            textvariable=self.dest_var,
            values=list(self.locations.keys()),
            width=30
        )
        dest_combo.pack(padx=10, pady=5)

        # RESOURCE
        tk.Label(
            left_panel,
            text="📦 Resource Type:",
            font=("Arial", 11),
            bg="#34495e",
            fg="white"
        ).pack(anchor=tk.W, padx=10, pady=(10, 0))

        self.resource_var = tk.StringVar(value="Medical Supplies")

        resource_combo = ttk.Combobox(
            left_panel,
            textvariable=self.resource_var,
            values=[
                "Medical Supplies",
                "Food & Water",
                "Rescue Team",
                "Heavy Equipment",
                "Communication Gear"
            ],
            width=30
        )
        resource_combo.pack(padx=10, pady=5)

        # ALGORITHM
        tk.Label(
            left_panel,
            text="🤖 AI Search Algorithm:",
            font=("Arial", 11),
            bg="#34495e",
            fg="white"
        ).pack(anchor=tk.W, padx=10, pady=(10, 0))

        self.algo_var = tk.StringVar(value="A* Search")

        algo_combo = ttk.Combobox(
            left_panel,
            textvariable=self.algo_var,
            values=[
                "A* Search",
                "Best-First Search",
                "Dijkstra's Algorithm"
            ],
            width=30
        )
        algo_combo.pack(padx=10, pady=5)

        # PLAN BUTTON
        plan_btn = tk.Button(
            left_panel,
            text="🚁 Generate Optimal Rescue Plan",
            font=("Arial", 12, "bold"),
            bg="#e67e22",
            fg="white",
            command=self.generate_plan,
            padx=10,
            pady=5
        )
        plan_btn.pack(pady=10)

        # DISASTER BUTTON
        disaster_btn = tk.Button(
            left_panel,
            text="🔥 Simulate Disaster",
            font=("Arial", 11, "bold"),
            bg="#c0392b",
            fg="white",
            command=self.simulate_disaster
        )
        disaster_btn.pack(pady=10)

        # COMPARE BUTTON
        compare_btn = tk.Button(
            left_panel,
            text="📊 Compare Algorithms",
            font=("Arial", 11, "bold"),
            bg="#2980b9",
            fg="white",
            command=self.compare_algorithms
        )
        compare_btn.pack(pady=10)

        # RESULTS
        tk.Label(
            left_panel,
            text="📋 Rescue Plan & Metrics",
            font=("Arial", 12, "bold"),
            bg="#34495e",
            fg="white"
        ).pack(anchor=tk.W, padx=10, pady=(10, 0))

        self.results_text = scrolledtext.ScrolledText(
            left_panel,
            width=45,
            height=18,
            font=("Consolas", 10),
            bg="#ecf0f1"
        )
        self.results_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # RIGHT PANEL
        right_panel = tk.Frame(main_frame, bg="#2c3e50")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig, self.ax = plt.subplots(figsize=(7, 6), facecolor="#2c3e50")

        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.draw_graph()

    def draw_graph(self, path=None):
        self.ax.clear()

        pos = self.locations

        # NODE COLORS
        node_colors = []

        for node in self.graph.nodes():
            if node in self.danger_zones:
                node_colors.append("red")
            else:
                node_colors.append("#3498db")

        nx.draw_networkx_nodes(
            self.graph,
            pos,
            node_size=800,
            node_color=node_colors,
            alpha=0.9,
            ax=self.ax
        )

        # NORMAL EDGES
        normal_edges = [
            edge for edge in self.graph.edges()
            if edge not in self.blocked_edges and
            (edge[1], edge[0]) not in self.blocked_edges
        ]

        nx.draw_networkx_edges(
            self.graph,
            pos,
            edgelist=normal_edges,
            edge_color="#7f8c8d",
            width=2,
            alpha=0.7,
            ax=self.ax
        )

        # BLOCKED EDGES
        if self.blocked_edges:
            nx.draw_networkx_edges(
                self.graph,
                pos,
                edgelist=list(self.blocked_edges),
                edge_color="black",
                width=5,
                style="dashed",
                ax=self.ax
            )

        nx.draw_networkx_labels(
            self.graph,
            pos,
            font_size=9,
            font_weight="bold",
            ax=self.ax
        )

        edge_labels = nx.get_edge_attributes(self.graph, 'weight')

        nx.draw_networkx_edge_labels(
            self.graph,
            pos,
            edge_labels=edge_labels,
            font_size=8,
            ax=self.ax
        )

        # HIGHLIGHT PATH
        if path and len(path) > 1:
            path_edges = list(zip(path, path[1:]))

            nx.draw_networkx_edges(
                self.graph,
                pos,
                edgelist=path_edges,
                edge_color="#f1c40f",
                width=4,
                ax=self.ax
            )

            nx.draw_networkx_nodes(
                self.graph,
                pos,
                nodelist=path,
                node_color="#f39c12",
                node_size=900,
                ax=self.ax
            )

        # SOURCE & DESTINATION
        source = self.source_var.get()
        dest = self.dest_var.get()

        nx.draw_networkx_nodes(
            self.graph,
            pos,
            nodelist=[source],
            node_color="#2ecc71",
            node_size=1000,
            ax=self.ax
        )

        nx.draw_networkx_nodes(
            self.graph,
            pos,
            nodelist=[dest],
            node_color="#9b59b6",
            node_size=1000,
            ax=self.ax
        )

        self.ax.set_title(
            "Disaster Response Network Map",
            fontsize=14,
            color="white",
            pad=20
        )

        self.ax.set_facecolor("#2c3e50")
        self.ax.axis("off")

        self.canvas.draw()

    def heuristic(self, node, goal):
        node_pos = self.locations[node]
        goal_pos = self.locations[goal]

        return ((node_pos[0] - goal_pos[0]) ** 2 +
                (node_pos[1] - goal_pos[1]) ** 2) ** 0.5

    # A* SEARCH
    def a_star_search(self, start, goal):
        open_set = [(0, start)]

        g_score = {
            node: float('inf') for node in self.graph.nodes()
        }

        g_score[start] = 0

        came_from = {}
        nodes_expanded = 0

        while open_set:
            current = heapq.heappop(open_set)[1]
            nodes_expanded += 1

            if current == goal:
                path = []

                while current in came_from:
                    path.append(current)
                    current = came_from[current]

                path.append(start)
                path.reverse()

                return path, g_score[goal], nodes_expanded

            for neighbor in self.graph.neighbors(current):

                if (current, neighbor) in self.blocked_edges or \
                   (neighbor, current) in self.blocked_edges:
                    continue

                tentative_g = (
                    g_score[current] +
                    self.graph[current][neighbor]['weight']
                )

                if tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g

                    f_score = tentative_g + self.heuristic(neighbor, goal)

                    heapq.heappush(open_set, (f_score, neighbor))

        return None, float('inf'), nodes_expanded

    # BEST FIRST SEARCH
    def best_first_search(self, start, goal):
        open_set = [(self.heuristic(start, goal), start)]

        visited = set()
        came_from = {}
        nodes_expanded = 0

        while open_set:
            current = heapq.heappop(open_set)[1]
            nodes_expanded += 1

            if current == goal:
                path = []

                while current in came_from:
                    path.append(current)
                    current = came_from[current]

                path.append(start)
                path.reverse()

                cost = 0

                for i in range(len(path) - 1):
                    cost += self.graph[path[i]][path[i + 1]]['weight']

                return path, cost, nodes_expanded

            visited.add(current)

            for neighbor in self.graph.neighbors(current):

                if (current, neighbor) in self.blocked_edges or \
                   (neighbor, current) in self.blocked_edges:
                    continue

                if neighbor not in visited:
                    came_from[neighbor] = current

                    heapq.heappush(
                        open_set,
                        (self.heuristic(neighbor, goal), neighbor)
                    )

        return None, float('inf'), nodes_expanded

    # DIJKSTRA
    def dijkstra_search(self, start, goal):
        distances = {
            node: float('inf') for node in self.graph.nodes()
        }

        distances[start] = 0

        pq = [(0, start)]
        came_from = {}
        nodes_expanded = 0

        while pq:
            current_dist, current = heapq.heappop(pq)
            nodes_expanded += 1

            if current == goal:
                path = []

                while current in came_from:
                    path.append(current)
                    current = came_from[current]

                path.append(start)
                path.reverse()

                return path, distances[goal], nodes_expanded

            for neighbor in self.graph.neighbors(current):

                if (current, neighbor) in self.blocked_edges or \
                   (neighbor, current) in self.blocked_edges:
                    continue

                new_dist = (
                    distances[current] +
                    self.graph[current][neighbor]['weight']
                )

                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    came_from[neighbor] = current

                    heapq.heappush(pq, (new_dist, neighbor))

        return None, float('inf'), nodes_expanded

    # DISASTER SIMULATION
    def simulate_disaster(self):

        available_edges = [
            edge for edge in self.graph.edges()
            if edge not in self.blocked_edges and
            (edge[1], edge[0]) not in self.blocked_edges
        ]

        if not available_edges:
            messagebox.showinfo(
                "Simulation",
                "All roads are already blocked!"
            )
            return

        edge = random.choice(available_edges)

        self.blocked_edges.add(edge)

        self.results_text.insert(
            tk.END,
            f"\n🔥 ROAD BLOCKED: {edge}\n"
        )

        # AUTO RECALCULATE
        self.generate_plan()

    # COMPARE ALGORITHMS
    def compare_algorithms(self):
        source = self.source_var.get()
        destination = self.dest_var.get()

        algorithms = {
            "A*": self.a_star_search,
            "Best-First": self.best_first_search,
            "Dijkstra": self.dijkstra_search
        }

        self.results_text.delete(1.0, tk.END)

        self.results_text.insert(
            tk.END,
            "📊 ALGORITHM COMPARISON\n"
        )

        self.results_text.insert(
            tk.END,
            "=" * 50 + "\n\n"
        )

        for name, algo in algorithms.items():
            path, cost, expanded = algo(source, destination)

            self.results_text.insert(
                tk.END,
                f"🤖 {name}\n"
                f"Cost: {cost}\n"
                f"Nodes Expanded: {expanded}\n"
                f"Path Length: {len(path) if path else 0}\n\n"
            )

    # GENERATE PLAN
    def generate_plan(self):

        source = self.source_var.get()
        destination = self.dest_var.get()
        algorithm = self.algo_var.get()
        resource = self.resource_var.get()

        if source == destination:
            messagebox.showwarning(
                "Warning",
                "Source and destination cannot be the same!"
            )
            return

        if algorithm == "A* Search":
            path, cost, expanded = self.a_star_search(source, destination)

        elif algorithm == "Best-First Search":
            path, cost, expanded = self.best_first_search(source, destination)

        else:
            path, cost, expanded = self.dijkstra_search(source, destination)

        self.results_text.delete(1.0, tk.END)

        if path:
            self.results_text.insert(
                tk.END,
                "🚁 OPTIMAL RESCUE PLAN GENERATED\n"
            )

            self.results_text.insert(
                tk.END,
                "=" * 50 + "\n\n"
            )

            self.results_text.insert(
                tk.END,
                f"📦 Resource Type: {resource}\n"
            )

            self.results_text.insert(
                tk.END,
                f"🤖 Algorithm: {algorithm}\n"
            )

            self.results_text.insert(
                tk.END,
                f"📍 Start: {source}\n"
            )

            self.results_text.insert(
                tk.END,
                f"🎯 Goal: {destination}\n\n"
            )

            self.results_text.insert(
                tk.END,
                "🗺️ Optimal Route:\n"
            )

            for i, node in enumerate(path):
                self.results_text.insert(
                    tk.END,
                    f"  {i + 1}. {node}\n"
                )

            eta = cost * 5

            self.results_text.insert(
                tk.END,
                f"\n📊 Performance Metrics:\n"
            )

            self.results_text.insert(
                tk.END,
                f"  • Total Path Cost: {cost}\n"
            )

            self.results_text.insert(
                tk.END,
                f"  • Nodes Expanded: {expanded}\n"
            )

            self.results_text.insert(
                tk.END,
                f"  • Estimated Rescue Time: {eta} mins\n"
            )

            self.results_text.insert(
                tk.END,
                f"  • Stops Required: {len(path) - 1}\n"
            )

            efficiency = 100 - (
                expanded / len(self.graph.nodes()) * 20
            )

            efficiency = max(0, min(100, efficiency))

            self.results_text.insert(
                tk.END,
                f"  • Search Efficiency: {efficiency:.1f}%\n"
            )

            self.results_text.insert(
                tk.END,
                f"\n💡 Recommendation:\n"
            )

            if algorithm == "A* Search":
                self.results_text.insert(
                    tk.END,
                    "  A* gives optimal and intelligent routing.\n"
                )

            elif algorithm == "Best-First Search":
                self.results_text.insert(
                    tk.END,
                    "  Best-First is faster but not always optimal.\n"
                )

            else:
                self.results_text.insert(
                    tk.END,
                    "  Dijkstra guarantees shortest path.\n"
                )

            self.draw_graph(path)

        else:
            self.results_text.insert(
                tk.END,
                "❌ NO PATH FOUND!\n"
            )

            self.results_text.insert(
                tk.END,
                "All rescue routes are blocked.\n"
            )

            self.draw_graph()


if __name__ == "__main__":
    root = tk.Tk()
    app = DisasterResponsePlanner(root)
    root.mainloop()

