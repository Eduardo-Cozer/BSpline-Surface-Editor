import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np
import math
import json
from bspline_surface import BSplineSurface

class BSplineEditor:
    def __init__(self, root):
        self.root = root
        self.window_coords = np.array([[-500, 500], [-500, 500]])
        self.viewport_coords = np.array([[0, 800], [0, 600]]) 
        self.WIDTH = int(self.viewport_coords[0, 1] - self.viewport_coords[0, 0])
        self.HEIGHT = int(self.viewport_coords[1, 1] - self.viewport_coords[1, 0])
        self.root.title("Editor de Superfícies B-Spline")

        self.canvas = tk.Canvas(root, width=self.WIDTH, height=self.HEIGHT, bg="#1A1A1A")
        self.canvas.pack(side=tk.LEFT)

        self.control_frame = ttk.Frame(root)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas_scroll = ttk.Scrollbar(self.control_frame, orient=tk.VERTICAL)
        self.canvas_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.controls_canvas = tk.Canvas(self.control_frame, yscrollcommand=self.canvas_scroll.set, width=450)
        self.controls_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas_scroll.config(command=self.controls_canvas.yview)

        self.inner_frame = ttk.Frame(self.controls_canvas)
        self.controls_canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.inner_frame.bind("<Configure>", lambda e: self.controls_canvas.configure(scrollregion=self.controls_canvas.bbox("all")))

        def on_mousewheel(event):
            self.controls_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def on_mousewheel_linux(event):
            if event.num == 4:
                self.controls_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.controls_canvas.yview_scroll(1, "units")

        self.controls_canvas.bind_all("<MouseWheel>", on_mousewheel)
        self.controls_canvas.bind_all("<Button-4>", on_mousewheel_linux)
        self.controls_canvas.bind_all("<Button-5>", on_mousewheel_linux)

        self.m = tk.IntVar(value=4)
        self.n = tk.IntVar(value=4)
        self.order_i = tk.IntVar(value=3)
        self.order_j = tk.IntVar(value=3)
        self.surface = BSplineSurface(self.m.get(), self.n.get())
        self.resolution_i = tk.IntVar(value=10)
        self.resolution_j = tk.IntVar(value=10)
        self.vrp_x = tk.DoubleVar(value=50.0)
        self.vrp_y = tk.DoubleVar(value=50.0)
        self.vrp_z = tk.DoubleVar(value=50.0)
        self.p_x = tk.DoubleVar(value=0.0)
        self.p_y = tk.DoubleVar(value=0.0)
        self.p_z = tk.DoubleVar(value=0.0)
        self.vrp = np.array([self.vrp_x.get(), self.vrp_y.get(), self.vrp_z.get()])
        self.p = np.array([self.p_x.get(), self.p_y.get(), self.p_z.get()])
        self.vup = np.array([0.0, 1.0, 0.0])  
        
        self.rotacao_vars = [tk.DoubleVar(value=0.0) for _ in range(3)]
        self.rotacao_value = np.array([0.0, 0.0, 0.0])
        self.translacao_vars = [tk.DoubleVar(value=0.0) for _ in range(3)]
        self.translacao_value = np.array([0.0, 0.0, 0.0])
        self.escala = tk.DoubleVar(value=1.0)
        self.escala_value = np.array([1.0, 1.0, 1.0])
        self.cor_aresta_visivel = [tk.DoubleVar(value=0.0) for _ in range(3)]
        self.cor_aresta_visivel[1].set(1.0)  
        self.cor_aresta_visivel_value = np.array([0.0, 1.0, 0.0])
        self.cor_aresta_invisivel = [tk.DoubleVar(value=0.0) for _ in range(3)]
        self.cor_aresta_invisivel[0].set(1.0)  
        self.cor_aresta_invisivel_value = np.array([1.0, 0.0, 0.0])
        self.background_color = [tk.DoubleVar(value=0.1) for _ in range(3)]
        self.background_color_value = np.array([0.1, 0.1, 0.1])
        self.mostrar_pontos = tk.BooleanVar(value=True)
        self.window_min_x = tk.DoubleVar(value=self.window_coords[0, 0])
        self.window_min_y = tk.DoubleVar(value=self.window_coords[1, 0])
        self.window_max_x = tk.DoubleVar(value=self.window_coords[0, 1])
        self.window_max_y = tk.DoubleVar(value=self.window_coords[1, 1])
        self.viewport_min_u = tk.DoubleVar(value=self.viewport_coords[0, 0])
        self.viewport_max_u = tk.DoubleVar(value=self.viewport_coords[0, 1])
        self.viewport_min_v = tk.DoubleVar(value=self.viewport_coords[1, 0])
        self.viewport_max_v = tk.DoubleVar(value=self.viewport_coords[1, 1])
        self.atualizar_malha = True

        self.intensidade_ambiente = tk.DoubleVar(value=0.3)
        self.intensidade_ambiente_value = 0.3
        self.intensidade_luz = tk.DoubleVar(value=1.0)
        self.intensidade_luz_value = 1.0
        self.vetor_l = [tk.DoubleVar(value=1.0) for _ in range(3)]
        self.vetor_l_value = np.array([1.0, 1.0, 1.0])
        self.ka = tk.DoubleVar(value=0.3)
        self.ka_value = 0.3
        self.kd = tk.DoubleVar(value=0.7)
        self.kd_value = 0.7
        self.ks = tk.DoubleVar(value=0.5)
        self.ks_value = 0.5
        self.n_shininess = tk.IntVar(value=32)
        self.n_shininess_value = 32
        self.sombreamento = tk.StringVar(value="wireframe")
        self.z_buffer = None
        self.color_buffer = None

        self.setup_controls()
        self.render()

    def setup_controls(self):
        row = 0
        ttk.Label(self.inner_frame, text="Dimensões").grid(row=row, column=0, pady=5, sticky="w")
        row += 1
        ttk.Label(self.inner_frame, text="M").grid(row=row, column=0, sticky="w")
        entry_m = ttk.Entry(self.inner_frame, textvariable=self.m)
        entry_m.grid(row=row, column=1)
        entry_m.bind("<FocusOut>", lambda e: self.update_transform())
        row += 1
        ttk.Label(self.inner_frame, text="N").grid(row=row, column=0, sticky="w")
        entry_n = ttk.Entry(self.inner_frame, textvariable=self.n)
        entry_n.grid(row=row, column=1)
        entry_n.bind("<FocusOut>", lambda e: self.update_transform())
        row += 1
        """ttk.Label(self.inner_frame, text="Ordem I").grid(row=row, column=0, sticky="w")
        entry_order_i = ttk.Entry(self.inner_frame, textvariable=self.order_i)
        entry_order_i.grid(row=row, column=1)
        entry_order_i.bind("<FocusOut>", lambda e: self.update_transform())
        row += 1
        ttk.Label(self.inner_frame, text="Ordem J").grid(row=row, column=0, sticky="w")
        entry_order_j = ttk.Entry(self.inner_frame, textvariable=self.order_j)
        entry_order_j.grid(row=row, column=1)
        entry_order_j.bind("<FocusOut>", lambda e: self.update_transform())
        row += 1"""
        ttk.Label(self.inner_frame, text="Resolução I").grid(row=row, column=0, sticky="w")
        entry_resolution_i = ttk.Entry(self.inner_frame, textvariable=self.resolution_i)
        entry_resolution_i.grid(row=row, column=1)
        entry_resolution_i.bind("<FocusOut>", lambda e: self.update_transform())
        row += 1
        ttk.Label(self.inner_frame, text="Resolução J").grid(row=row, column=0, sticky="w")
        entry_resolution_j = ttk.Entry(self.inner_frame, textvariable=self.resolution_j)
        entry_resolution_j.grid(row=row, column=1)
        entry_resolution_j.bind("<FocusOut>", lambda e: self.update_transform())
        row += 1

        ttk.Label(self.inner_frame, text="Transformações").grid(row=row, column=0, pady=5, sticky="w")
        row += 1
        ttk.Label(self.inner_frame, text="Rotação (x, y, z)").grid(row=row, column=0, sticky="w")
        row += 1
        for i, axis in enumerate(["X", "Y", "Z"]):
            ttk.Scale(self.inner_frame, from_=-180, to=180, variable=self.rotacao_vars[i], command=self.update_transform).grid(row=row, column=0, columnspan=2, sticky="ew")
            ttk.Label(self.inner_frame, text=axis).grid(row=row, column=2, sticky="w")
            row += 1
        ttk.Label(self.inner_frame, text="Translação (x, y, z)").grid(row=row, column=0, sticky="w")
        row += 1
        for i, axis in enumerate(["X", "Y", "Z"]):
            ttk.Scale(self.inner_frame, from_=-50, to=50, variable=self.translacao_vars[i], command=self.update_transform).grid(row=row, column=0, columnspan=2, sticky="ew")
            ttk.Label(self.inner_frame, text=axis).grid(row=row, column=2, sticky="w")
            row += 1
        ttk.Label(self.inner_frame, text="Escala").grid(row=row, column=0, sticky="w")
        ttk.Scale(self.inner_frame, from_=0.1, to=10, variable=self.escala, command=self.update_transform).grid(row=row, column=1, sticky="ew")
        row += 1

        ttk.Label(self.inner_frame, text="Cores").grid(row=row, column=0, pady=5, sticky="w")
        row += 1
        ttk.Label(self.inner_frame, text="Cor Aresta Visível (R, G, B)").grid(row=row, column=0, sticky="w")
        row += 1
        for i in range(3):
            ttk.Scale(self.inner_frame, from_=0, to=1, variable=self.cor_aresta_visivel[i], command=self.update_transform).grid(row=row, column=0, columnspan=2, sticky="ew")
            row += 1
        ttk.Label(self.inner_frame, text="Cor Aresta Invisível (R, G, B)").grid(row=row, column=0, sticky="w")
        row += 1
        for i in range(3):
            ttk.Scale(self.inner_frame, from_=0, to=1, variable=self.cor_aresta_invisivel[i], command=self.update_transform).grid(row=row, column=0, columnspan=2, sticky="ew")
            row += 1
        ttk.Label(self.inner_frame, text="Cor de Fundo (R, G, B)").grid(row=row, column=0, sticky="w")
        row += 1
        for i in range(3):
            ttk.Scale(self.inner_frame, from_=0, to=1, variable=self.background_color[i], command=self.update_transform).grid(row=row, column=0, columnspan=2, sticky="ew")
            row += 1

        ttk.Label(self.inner_frame, text="VRP (Ponto de Vista)").grid(row=row, column=0, pady=5, sticky="w")
        row += 1
        ttk.Label(self.inner_frame, text="VRP X").grid(row=row, column=0, sticky="w")
        entry_vrp_x = ttk.Entry(self.inner_frame, textvariable=self.vrp_x)
        entry_vrp_x.grid(row=row, column=1)
        entry_vrp_x.bind("<FocusOut>", lambda e: self.update_transform())
        row += 1
        ttk.Label(self.inner_frame, text="VRP Y").grid(row=row, column=0, sticky="w")
        entry_vrp_y = ttk.Entry(self.inner_frame, textvariable=self.vrp_y)
        entry_vrp_y.grid(row=row, column=1)
        entry_vrp_y.bind("<FocusOut>", lambda e: self.update_transform())
        row += 1
        ttk.Label(self.inner_frame, text="VRP Z").grid(row=row, column=0, sticky="w")
        entry_vrp_z = ttk.Entry(self.inner_frame, textvariable=self.vrp_z)
        entry_vrp_z.grid(row=row, column=1)
        entry_vrp_z.bind("<FocusOut>", lambda e: self.update_transform())
        row += 1

        ttk.Label(self.inner_frame, text="P (Ponto de Foco)").grid(row=row, column=0, pady=5, sticky="w")
        row += 1
        ttk.Label(self.inner_frame, text="P X").grid(row=row, column=0, sticky="w")
        entry_p_x = ttk.Entry(self.inner_frame, textvariable=self.p_x)
        entry_p_x.grid(row=row, column=1)
        entry_p_x.bind("<FocusOut>", lambda e: self.update_transform())
        row += 1
        ttk.Label(self.inner_frame, text="P Y").grid(row=row, column=0, sticky="w")
        entry_p_y = ttk.Entry(self.inner_frame, textvariable=self.p_y)
        entry_p_y.grid(row=row, column=1)
        entry_p_y.bind("<FocusOut>", lambda e: self.update_transform())
        row += 1
        ttk.Label(self.inner_frame, text="P Z").grid(row=row, column=0, sticky="w")
        entry_p_z = ttk.Entry(self.inner_frame, textvariable=self.p_z)
        entry_p_z.grid(row=row, column=1)
        entry_p_z.bind("<FocusOut>", lambda e: self.update_transform())
        row += 1

        ttk.Label(self.inner_frame, text="Opções").grid(row=row, column=0, pady=5, sticky="w")
        row += 1
        ttk.Checkbutton(self.inner_frame, text="Mostrar Pontos", variable=self.mostrar_pontos, command=self.update_transform).grid(row=row, column=0, sticky="w")
        row += 1
        ttk.Button(self.inner_frame, text="Editar Pontos de Controle", command=self.editar_pontos_controle).grid(row=row, column=0, sticky="w")
        row += 1

        ttk.Label(self.inner_frame, text="Coordenadas").grid(row=row, column=0, pady=5, sticky="w")
        row += 1
        ttk.Label(self.inner_frame, text="Window Min (x, y)").grid(row=row, column=0, sticky="w")
        row += 1
        entry_window_min_x = ttk.Entry(self.inner_frame, textvariable=self.window_min_x)
        entry_window_min_x.grid(row=row, column=0)
        entry_window_min_x.bind("<FocusOut>", lambda e: self.update_transform())
        entry_window_min_y = ttk.Entry(self.inner_frame, textvariable=self.window_min_y)
        entry_window_min_y.grid(row=row, column=1)
        entry_window_min_y.bind("<FocusOut>", lambda e: self.update_transform())
        row += 1
        ttk.Label(self.inner_frame, text="Window Max (x, y)").grid(row=row, column=0, sticky="w")
        row += 1
        entry_window_max_x = ttk.Entry(self.inner_frame, textvariable=self.window_max_x)
        entry_window_max_x.grid(row=row, column=0)
        entry_window_max_x.bind("<FocusOut>", lambda e: self.update_transform())
        entry_window_max_y = ttk.Entry(self.inner_frame, textvariable=self.window_max_y)
        entry_window_max_y.grid(row=row, column=1)
        entry_window_max_y.bind("<FocusOut>", lambda e: self.update_transform())
        row += 1
        ttk.Label(self.inner_frame, text="Viewport (x_min, x_max, y_min, y_max)").grid(row=row, column=0, sticky="w")
        row += 1
        entry_viewport_min_u = ttk.Entry(self.inner_frame, textvariable=self.viewport_min_u)
        entry_viewport_min_u.grid(row=row, column=0)
        entry_viewport_min_u.bind("<FocusOut>", lambda e: self.update_transform())
        entry_viewport_max_u = ttk.Entry(self.inner_frame, textvariable=self.viewport_max_u)
        entry_viewport_max_u.grid(row=row, column=1)
        entry_viewport_max_u.bind("<FocusOut>", lambda e: self.update_transform())
        row += 1
        entry_viewport_min_v = ttk.Entry(self.inner_frame, textvariable=self.viewport_min_v)
        entry_viewport_min_v.grid(row=row, column=0)
        entry_viewport_min_v.bind("<FocusOut>", lambda e: self.update_transform())
        entry_viewport_max_v = ttk.Entry(self.inner_frame, textvariable=self.viewport_max_v)
        entry_viewport_max_v.grid(row=row, column=1)
        entry_viewport_max_v.bind("<FocusOut>", lambda e: self.update_transform())
        row += 1

        ttk.Label(self.inner_frame, text="Iluminação").grid(row=row, column=0, pady=5, sticky="w")
        row += 1
        ttk.Label(self.inner_frame, text="Intensidade Ambiente").grid(row=row, column=0, sticky="w")
        ttk.Scale(self.inner_frame, from_=0.0, to=1.0, variable=self.intensidade_ambiente, command=self.update_transform).grid(row=row, column=1, sticky="ew")
        row += 1
        ttk.Label(self.inner_frame, text="Intensidade Luz").grid(row=row, column=0, sticky="w")
        ttk.Scale(self.inner_frame, from_=0.0, to=2.0, variable=self.intensidade_luz, command=self.update_transform).grid(row=row, column=1, sticky="ew")
        row += 1
        ttk.Label(self.inner_frame, text="Vetor L (x, y, z)").grid(row=row, column=0, sticky="w")
        row += 1
        for i, axis in enumerate(["X", "Y", "Z"]):
            ttk.Scale(self.inner_frame, from_=-1.0, to=1.0, variable=self.vetor_l[i], command=self.update_transform).grid(row=row, column=0, columnspan=2, sticky="ew")
            ttk.Label(self.inner_frame, text=axis).grid(row=row, column=2, sticky="w")
            row += 1
        ttk.Label(self.inner_frame, text="Ka").grid(row=row, column=0, sticky="w")
        ttk.Scale(self.inner_frame, from_=0.0, to=1.0, variable=self.ka, command=self.update_transform).grid(row=row, column=1, sticky="ew")
        row += 1
        ttk.Label(self.inner_frame, text="Kd").grid(row=row, column=0, sticky="w")
        ttk.Scale(self.inner_frame, from_=0.0, to=1.0, variable=self.kd, command=self.update_transform).grid(row=row, column=1, sticky="ew")
        row += 1
        ttk.Label(self.inner_frame, text="Ks").grid(row=row, column=0, sticky="w")
        ttk.Scale(self.inner_frame, from_=0.0, to=1.0, variable=self.ks, command=self.update_transform).grid(row=row, column=1, sticky="ew")
        row += 1
        ttk.Label(self.inner_frame, text="n").grid(row=row, column=0, sticky="w")
        entry_lines = ttk.Entry(self.inner_frame, textvariable=self.n_shininess)
        entry_lines.grid(row=row, column=1)
        entry_lines.bind("<FocusOut>", lambda e: self.update_transform())
        row += 1

        ttk.Label(self.inner_frame, text="Sombreamento").grid(row=row, column=0, pady=5, sticky="w")
        row += 1
        ttk.Radiobutton(self.inner_frame, text="Wireframe", variable=self.sombreamento, value="wireframe", command=self.update_transform).grid(row=row, column=0, sticky="w")
        row += 1
        ttk.Radiobutton(self.inner_frame, text="Constante", variable=self.sombreamento, value="constante", command=self.update_transform).grid(row=row, column=0, sticky="w")
        row += 1
        ttk.Radiobutton(self.inner_frame, text="Gouraud", variable=self.sombreamento, value="gouraud", command=self.update_transform).grid(row=row, column=0, sticky="w")
        row += 1
        ttk.Radiobutton(self.inner_frame, text="Phong", variable=self.sombreamento, value="phong", command=self.update_transform).grid(row=row, column=0, sticky="w")
        row += 1

        ttk.Button(self.inner_frame, text="Salvar Malha", command=self.salvar_malha).grid(row=row, column=0, pady=5)
        row += 1
        ttk.Button(self.inner_frame, text="Abrir Malha", command=self.abrir_malha).grid(row=row, column=0, pady=5)
        row += 1

        ttk.Button(self.inner_frame, text="Atualizar Malha", command=self.render).grid(row=row, column=0, pady=5)
        row += 1

    def update_transform(self, *args):
        self.rotacao_value = np.array([var.get() for var in self.rotacao_vars])
        self.translacao_value = np.array([var.get() for var in self.translacao_vars])
        self.escala_value = np.array([self.escala.get(), self.escala.get(), self.escala.get()])
        self.vrp = np.array([self.vrp_x.get(), self.vrp_y.get(), self.vrp_z.get()])
        self.p = np.array([self.p_x.get(), self.p_y.get(), self.p_z.get()])
        self.cor_aresta_visivel_value = np.array([var.get() for var in self.cor_aresta_visivel])
        self.cor_aresta_invisivel_value = np.array([var.get() for var in self.cor_aresta_invisivel])
        self.background_color_value = np.array([var.get() for var in self.background_color])
        self.intensidade_ambiente_value = self.intensidade_ambiente.get()
        self.intensidade_luz_value = self.intensidade_luz.get()
        self.vetor_l_value = np.array([var.get() for var in self.vetor_l])
        self.ka_value = self.ka.get()
        self.kd_value = self.kd.get()
        self.ks_value = self.ks.get()
        self.n_shininess_value = self.n_shininess.get()

        self.window_coords = np.array([
            [self.window_min_x.get(), self.window_max_x.get()],
            [self.window_min_y.get(), self.window_max_y.get()]
        ])
        self.viewport_coords = np.array([
            [self.viewport_min_u.get(), self.viewport_max_u.get()],
            [self.viewport_min_v.get(), self.viewport_max_v.get()]
        ])
        
        m_atual = max(4, min(100, self.m.get()))
        n_atual = max(4, min(100, self.n.get()))
        order_i_atual = self.order_i.get()
        order_j_atual = self.order_j.get()
        resolution_i_atual = self.resolution_i.get()
        resolution_j_atual = self.resolution_j.get()

        if m_atual != self.surface.m or n_atual != self.surface.n:
            self.surface = BSplineSurface(m_atual, n_atual)
            self.atualizar_malha = True

        self.order_i.set(order_i_atual)
        self.order_j.set(order_j_atual)

        self.resolution_i.set(resolution_i_atual)
        self.resolution_j.set(resolution_j_atual)

        self.canvas.configure(bg=f"#{int(self.background_color_value[0]*255):02x}{int(self.background_color_value[1]*255):02x}{int(self.background_color_value[2]*255):02x}")
        self.atualizar_malha = True

    def produto_escalar(self, v1, v2):
        return np.dot(v1, v2)

    def produto_vetorial(self, v1, v2):
        return np.cross(v1, v2)

    def normalizar(self, v):
        norma = np.linalg.norm(v)
        return v / norma if norma != 0 else np.zeros_like(v)

    def calcular_centroide(self, face):
        return np.mean(face, axis=0)

    def calcular_distancia(self, vrp, centroide):
        return np.linalg.norm(vrp - centroide)

    def vis_normal(self, face, vrp):
        if len(face) < 3:
            return False
        v1 = face[1] - face[0]
        v2 = face[2] - face[1]
        vetN = self.produto_vetorial(v1, v2)
        vetN_normalizado = self.normalizar(vetN)
        centroide = self.calcular_centroide(face)
        vetO = vrp - centroide
        vetO_normalizado = self.normalizar(vetO)
        return self.produto_escalar(vetN_normalizado, vetO_normalizado) > 0

    def calcular_normal(self, face):
        v1 = face[1] - face[0]
        v2 = face[2] - face[1]
        vetN = self.produto_vetorial(v1, v2)
        return self.normalizar(vetN)

    def calcular_bspline(self):
        result = self.surface.interpolate(self.resolution_i.get(), self.resolution_j.get(), self.order_i.get(), self.order_j.get())
        if isinstance(result, np.ndarray) and result.ndim == 3 and result.shape[2] == 3:
            X = result[:, :, 0]
            Y = result[:, :, 1]
            Z = result[:, :, 2]
            return X, Y, Z
        else:
            raise ValueError(f"Esperado um array tridimensional (n, m, 3) ou uma tupla (X, Y, Z), mas recebido: {type(result)}")

    def ordenar_faces_por_distancia(self, faces, vrp):
        return sorted(faces, key=lambda x: self.calcular_distancia(vrp, self.calcular_centroide(x[1])), reverse=True)

    def matriz_rotacao(self, angulos):
        rot_x = np.radians(angulos[0])
        rot_y = np.radians(angulos[1])
        rot_z = np.radians(angulos[2])
        rot_x_matriz = np.array([[1, 0, 0, 0], 
                                 [0, math.cos(rot_x), -math.sin(rot_x), 0], 
                                 [0, math.sin(rot_x), math.cos(rot_x), 0], 
                                 [0, 0, 0, 1]])
        rot_y_matriz = np.array([[math.cos(rot_y), 0, math.sin(rot_y), 0], 
                                 [0, 1, 0, 0], 
                                 [-math.sin(rot_y), 0, math.cos(rot_y), 0], 
                                 [0, 0, 0, 1]])
        rot_z_matriz = np.array([[math.cos(rot_z), -math.sin(rot_z), 0, 0], 
                                 [math.sin(rot_z), math.cos(rot_z), 0, 0], 
                                 [0, 0, 1, 0], 
                                 [0, 0, 0, 1]])
        return np.dot(np.dot(rot_z_matriz, rot_y_matriz), rot_x_matriz)

    def matriz_translacao(self, translacao):
        return np.array([[1, 0, 0, translacao[0]], 
                         [0, 1, 0, translacao[1]], 
                         [0, 0, 1, translacao[2]], 
                         [0, 0, 0, 1]])

    def matriz_escala(self, escala):
        return np.array([[escala[0], 0, 0, 0], 
                         [0, escala[1], 0, 0], 
                         [0, 0, escala[2], 0], 
                         [0, 0, 0, 1]])

    def matriz_sru_to_src(self, vrp, p, vup):
        vnn = self.normalizar(vrp - p)
        vvn = self.normalizar(vup - np.dot(vup, vnn) * vnn)
        vun = self.normalizar(self.produto_vetorial(vvn, vnn))

        M = [[vun[0], vun[1], vun[2], self.produto_escalar(-vrp,vun)],
            [vvn[0], vvn[1], vvn[2], self.produto_escalar(-vrp,vvn)],
            [vnn[0], vnn[1], vnn[2], self.produto_escalar(-vrp,vnn)],
            [0, 0, 0, 1]]

        return M

    def aplicar_transformacoes(self, pontos):
        rotacao_matriz = self.matriz_rotacao(self.rotacao_value)
        translacao_matriz = self.matriz_translacao(self.translacao_value)
        escala_matriz = self.matriz_escala(self.escala_value * 100)
        pontos_homogeneos = np.concatenate([pontos, np.ones((pontos.shape[0], pontos.shape[1], 1))], axis=2)
        pontos_transformados = np.einsum('ij,klj->kli', escala_matriz, pontos_homogeneos)
        pontos_transformados = np.einsum('ij,klj->kli', rotacao_matriz, pontos_transformados)
        pontos_transformados = np.einsum('ij,klj->kli', translacao_matriz, pontos_transformados)
        return pontos_transformados[:, :, :3]
    
    def aplicar_projecao_viewport_isometrica(self, pontos, window, viewport):
        src_matriz = self.matriz_sru_to_src(self.vrp, self.p, self.vup)

        #x_min = window[0, 0] x_max = window[0, 1] y_min = window[1, 0] y_max = window[1, 1]
        #u_min = viewport[0, 0] u_max = viewport[0, 1] v_min = viewport[1, 0] v_max = viewport[1, 1]

        sx = (viewport[0, 1] - viewport[0, 0]) / (window[0, 1] - window[0, 0])
        sy = (viewport[1, 0] - viewport[1, 1]) / (window[1, 1] - window[1, 0])
        tx = -window[0, 0] * sx + viewport[0, 0]
        ty = window[1, 0] * (viewport[1, 1] - viewport[1, 0]) / (window[1, 1] - window[1, 0]) + viewport[1, 1]

        jp_matriz = np.array([
            [sx, 0, 0, tx],
            [0, sy, 0, ty],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        iso_matriz = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        
        sru_srt_matriz =  jp_matriz @ iso_matriz @ src_matriz
        pontos_homogeneos = np.concatenate([pontos, np.ones((pontos.shape[0], pontos.shape[1], 1))], axis=2)
        pontos_transformados = np.einsum('ij,klj->kli', sru_srt_matriz, pontos_homogeneos)
        return pontos_transformados[:, :, :3]
    
    def ponto_dentro_borda(self, ponto, borda, tipo_borda):
        x, y = ponto
        if tipo_borda == "LEFT":
            return x >= self.viewport_coords[0, 0]
        elif tipo_borda == "RIGHT":
            return x <= self.viewport_coords[0, 1]
        elif tipo_borda == "BOTTOM":
            return y >= self.viewport_coords[1, 0]
        elif tipo_borda == "TOP":
            return y <= self.viewport_coords[1, 1]
        return False

    def calcular_intersecao(self, p1, p2, borda, tipo_borda):
        x1, y1 = p1
        x2, y2 = p2
        if tipo_borda == "LEFT":
            x = self.viewport_coords[0, 0]
            t = (x - x1) / (x2 - x1) if x2 != x1 else 0
            y = y1 + t * (y2 - y1)
            return np.array([x, y])
        elif tipo_borda == "RIGHT":
            x = self.viewport_coords[0, 1]
            t = (x - x1) / (x2 - x1) if x2 != x1 else 0
            y = y1 + t * (y2 - y1)
            return np.array([x, y])
        elif tipo_borda == "BOTTOM":
            y = self.viewport_coords[1, 0]
            t = (y - y1) / (y2 - y1) if y2 != y1 else 0
            x = x1 + t * (x2 - x1)
            return np.array([x, y])
        elif tipo_borda == "TOP":
            y = self.viewport_coords[1, 1]
            t = (y - y1) / (y2 - y1) if y2 != y1 else 0
            x = x1 + t * (x2 - x1)
            return np.array([x, y])
        return None

    def recorte_2d_viewport(self, face_2d, indices_originais=None):
        if indices_originais is None:
            indices_originais = list(range(len(face_2d)))
        bordas = ["LEFT", "RIGHT", "BOTTOM", "TOP"]
        face_atual = face_2d
        indices_atual = indices_originais

        for borda in bordas:
            nova_face = []
            novos_indices = []
            num_vertices = len(face_atual)

            for i in range(num_vertices):
                p1 = face_atual[i]
                p2 = face_atual[(i + 1) % num_vertices]
                idx1 = indices_atual[i]
                idx2 = indices_atual[(i + 1) % num_vertices]

                dentro_p1 = self.ponto_dentro_borda(p1, None, borda)
                dentro_p2 = self.ponto_dentro_borda(p2, None, borda)

                if dentro_p1 and dentro_p2:
                    nova_face.append(p2)
                    novos_indices.append(idx2)
                elif not dentro_p1 and dentro_p2:
                    intersecao = self.calcular_intersecao(p1, p2, None, borda)
                    if intersecao is not None:
                        nova_face.append(intersecao)
                        novos_indices.append(-1)
                    nova_face.append(p2)
                    novos_indices.append(idx2)
                elif dentro_p1 and not dentro_p2:
                    intersecao = self.calcular_intersecao(p1, p2, None, borda)
                    if intersecao is not None:
                        nova_face.append(intersecao)
                        novos_indices.append(-1)

            face_atual = np.array(nova_face) if len(nova_face) >= 3 else np.array([])
            indices_atual = novos_indices
            if len(face_atual) == 0:
                return np.array([]), []

        return face_atual, indices_atual
    
    def render_wireframe(self, faces_2d, faces_3d, z_values):
        for face_2d, face_3d, face_z in zip(faces_2d, faces_3d, z_values):
            if len(face_2d) < 3:
                continue

            rgb = "#1A1A1A"

            y_coords = [v[1] for v in face_2d]
            x_coords = [v[0] for v in face_2d]
            z_coords = face_z
            ymin = max(0, int(min(y_coords)))
            ymax = min(self.HEIGHT - 1, int(max(y_coords)))
            xmin = max(0, int(min(x_coords)))
            xmax = min(self.WIDTH - 1, int(max(x_coords)))

            num_vertices = len(face_2d)
            active_edges = []

            for i in range(num_vertices):
                j = (i + 1) % num_vertices
                v1 = face_2d[i]
                v2 = face_2d[j]
                z1 = face_z[i]
                z2 = face_z[j]

                if v1[1] > v2[1]:
                    v1, v2 = v2, v1
                    z1, z2 = z2, z1

                y_start = max(ymin, int(v1[1]))
                y_end = min(ymax, int(v2[1]) - 1) if v2[1] > v1[1] else y_start

                if y_end >= y_start:
                    dx = v2[0] - v1[0]
                    dy = v2[1] - v1[1]
                    dz = z2 - z1
                    if dy != 0:
                        tx = dx / dy
                        tz = dz / dy
                        x = v1[0]
                        z = z1
                        active_edges.append({
                            'x': x,
                            'z': z,
                            'tx': tx,
                            'tz': tz,
                            'y_max': y_end,
                            'y_min': y_start
                        })

            for y in range(ymin, ymax + 1):
                if y < 0 or y >= self.HEIGHT:
                    continue

                current_edges = [edge for edge in active_edges if y >= edge['y_min'] and y <= edge['y_max']]
                if len(current_edges) < 2:
                    continue

                current_edges.sort(key=lambda e: e['x'])

                for i in range(0, len(current_edges), 2):
                    if i + 1 >= len(current_edges):
                        break
                    edge1 = current_edges[i]
                    edge2 = current_edges[i + 1]

                    x_start = edge1['x']
                    x_end = edge2['x']
                    z_start = edge1['z']
                    z_end = edge2['z']

                    x_start_int = int(np.ceil(x_start))
                    x_end_int = int(np.floor(x_end))

                    if x_end_int >= x_start_int and x_start_int < self.WIDTH:
                        x_end_int = min(x_end_int, self.WIDTH - 1)
                        x_start_int = max(x_start_int, 0)

                        if x_end_int > x_start_int:
                            dz_dx = (z_end - z_start) / (x_end - x_start) if x_end != x_start else 0
                            tz_scanline = dz_dx if not np.isnan(dz_dx) and not np.isinf(dz_dx) else 0
                        else:
                            tz_scanline = 0

                        z_current = z_start + (x_start_int - x_start) * tz_scanline


                        for x_pixel in range(x_start_int, x_end_int + 1):
                            if x_pixel < 0 or x_pixel >= self.WIDTH:
                                continue
                            z_pixel = z_current
                            if z_pixel < self.z_buffer[y, x_pixel]:
                                self.canvas.create_line(x_pixel, y, x_pixel + 1, y, fill=rgb)
                                self.z_buffer[y, x_pixel] = z_pixel
                            z_current += tz_scanline

                for edge in current_edges:
                    edge['x'] += edge['tx']
                    edge['z'] += edge['tz']
                #print(f"Scanline y={y}, active_edges={[current_edges]}")

                active_edges = [edge for edge in active_edges if y < edge['y_max']]

    def render_constante(self, faces_2d, faces_3d, z_values):
        Ia = self.intensidade_ambiente_value  
        Il = self.intensidade_luz_value      
        Ka = self.ka_value                    
        Kd = self.kd_value                         
        Ks = self.ks_value                 
        n = self.n_shininess_value     

        light_pos = np.array([self.vetor_l_value[0] * 100, 
                            self.vetor_l_value[1] * 100, 
                            self.vetor_l_value[2] * 100])

        for face_2d, face_3d, face_z in zip(faces_2d, faces_3d, z_values):
            if len(face_2d) < 3: 
                continue

            centroid = np.mean(face_3d, axis=0)

            normal = self.calcular_normal(face_3d)
            #normal = normal / np.linalg.norm(normal) if np.linalg.norm(normal) > 0 else normal

            Ia_total = Ia * Ka

            L = light_pos - centroid
            L = L / np.linalg.norm(L) if np.linalg.norm(L) > 0 else L
            N_dot_L = np.dot(normal, L)
            Id_total = Il * Kd * max(0, N_dot_L) if N_dot_L > 0 else 0

            if(N_dot_L > 0):
                R = 2 * (np.dot(normal, L)) * normal - L
                R = R / np.linalg.norm(R) if np.linalg.norm(R) > 0 else R
                S = self.vrp - centroid
                S = S / np.linalg.norm(S) if np.linalg.norm(S) > 0 else S
                R_dot_S = np.dot(R, S)
                Is_total = Il * Ks * (max(0, R_dot_S) ** n) if R_dot_S > 0 else 0

            It = Ia_total + Id_total + Is_total
            It = max(0, min(1, It)) 
            rgb = f"#{int(It*255):02x}{int(It*255):02x}{int(It*255):02x}"

            y_coords = [v[1] for v in face_2d]
            x_coords = [v[0] for v in face_2d]
            z_coords = face_z
            ymin = max(0, int(min(y_coords)))
            ymax = min(self.HEIGHT - 1, int(max(y_coords)))
            xmin = max(0, int(min(x_coords)))
            xmax = min(self.WIDTH - 1, int(max(x_coords)))

            num_vertices = len(face_2d)
            active_edges = []

            for i in range(num_vertices):
                j = (i + 1) % num_vertices
                v1 = face_2d[i]
                v2 = face_2d[j]
                z1 = face_z[i]
                z2 = face_z[j]

                if v1[1] > v2[1]:
                    v1, v2 = v2, v1
                    z1, z2 = z2, z1

                y_start = max(ymin, int(v1[1]))
                y_end = min(ymax, int(v2[1]) - 1) if v2[1] > v1[1] else y_start

                if y_end >= y_start:
                    dx = v2[0] - v1[0]
                    dy = v2[1] - v1[1]
                    dz = z2 - z1
                    if dy != 0:
                        tx = dx / dy
                        tz = dz / dy
                        x = v1[0]
                        z = z1
                        active_edges.append({
                            'x': x,
                            'z': z,
                            'tx': tx,
                            'tz': tz,
                            'y_max': y_end,
                            'y_min': y_start
                        })

            for y in range(ymin, ymax + 1):
                if y < 0 or y >= self.HEIGHT:
                    continue

                current_edges = [edge for edge in active_edges if y >= edge['y_min'] and y <= edge['y_max']]
                if len(current_edges) < 2:
                    continue

                current_edges.sort(key=lambda e: e['x'])

                for i in range(0, len(current_edges), 2):
                    if i + 1 >= len(current_edges):
                        break
                    edge1 = current_edges[i]
                    edge2 = current_edges[i + 1]

                    x_start = edge1['x']
                    x_end = edge2['x']
                    z_start = edge1['z']
                    z_end = edge2['z']

                    x_start_int = int(np.ceil(x_start))
                    x_end_int = int(np.floor(x_end))

                    if x_end_int >= x_start_int and x_start_int < self.WIDTH:
                        x_end_int = min(x_end_int, self.WIDTH - 1)
                        x_start_int = max(x_start_int, 0)

                        if x_end_int > x_start_int:
                            dz_dx = (z_end - z_start) / (x_end - x_start) if x_end != x_start else 0
                            tz_scanline = dz_dx if not np.isnan(dz_dx) and not np.isinf(dz_dx) else 0
                        else:
                            tz_scanline = 0

                        z_current = z_start + (x_start_int - x_start) * tz_scanline

                        for x_pixel in range(x_start_int, x_end_int + 1):
                            if x_pixel < 0 or x_pixel >= self.WIDTH:
                                continue
                            z_pixel = z_current
                            if z_pixel < self.z_buffer[y, x_pixel]:
                                self.canvas.create_line(x_pixel, y, x_pixel + 1, y, fill=rgb)
                                self.z_buffer[y, x_pixel] = z_pixel
                            z_current += tz_scanline

                for edge in current_edges:
                    edge['x'] += edge['tx']
                    edge['z'] += edge['tz']
                #print(f"Scanline y={y}, active_edges={[current_edges]}")

                active_edges = [edge for edge in active_edges if y < edge['y_max']]
    
    def render_gouraud(self, faces_2d, faces_3d, z_values):
        Ia = self.intensidade_ambiente_value
        Il = self.intensidade_luz_value
        Ka = self.ka_value
        Kd = self.kd_value
        Ks = self.ks_value
        n = self.n_shininess_value
        light_pos = np.array([self.vetor_l_value[0] * 100, 
                            self.vetor_l_value[1] * 100, 
                            self.vetor_l_value[2] * 100])

        vertex_normals = {}
        for i, face in enumerate(faces_3d):
            normal = self.calcular_normal(face)
            #normal = normal / np.linalg.norm(normal) if np.linalg.norm(normal) > 0 else normal
            for vertex in face:
                vertex_tuple = tuple(vertex)
                if vertex_tuple in vertex_normals:
                    vertex_normals[vertex_tuple] += normal
                else:
                    vertex_normals[vertex_tuple] = normal

        for vertex in vertex_normals:
            vertex_normals[vertex] = vertex_normals[vertex] / np.linalg.norm(vertex_normals[vertex]) if np.linalg.norm(vertex_normals[vertex]) > 0 else vertex_normals[vertex]

        vertex_intensities = {}
        for vertex_tuple, normal in vertex_normals.items():
            vertex = np.array(vertex_tuple)

            Ia_total = Ia * Ka

            L = light_pos - vertex
            L = L / np.linalg.norm(L) if np.linalg.norm(L) > 0 else L
            N_dot_L = np.dot(normal, L)
            Id_total = Il * Kd * max(0, N_dot_L) if N_dot_L > 0 else 0

            if(N_dot_L > 0):
                R = 2 * (np.dot(normal, L)) * normal - L
                R = R / np.linalg.norm(R) if np.linalg.norm(R) > 0 else R
                S = self.vrp - vertex
                S = S / np.linalg.norm(S) if np.linalg.norm(S) > 0 else S
                R_dot_S = np.dot(R, S)
                Is_total = Il * Ks * (max(0, R_dot_S) ** n) if R_dot_S > 0 else 0

            It = Ia_total + Id_total + Is_total
            It = max(0, min(1, It))
            vertex_intensities[vertex_tuple] = It

        for face_2d, face_3d, face_z in zip(faces_2d, faces_3d, z_values):
            if len(face_2d) < 3:
                continue

            y_coords = [v[1] for v in face_2d]
            x_coords = [v[0] for v in face_2d]
            z_coords = face_z
            ymin = max(0, int(min(y_coords)))
            ymax = min(self.HEIGHT - 1, int(max(y_coords)))
            xmin = max(0, int(min(x_coords)))
            xmax = min(self.WIDTH - 1, int(max(x_coords)))

            num_vertices = len(face_2d)
            active_edges = []

            vertex_intensities_face = [vertex_intensities[tuple(face_3d[i])] for i in range(num_vertices)]

            for i in range(num_vertices):
                j = (i + 1) % num_vertices
                v1 = face_2d[i]
                v2 = face_2d[j]
                z1 = face_z[i]
                z2 = face_z[j]
                I1 = vertex_intensities_face[i]
                I2 = vertex_intensities_face[j]

                if v1[1] > v2[1]:
                    v1, v2 = v2, v1
                    z1, z2 = z2, z1
                    I1, I2 = I2, I1

                y_start = max(ymin, int(v1[1]))
                y_end = min(ymax, int(v2[1]) - 1) if v2[1] > v1[1] else y_start

                if y_end >= y_start:
                    dx = v2[0] - v1[0]
                    dy = v2[1] - v1[1]
                    dz = z2 - z1
                    dI = I2 - I1
                    if dy != 0:
                        tx = dx / dy
                        tz = dz / dy
                        tI = dI / dy
                        x = v1[0]
                        z = z1
                        I = I1
                        active_edges.append({
                            'x': x,
                            'z': z,
                            'tx': tx,
                            'tz': tz,
                            'tI': tI,
                            'I': I,
                            'y_max': y_end,
                            'y_min': y_start
                        })

            for y in range(ymin, ymax + 1):
                if y < 0 or y >= self.HEIGHT:
                    continue

                current_edges = [edge for edge in active_edges if y >= edge['y_min'] and y <= edge['y_max']]
                if len(current_edges) < 2:
                    continue

                current_edges.sort(key=lambda e: e['x'])

                for i in range(0, len(current_edges), 2):
                    if i + 1 >= len(current_edges):
                        break
                    edge1 = current_edges[i]
                    edge2 = current_edges[i + 1]

                    x_start = edge1['x']
                    x_end = edge2['x']
                    z_start = edge1['z']
                    z_end = edge2['z']
                    I_start = edge1['I']
                    I_end = edge2['I']

                    x_start_int = int(np.ceil(x_start))
                    x_end_int = int(np.floor(x_end))

                    if x_end_int >= x_start_int and x_start_int < self.WIDTH:
                        x_end_int = min(x_end_int, self.WIDTH - 1)
                        x_start_int = max(x_start_int, 0)

                        if x_end_int > x_start_int:
                            dz_dx = (z_end - z_start) / (x_end - x_start) if x_end != x_start else 0
                            dI_dx = (I_end - I_start) / (x_end - x_start) if x_end != x_start else 0
                            tz_scanline = dz_dx if not np.isnan(dz_dx) and not np.isinf(dz_dx) else 0
                            tI_scanline = dI_dx if not np.isnan(dI_dx) and not np.isinf(dI_dx) else 0
                        else:
                            tz_scanline = 0
                            tI_scanline = 0

                        z_current = z_start + (x_start_int - x_start) * tz_scanline
                        I_current = I_start + (x_start_int - x_start) * tI_scanline

                        for x_pixel in range(x_start_int, x_end_int + 1):
                            if x_pixel < 0 or x_pixel >= self.WIDTH:
                                continue
                            z_pixel = z_current
                            if z_pixel < self.z_buffer[y, x_pixel]:
                                It = max(0, min(1, I_current))
                                rgb = f"#{int(It*255):02x}{int(It*255):02x}{int(It*255):02x}"
                                self.canvas.create_line(x_pixel, y, x_pixel + 1, y, fill=rgb)
                                self.z_buffer[y, x_pixel] = z_pixel
                            z_current += tz_scanline
                            I_current += tI_scanline

                for edge in current_edges:
                    edge['x'] += edge['tx']
                    edge['z'] += edge['tz']
                    edge['I'] += edge['tI']
                #print(f"Scanline y={y}, active_edges={[current_edges]}")

                active_edges = [edge for edge in active_edges if y < edge['y_max']]

    def render_phong(self, faces_2d, faces_3d, z_values):
        Ia = self.intensidade_ambiente_value
        Il = self.intensidade_luz_value
        Ka = self.ka_value
        Kd = self.kd_value
        Ks = self.ks_value
        n = self.n_shininess_value
        light_pos = np.array([self.vetor_l_value[0] * 100, 
                            self.vetor_l_value[1] * 100, 
                            self.vetor_l_value[2] * 100])

        all_vertices = np.concatenate([face for face in faces_3d])
        centroid_objeto = np.mean(all_vertices, axis=0)

        L = light_pos - centroid_objeto
        L = L / np.linalg.norm(L) if np.linalg.norm(L) > 0 else L
        S = self.vrp - centroid_objeto
        S = S / np.linalg.norm(S) if np.linalg.norm(S) > 0 else S
        H = L + S
        H = H / np.linalg.norm(H) if np.linalg.norm(H) > 0 else H

        vertex_normals = {}
        for i, face in enumerate(faces_3d):
            normal = self.calcular_normal(face)
            #normal = normal / np.linalg.norm(normal) if np.linalg.norm(normal) > 0 else normal
            for vertex in face:
                vertex_tuple = tuple(vertex)
                if vertex_tuple in vertex_normals:
                    vertex_normals[vertex_tuple] += normal
                else:
                    vertex_normals[vertex_tuple] = normal

        for vertex in vertex_normals:
            vertex_normals[vertex] = vertex_normals[vertex] / np.linalg.norm(vertex_normals[vertex]) if np.linalg.norm(vertex_normals[vertex]) > 0 else vertex_normals[vertex]

        for face_2d, face_3d, face_z in zip(faces_2d, faces_3d, z_values):
            if len(face_2d) < 3:
                continue

            y_coords = [v[1] for v in face_2d]
            x_coords = [v[0] for v in face_2d]
            z_coords = face_z
            ymin = max(0, int(min(y_coords)))
            ymax = min(self.HEIGHT - 1, int(max(y_coords)))
            xmin = max(0, int(min(x_coords)))
            xmax = min(self.WIDTH - 1, int(max(x_coords)))

            num_vertices = len(face_2d)
            active_edges = []

            vertex_normals_face = [vertex_normals[tuple(face_3d[i])] for i in range(num_vertices)]

            for i in range(num_vertices):
                j = (i + 1) % num_vertices
                v1 = face_2d[i]
                v2 = face_2d[j]
                z1 = face_z[i]
                z2 = face_z[j]
                N1 = vertex_normals_face[i]
                N2 = vertex_normals_face[j]

                if v1[1] > v2[1]:
                    v1, v2 = v2, v1
                    z1, z2 = z2, z1
                    N1, N2 = N2, N1

                y_start = max(ymin, int(v1[1]))
                y_end = min(ymax, int(v2[1]) - 1) if v2[1] > v1[1] else y_start

                if y_end >= y_start:
                    dx = v2[0] - v1[0]
                    dy = v2[1] - v1[1]
                    dz = z2 - z1
                    dN = N2 - N1 
                    if dy != 0:
                        tx = dx / dy
                        tz = dz / dy
                        tNi = dN[0] / dy
                        tNj = dN[1] / dy
                        tNk = dN[2] / dy 
                        x = v1[0]
                        z = z1
                        Ni = N1[0]
                        Nj = N1[1]
                        Nk = N1[2]
                        active_edges.append({
                            'x': x,
                            'z': z,
                            'tx': tx,
                            'tz': tz,
                            'tNi': tNi,
                            'tNj': tNj,
                            'tNk': tNk,
                            'Ni': Ni,
                            'Nj': Nj,
                            'Nk': Nk,
                            'y_max': y_end,
                            'y_min': y_start
                        })

            for y in range(ymin, ymax + 1):
                if y < 0 or y >= self.HEIGHT:
                    continue

                current_edges = [edge for edge in active_edges if y >= edge['y_min'] and y <= edge['y_max']]
                if len(current_edges) < 2:
                    continue

                current_edges.sort(key=lambda e: e['x'])

                for i in range(0, len(current_edges), 2):
                    if i + 1 >= len(current_edges):
                        break
                    edge1 = current_edges[i]
                    edge2 = current_edges[i + 1]

                    x_start = edge1['x']
                    x_end = edge2['x']
                    z_start = edge1['z']
                    z_end = edge2['z']
                    Ni_start = edge1['Ni']
                    Nj_start = edge1['Nj']
                    Nk_start = edge1['Nk']
                    Ni_end = edge2['Ni']
                    Nj_end = edge2['Nj']
                    Nk_end = edge2['Nk']

                    x_start_int = int(np.ceil(x_start))
                    x_end_int = int(np.floor(x_end))

                    if x_end_int >= x_start_int and x_start_int < self.WIDTH:
                        x_end_int = min(x_end_int, self.WIDTH - 1)
                        x_start_int = max(x_start_int, 0)

                        if x_end_int > x_start_int:
                            dz_dx = (z_end - z_start) / (x_end - x_start) if x_end != x_start else 0
                            dNi_dx = (Ni_end - Ni_start) / (x_end - x_start) if x_end != x_start else 0
                            dNj_dx = (Nj_end - Nj_start) / (x_end - x_start) if x_end != x_start else 0
                            dNk_dx = (Nk_end - Nk_start) / (x_end - x_start) if x_end != x_start else 0
                            tz_scanline = dz_dx if not np.isnan(dz_dx) and not np.isinf(dz_dx) else 0
                            tNi_scanline = dNi_dx if not np.isnan(dNi_dx) and not np.isinf(dNi_dx) else 0
                            tNj_scanline = dNj_dx if not np.isnan(dNj_dx) and not np.isinf(dNj_dx) else 0
                            tNk_scanline = dNk_dx if not np.isnan(dNk_dx) and not np.isinf(dNk_dx) else 0
                        else:
                            tz_scanline = 0
                            tNi_scanline = 0
                            tNj_scanline = 0
                            tNk_scanline = 0

                        z_current = z_start + (x_start_int - x_start) * tz_scanline
                        Ni_current = Ni_start + (x_start_int - x_start) * tNi_scanline
                        Nj_current = Nj_start + (x_start_int - x_start) * tNj_scanline
                        Nk_current = Nk_start + (x_start_int - x_start) * tNk_scanline

                        for x_pixel in range(x_start_int, x_end_int + 1):
                            if x_pixel < 0 or x_pixel >= self.WIDTH:
                                continue
                            z_pixel = z_current
                            if z_pixel < self.z_buffer[y, x_pixel]:
                                N_pixel = np.array([Ni_current, Nj_current, Nk_current])
                                N_pixel = N_pixel / np.linalg.norm(N_pixel) if np.linalg.norm(N_pixel) > 0 else N_pixel

                                Ia_total = Ia * Ka
                                N_dot_L = np.dot(N_pixel, L)
                                Id_total = Il * Kd * max(0, N_dot_L) if N_dot_L > 0 else 0
                                if(N_dot_L > 0):
                                    N_dot_H = np.dot(N_pixel, H)
                                    Is_total = Il * Ks * (max(0, N_dot_H) ** n) if N_dot_H > 0 else 0
                                It = Ia_total + Id_total + Is_total
                                It = max(0, min(1, It))
                                rgb = f"#{int(It*255):02x}{int(It*255):02x}{int(It*255):02x}"
                                self.canvas.create_line(x_pixel, y, x_pixel + 1, y, fill=rgb)
                                self.z_buffer[y, x_pixel] = z_pixel
                                

                            z_current += tz_scanline
                            Ni_current += tNi_scanline
                            Nj_current += tNj_scanline
                            Nk_current += tNk_scanline

                for edge in current_edges:
                    edge['x'] += edge['tx']
                    edge['z'] += edge['tz']
                    edge['Ni'] += edge['tNi']
                    edge['Nj'] += edge['tNj']
                    edge['Nk'] += edge['tNk']
                #print(f"Scanline y={y}, active_edges={[current_edges]}")

                active_edges = [edge for edge in active_edges if y < edge['y_max']]

    def render(self):
        if self.atualizar_malha:
            self.canvas.delete("all")
            self.z_buffer = np.full((self.HEIGHT, self.WIDTH), np.inf)
            self.color_buffer = np.zeros((self.HEIGHT, self.WIDTH, 3))

            pontos_controle = self.surface.cm
            #print("Pontos de controle iniciais:\n", pontos_controle)

            X, Y, Z = self.calcular_bspline()
            pontos_interpolados = np.stack([X, Y, Z], axis=2)
            #print("Pontos interpolados antes das transformações:\n", pontos_interpolados)

            pontos_interpolados_transformados = self.aplicar_transformacoes(pontos_interpolados)
            #print("Pontos interpolados após transformações:\n", pontos_interpolados_transformados)

            pontos_interpolados_projetados = self.aplicar_projecao_viewport_isometrica(
                pontos_interpolados_transformados, self.window_coords, self.viewport_coords
            )

            pontos_interpolados_2d = pontos_interpolados_projetados[:, :, :2]
            pontos_interpolados_z = pontos_interpolados_projetados[:, :, 2]
            #print("Pontos 2D projetados:\n", pontos_interpolados_2d)

            faces_3d = []
            faces_2d = []
            faces_z = []
            for i in range(pontos_interpolados_projetados.shape[0] - 1):
                for j in range(pontos_interpolados_projetados.shape[1] - 1):
                    v1_3d = pontos_interpolados_transformados[i, j]
                    v2_3d = pontos_interpolados_transformados[i + 1, j]
                    v3_3d = pontos_interpolados_transformados[i + 1, j + 1]
                    v4_3d = pontos_interpolados_transformados[i, j + 1]
                    face_3d = np.array([v1_3d, v2_3d, v3_3d, v4_3d])

                    v1_2d = pontos_interpolados_2d[i, j]
                    v2_2d = pontos_interpolados_2d[i + 1, j]
                    v3_2d = pontos_interpolados_2d[i + 1, j + 1]
                    v4_2d = pontos_interpolados_2d[i, j + 1]
                    face_2d = np.array([v1_2d, v2_2d, v3_2d, v4_2d])
                    
                    z1 = pontos_interpolados_z[i, j]
                    z2 = pontos_interpolados_z[i + 1, j]
                    z3 = pontos_interpolados_z[i + 1, j + 1]
                    z4 = pontos_interpolados_z[i, j + 1]
                    face_z = np.array([z1, z2, z3, z4])

                    face_2d_recortada, indices_recortados = self.recorte_2d_viewport(face_2d, list(range(4)))
                    if len(face_2d_recortada) > 0:
                        new_face_z = []
                        for idx in indices_recortados:
                            if idx >= 0: 
                                new_face_z.append(face_z[idx])
                            else:  
                                new_face_z.append(np.mean(face_z))
                        new_face_z = np.array(new_face_z)
                        faces_3d.append(face_3d)
                        faces_2d.append(face_2d_recortada)
                        faces_z.append(new_face_z)         

            faces_with_indices = list(enumerate(faces_3d))
            faces_with_indices_sorted = self.ordenar_faces_por_distancia(faces_with_indices, self.vrp)
            indices_ordenados = [index for index, _ in faces_with_indices_sorted]
            faces_3d_ordenadas = [faces_3d[idx] for idx in indices_ordenados]
            faces_2d_ordenadas = [faces_2d[idx] for idx in indices_ordenados]
            faces_z_ordenadas = [faces_z[idx] for idx in indices_ordenados]

            """
            faces_3d_visiveis = []
            faces_2d_visiveis = []
            faces_z_visiveis = []
            for face_3d, face_2d, face_z in zip(faces_3d_ordenadas, faces_2d_ordenadas, faces_z_ordenadas):
                if self.vis_normal(face_3d, self.vrp):
                    faces_3d_visiveis.append(face_3d)
                    faces_2d_visiveis.append(face_2d)
                    faces_z_visiveis.append(face_z)"""
            
            faces_2d_filtradas = []
            faces_3d_filtradas = []
            faces_z_filtradas = []
            for face_2d, face_3d, face_z in zip(faces_2d_ordenadas, faces_3d_ordenadas, faces_z_ordenadas):
                if len(face_2d) <= len(face_3d):
                    faces_2d_filtradas.append(face_2d)
                    faces_3d_filtradas.append(face_3d)
                    faces_z_filtradas.append(face_z)

            if self.sombreamento.get() == "wireframe":
                self.render_wireframe(faces_2d_ordenadas, faces_3d_ordenadas, faces_z_ordenadas)
            elif self.sombreamento.get() == "constante":
                self.render_constante(faces_2d_ordenadas, faces_3d_ordenadas, faces_z_ordenadas)
            elif self.sombreamento.get() == "gouraud":
                self.render_gouraud(faces_2d_filtradas, faces_3d_filtradas, faces_z_filtradas)
            elif self.sombreamento.get() == "phong":
                self.render_phong(faces_2d_filtradas, faces_3d_filtradas, faces_z_filtradas)

            if self.sombreamento.get() == "wireframe":
                for face_2d, face_3d in zip(faces_2d_ordenadas, faces_3d_ordenadas):
                    if len(face_2d) < 3:
                        continue
                    cor_aresta = self.cor_aresta_visivel_value if self.vis_normal(face_3d, self.vrp) else self.cor_aresta_invisivel_value
                    rgb = f"#{int(cor_aresta[0]*255):02x}{int(cor_aresta[1]*255):02x}{int(cor_aresta[2]*255):02x}"
                    for i in range(len(face_2d)):
                        p1 = face_2d[i]
                        p2 = face_2d[(i + 1) % len(face_2d)]
                        self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=rgb)

            if self.mostrar_pontos.get():
                pontos_controle_transformados = self.aplicar_transformacoes(pontos_controle.copy())
                pontos_controle_transformados_2d = self.aplicar_projecao_viewport_isometrica(
                    pontos_controle_transformados, self.window_coords, self.viewport_coords
                )[:, :, :2]
                #print("Pontos de controle 2D projetados:\n", pontos_controle_transformados_2d)
                for i in range(pontos_controle_transformados_2d.shape[0]):
                    for j in range(pontos_controle_transformados_2d.shape[1]):
                        ponto = pontos_controle_transformados_2d[i, j]
                        self.canvas.create_oval(ponto[0]-3, ponto[1]-3, ponto[0]+3, ponto[1]+3, fill="yellow", outline="yellow")

            self.atualizar_malha = False

    def editar_pontos_controle(self):
        top = tk.Toplevel(self.root)
        top.title("Editar Pontos de Controle")

        canvas = tk.Canvas(top, width=400, height=300)
        scrollbar = ttk.Scrollbar(top, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        canvas.configure(yscrollcommand=scrollbar.set)

        frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        m, n = self.surface.cm.shape[:2]
        entries = {}
        
        for i in range(m):
            for j in range(n):
                ponto = self.surface.cm[i, j]
                ttk.Label(frame, text=f"i={i}, j={j}").grid(row=i*n+j, column=0, padx=5, pady=2)
                for k, coord in enumerate(["x", "y", "z"]):
                    var = tk.DoubleVar(value=ponto[k])
                    ttk.Entry(frame, textvariable=var, width=8).grid(row=i*n+j, column=k+1, padx=5, pady=2)
                    entries[(i, j, k)] = var

        ttk.Button(frame, text="Salvar", command=lambda: self.save_control_points(entries, top)).grid(row=m*n, column=1, pady=10)

        frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Button-4>", lambda event: canvas.yview_scroll(-1, "units")) 
        canvas.bind_all("<Button-5>", lambda event: canvas.yview_scroll(1, "units"))  

    def save_control_points(self, entries, top):
        m, n = self.surface.cm.shape[:2]
        for i in range(m):
            for j in range(n):
                ponto = [entries[(i, j, k)].get() for k in range(3)]
                self.surface.cm[i, j] = np.array(ponto)
        top.destroy()
        self.atualizar_malha = True

    def salvar_malha(self):
        data = {
            "m": self.m.get(),
            "n": self.n.get(),
            "order_i": self.order_i.get(),
            "order_j": self.order_j.get(),
            "resolution_i": self.resolution_i.get(),
            "resolution_j": self.resolution_j.get(),
            "pontos_controle": self.surface.cm.tolist(),
            "rotacao": [var.get() for var in self.rotacao_vars],
            "translacao": [var.get() for var in self.translacao_vars],
            "escala": self.escala.get(),
            "cor_aresta_visivel": [var.get() for var in self.cor_aresta_visivel],
            "cor_aresta_invisivel": [var.get() for var in self.cor_aresta_invisivel],
            "background_color": [var.get() for var in self.background_color],
            "mostrar_pontos": self.mostrar_pontos.get(),
            "window_coords": self.window_coords.tolist(),
            "viewport_coords": self.viewport_coords.tolist(),
            "vrp": [self.vrp_x.get(), self.vrp_y.get(), self.vrp_z.get()],
            "p": [self.p_x.get(), self.p_y.get(), self.p_z.get()],
            "intensidade_ambiente": self.intensidade_ambiente.get(),
            "intensidade_luz": self.intensidade_luz.get(),
            "vetor_l": [var.get() for var in self.vetor_l],
            "ka": self.ka.get(),
            "kd": self.kd.get(),
            "ks": self.ks.get(),
            "n_shininess": self.n_shininess.get(),
            "sombreamento": self.sombreamento.get()
        }

        with tk.filedialog.asksaveasfile(defaultextension=".json", filetypes=[("JSON files", "*.json")]) as f:
            if f:
                json.dump(data, f, indent=4)
                print("Malha salva com sucesso!")

    def abrir_malha(self):
        with tk.filedialog.askopenfile(defaultextension=".json", filetypes=[("JSON files", "*.json")]) as f:
            if f:
                data = json.load(f)
                
                self.m.set(data["m"])
                self.n.set(data["n"])
                self.order_i.set(data["order_i"])
                self.order_j.set(data["order_j"])
                self.resolution_i.set(data["resolution_i"])
                self.resolution_j.set(data["resolution_j"])
                
                self.surface = BSplineSurface(self.m.get(), self.n.get())
                self.surface.cm = np.array(data["pontos_controle"])

                for i, value in enumerate(data["rotacao"]):
                    self.rotacao_vars[i].set(value)
                for i, value in enumerate(data["translacao"]):
                    self.translacao_vars[i].set(value)
                self.escala.set(data["escala"])

                # Cores
                for i, value in enumerate(data["cor_aresta_visivel"]):
                    self.cor_aresta_visivel[i].set(value)
                for i, value in enumerate(data["cor_aresta_invisivel"]):
                    self.cor_aresta_invisivel[i].set(value)
                for i, value in enumerate(data["background_color"]):
                    self.background_color[i].set(value)

                self.mostrar_pontos.set(data["mostrar_pontos"])

                self.window_coords = np.array(data["window_coords"])
                self.window_min_x.set(self.window_coords[0, 0])
                self.window_max_x.set(self.window_coords[0, 1])
                self.window_min_y.set(self.window_coords[1, 0])
                self.window_max_y.set(self.window_coords[1, 1])

                self.viewport_coords = np.array(data["viewport_coords"])
                self.viewport_min_u.set(self.viewport_coords[0, 0])
                self.viewport_max_u.set(self.viewport_coords[0, 1])
                self.viewport_min_v.set(self.viewport_coords[1, 0])
                self.viewport_max_v.set(self.viewport_coords[1, 1])

                self.vrp_x.set(data["vrp"][0])
                self.vrp_y.set(data["vrp"][1])
                self.vrp_z.set(data["vrp"][2])
                self.p_x.set(data["p"][0])
                self.p_y.set(data["p"][1])
                self.p_z.set(data["p"][2])

                self.intensidade_ambiente.set(data["intensidade_ambiente"])
                self.intensidade_luz.set(data["intensidade_luz"])
                for i, value in enumerate(data["vetor_l"]):
                    self.vetor_l[i].set(value)
                self.ka.set(data["ka"])
                self.kd.set(data["kd"])
                self.ks.set(data["ks"])
                self.n_shininess.set(data["n_shininess"])
                self.sombreamento.set(data["sombreamento"])

                self.update_transform()
                self.atualizar_malha = True
                self.render()
                print("Malha carregada com sucesso!")

if __name__ == "__main__":
    root = tk.Tk()
    app = BSplineEditor(root)
    root.mainloop()