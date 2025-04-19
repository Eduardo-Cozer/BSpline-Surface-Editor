# Editor de Superfícies B-Spline

## Visão Geral

O **Editor de Superfícies B-Spline** é uma aplicação em Python que permite aos usuários criar, visualizar e manipular superfícies B-Spline 3D de forma interativa. Ele oferece uma interface gráfica (GUI) construída com `tkinter`, permitindo ajustar parâmetros da superfície, aplicar transformações (rotação, translação, escala), configurar iluminação e modelos de sombreamento, além de salvar e carregar configurações da superfície. A aplicação suporta múltiplas técnicas de sombreamento (Wireframe, Constante, Gouraud e Phong) para renderizar a superfície, sendo uma ferramenta útil para entusiastas de computação gráfica, estudantes e desenvolvedores.

O projeto utiliza `numpy` para cálculos numéricos e depende de uma classe externa `BSplineSurface` (`bspline_surface.py`) para lidar com a interpolação de superfícies B-Spline.

---

## Funcionalidades

- **Interface Gráfica Interativa**: Construída com `tkinter`, permite ajustar dimensões da superfície, transformações, cores, iluminação e mais.
- **Geração de Superfícies B-Spline**: Cria superfícies 3D B-Spline com base em pontos de controle e resoluções definidas pelo usuário.
- **Transformações**: Suporta rotação, translação e escala da superfície.
- **Projeção e Renderização**: Implementa uma projeção axonométrica isométrica para mapear pontos 3D para um canvas 2D, com transformações de janela e viewport.
- **Modelos de Sombreamento**: Suporta quatro modos de renderização:
  - **Wireframe**: Desenha as arestas da superfície com coloração baseada em visibilidade.
  - **Sombreamento Constante**: Aplica um único valor de iluminação por face.
  - **Sombreamento Gouraud**: Interpola a iluminação nos vértices e ao longo das faces.
  - **Sombreamento Phong**: Interpola normais ao longo das faces para efeitos de iluminação mais suaves.
- **Iluminação**: Implementa o modelo de iluminação com componentes ambiente, difusa e especular.
- **Entrada/Saída de Arquivos**: Permite salvar e carregar configurações da superfície em formato JSON.
- **Edição de Pontos de Controle**: Oferece uma interface para editar manualmente as coordenadas dos pontos de controle.

---

## Requisitos

Para executar o Editor de Superfícies B-Spline, você precisa do seguinte:

- **Python 3.x**: O projeto é escrito em Python.
- **tkinter**: Para a interface gráfica (geralmente incluído na instalação do Python).
- **numpy**: Para cálculos numéricos.
- **bspline_surface.py**: Um módulo personalizado que fornece a classe `BSplineSurface` para interpolação de superfícies B-Spline. (seguindo https://paulbourke.net/geometry/spline/)

Instale o `numpy` usando o pip, caso ainda não o tenha:

```bash
pip install numpy
```

---

## Estrutura do Projeto

O projeto consiste em um único arquivo principal:

- `main.py`: O arquivo principal contendo a classe `BSplineEditor`, que gerencia a interface gráfica, geração da superfície, transformações, renderização e entrada/saída de arquivos.

Além disso, o projeto assume a existência de:

- `bspline_surface.py`: Um módulo externo que fornece a classe `BSplineSurface` para interpolação de superfícies B-Spline.

---

## Detalhamento do Código

O arquivo `main.py` contém a classe `BSplineEditor`, que é o núcleo da aplicação. Abaixo está uma explicação detalhada de seus componentes:

### 1. **Inicialização (**`__init__`**)**

- **Propósito**: Configura a interface gráfica, inicializa a superfície B-Spline e define valores padrão para os parâmetros.
- **Atributos Principais**:
  - `self.canvas`: Um `tkinter.Canvas` para renderizar a superfície.
  - `self.WIDTH` e `self.HEIGHT`: Dimensões do canvas (800x600 pixels).
  - `self.m` e `self.n`: Número de pontos de controle nas direções i e j (padrão: 4x4).
  - `self.resolution_i` e `self.resolution_j`: Resolução para interpolação da superfície (padrão: 10x10).
  - `self.vrp` e `self.p`: Ponto de Referência de Visão (VRP) e ponto focal (P) da câmera (padrão: VRP em (50, 50, 50), P em (0, 0, 0)).
  - `self.vup`: Vetor de visão "para cima" (padrão: (0, 1, 0)).
  - Parâmetros de transformação: `self.rotacao_value`, `self.translacao_value`, `self.escala_value`.
  - Configurações de cor: `self.cor_aresta_visivel_value`, `self.cor_aresta_invisivel_value`, `self.background_color_value`.
  - Parâmetros de iluminação: `self.intensidade_ambiente_value`, `self.intensidade_luz_value`, `self.vetor_l_value`, `self.ka_value`, `self.kd_value`, `self.ks_value`, `self.n_shininess_value`.
  - Modo de sombreamento: `self.sombreamento` (padrão: "wireframe").
  - Buffers: `self.z_buffer` para teste de profundidade, `self.color_buffer` para armazenar cores dos pixels.

### 2. **Configuração da Interface (**`setup_controls`**)**

- **Propósito**: Cria o painel de controle à direita da janela, com controles deslizantes, campos de entrada e botões para ajustar os parâmetros.
- **Componentes**:
  - **Dimensões**: Ajusta `m`, `n`, `resolution_i` e `resolution_j`.
  - **Transformações**: Controles deslizantes para rotação (x, y, z), translação (x, y, z) e escala.
  - **Cores**: Controles deslizantes para cor das arestas visíveis, arestas invisíveis e cor de fundo.
  - **VRP e P**: Campos de entrada para definir o Ponto de Referência de Visão e o ponto focal.
  - **Opções**: Caixa de seleção para mostrar pontos de controle, botão para editar pontos de controle.
  - **Coordenadas**: Campos de entrada para ajustar as coordenadas da janela e do viewport.
  - **Iluminação**: Controles deslizantes para intensidade ambiente, intensidade da luz, direção da luz (`vetor_l`) e coeficientes do modelo de Phong (`Ka`, `Kd`, `Ks`, `n`).
  - **Sombreamento**: Botões de rádio para selecionar o modo de sombreamento (Wireframe, Constante, Gouraud ou Phong).
  - **Entrada/Saída de Arquivos**: Botões para salvar e carregar configurações da superfície.

### 3. **Atualização de Parâmetros (**`update_transform`**)**

- **Propósito**: Atualiza o estado interno quando os controles da interface são modificados.
- **Funcionalidade**:
  - Atualiza valores de transformação (rotação, translação, escala).
  - Atualiza VRP, P, cores, parâmetros de iluminação e coordenadas da janela/viewport.
  - Reinstancia a superfície B-Spline se `m` ou `n` mudar.
  - Marca a superfície para re-renderização (`self.atualizar_malha = True`).

### 4. **Métodos de Utilidade**

Esses métodos fornecem operações vetoriais básicas e cálculos geométricos:

- `produto_escalar(v1, v2)`: Calcula o produto escalar entre dois vetores.
- `produto_vetorial(v1, v2)`: Calcula o produto vetorial entre dois vetores.
- `normalizar(v)`: Normaliza um vetor (retorna vetor zero se a norma for zero).
- `calcular_centroide(face)`: Calcula o centroide de uma face.
- `calcular_distancia(vrp, centroide)`: Calcula a distância Euclidiana entre dois pontos.
- `vis_normal(face, vrp)`: Determina se uma face é visível a partir do VRP (usando eliminação de faces traseiras).
- `calcular_normal(face)`: Calcula o vetor normal de uma face (normalizado).

### 5. **Geração da Superfície B-Spline (**`calcular_bspline`**)**

- **Propósito**: Gera a superfície B-Spline 3D interpolando os pontos de controle.
- **Funcionalidade**:
  - Chama `self.surface.interpolate()` para calcular os pontos da superfície.
  - Retorna três arrays (`X`, `Y`, `Z`) representando as coordenadas da superfície.

### 6. **Transformações**

Esses métodos aplicam transformações aos pontos da superfície:

- `matriz_rotacao(angulos)`: Cria uma matriz de rotação 4x4 para rotações em torno dos eixos x, y e z.
- `matriz_translacao(translacao)`: Cria uma matriz de translação 4x4.
- `matriz_escala(escala)`: Cria uma matriz de escala 4x4.
- `matriz_sru_to_src(vrp, p, vup)`: Cria uma matriz 4x4 para transformar de coordenadas do mundo (SRU) para coordenadas da câmera (SRC).
- `aplicar_transformacoes(pontos)`: Aplica escala, rotação e translação aos pontos da superfície usando coordenadas homogêneas.

### 7. **Projeção e Mapeamento para Viewport (**`aplicar_projecao_viewport_isometrica`**)**

- **Propósito**: Projeta pontos 3D para coordenadas 2D na tela.
- **Funcionalidade**:
  - Transforma os pontos para coordenadas da câmera usando `matriz_sru_to_src`.
  - Aplica uma projeção axonométrica isométrica.
  - Mapeia os pontos das coordenadas da janela para as coordenadas do viewport usando uma matriz de escala e translação 2D.
  - Retorna os pontos transformados com coordenadas 2D (x, y) e profundidade (z).

### 8. **Recorte (**`recorte_2d_viewport`**)**

- **Propósito**: Recorta faces para os limites do viewport usando o algoritmo de Sutherland-Hodgman.
- **Funcionalidade**:
  - Recorta faces contra os limites esquerdo, direito, inferior e superior do viewport.
  - Retorna a face recortada (coordenadas 2D) e os índices dos vértices originais.

### 9. **Pipeline de Renderização (**`render`**)**

- **Propósito**: Orquestra o processo de renderização.
- **Etapas**:
   1. Limpa o canvas e inicializa o z-buffer e o buffer de cores.
   2. Gera a superfície B-Spline (`calcular_bspline`).
   3. Aplica transformações (`aplicar_transformacoes`).
   4. Projeta os pontos para 2D (`aplicar_projecao_viewport_isometrica`).
   5. Constrói faces (quadriláteros) a partir dos pontos da superfície.
   6. Recorta as faces para o viewport (`recorte_2d_viewport`).
   7. Ordena as faces por distância do VRP (algoritmo do pintor).
   8. Filtra as faces para garantir que o número de vértices 2D corresponda à face 3D.
   9. Renderiza as faces usando o método de sombreamento selecionado:
      - `render_wireframe`
      - `render_constante`
      - `render_gouraud`
      - `render_phong`
  10. Opcionalmente desenha arestas no modo wireframe com coloração baseada em visibilidade.
  11. Opcionalmente desenha pontos de controle como pontos amarelos.

### 10. **Métodos de Sombreamento**

Esses métodos implementam diferentes técnicas de renderização:

- `render_wireframe(faces_2d, faces_3d, z_values)`:
  - Usa um algoritmo de scanline para desenhar as faces.
  - Preenche as faces com uma cor de fundo (`#1A1A1A`).
  - Atualiza o z-buffer para teste de profundidade.
- `render_constante(faces_2d, faces_3d, z_values)`:
  - Calcula um único valor de iluminação por face usando o modelo de iluminação de Phong.
  - Aplica iluminação ambiente, difusa e especular com base na normal e no centroide da face.
  - Preenche a face com uma cor em escala de cinza baseada na iluminação.
- `render_gouraud(faces_2d, faces_3d, z_values)`:
  - Calcula a iluminação em cada vértice usando o modelo de iluminação de Phong.
  - Interpola a iluminação ao longo da face durante a renderização por scanline.
  - Produz transições de iluminação mais suaves em comparação com o sombreamento constante.
- `render_phong(faces_2d, faces_3d, z_values)`:
  - Interpola os vetores normais ao longo da face.
  - Calcula a iluminação em cada pixel usando a normal interpolada.
  - Produz os efeitos de iluminação mais suaves, mas é computacionalmente mais caro.

### 11. **Edição de Pontos de Controle (**`editar_pontos_controle` **e** `save_control_points`**)**

- **Propósito**: Permite aos usuários editar as coordenadas dos pontos de controle.
- **Funcionalidade**:
  - Abre uma nova janela com uma lista rolável de pontos de controle.
  - As coordenadas (x, y, z) de cada ponto de controle podem ser editadas em campos de texto.
  - Salva as coordenadas atualizadas e marca a superfície para re-renderização.

### 12. **Entrada/Saída de Arquivos (**`salvar_malha` **e** `abrir_malha`**)**

- **Propósito**: Salva e carrega configurações da superfície em arquivos JSON.
- **Funcionalidade**:
  - **Salvar**: Serializa todos os parâmetros (pontos de controle, transformações, cores, iluminação, etc.) em um arquivo JSON.
  - **Carregar**: Lê um arquivo JSON, atualiza os parâmetros e dispara uma re-renderização.

---

## Como Usar

1. **Executar a Aplicação**: Certifique-se de ter as dependências instaladas e o módulo `bspline_surface.py` disponível. Em seguida, execute:

   ```bash
   python main.py
   ```
   ou

   ```bash
   python3 main.py
   ```

2. **Interagir com a Interface**:

   - Ajuste o número de pontos de controle (`M`, `N`) e as resoluções (`Resolução I`, `Resolução J`).
   - Use os controles deslizantes para aplicar rotações, translações e escala.
   - Defina o VRP e o ponto focal (P) para mudar a posição da câmera.
   - Configure os parâmetros de iluminação (ambiente, difusa, especular) e a direção da luz.
   - Selecione um modo de sombreamento (Wireframe, Constante, Gouraud ou Phong).
   - Edite os pontos de controle usando o botão "Editar Pontos de Controle".
   - Salve ou carregue configurações da superfície usando os botões "Salvar Malha" e "Abrir Malha".
   - Re-renderize manualmente (desempenho) usando o botão "Atualizar Malha".

---

## Limitações

- **Desempenho**: O pipeline de renderização é baseado em software (sem aceleração por GPU), o que pode ser lento para superfícies de alta resolução ou modelos de sombreamento complexos (Recomendado fortemente utilizar sistemas GNU/Linux).
- **Artefatos de Sombreamento**: O algoritmo de scanline pode produzir artefatos nas bordas das faces, especialmente com sombreamento Gouraud ou Phong.

---

## Contribuidores

`Projeto Final do ano letivo de 2024 da matéria de Computação Gráfica ministrada pelo professor Adair Santa Catarina e desenvolvida pelos alunos Eduardo Cozer, Geandro Silva e Vinicius Messaggi de Lima Ribeiro na Instituição de ensino superior UNIOESTE (Universidade Estadual do Oeste do Paraná)`

<table>
  <tr>
    <td align="center"><a href="https://github.com/Eduardo-Cozer"><img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/129805691?v=4" width="100px;" alt=""/><br /><sub><b>Eduardo Cozer</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/GeandroRdS"><img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/140825373?v=4" width="100px;" alt=""/><br /><sub><b>Geandro Silva</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/Vmessaggi"><img style="border-radius: 50%;" src="https://avatars.githubusercontent.com/u/109189195?v=4" width="100px;" alt=""/><br /><sub><b>Vinicius Messaggi de Lima Ribeiro</b></sub></a><br /></td>
  </tr>
</table>