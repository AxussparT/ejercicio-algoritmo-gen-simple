# Algoritmo Genético Configurable para Optimización Univariada $f(x)$

Aplicación modular en Python para la optimización de funciones univariadas $f(x)$ que implementa **todos los métodos evolutivos** documentados en el archivo `05_hiperparametros`.

---

## 📁 Estructura del Proyecto

```text
alogoritmo genetico simple/
│
├── main.py                          # Punto de entrada de la aplicación
├── requirements.txt                 # Dependencias (numpy, matplotlib)
├── README.md                        # Documentación técnica y guía de usuario
│
├── logica/                          # Módulo de lógica y algoritmos genéticos
│   ├── __init__.py
│   ├── individual.py                # Representación de soluciones, fenotipo x y fitness
│   ├── population.py                # Manejo de la población y escalamiento de aptitud
│   ├── evaluator.py                 # Evaluador matemático seguro con AST (sin eval inseguro)
│   ├── selection.py                 # Operadores de selección (Ruleta, Rankings, Torneo, SUS)
│   ├── crossover.py                 # Operadores de cruce (Uniforme, Aritmético, Plano, BLX-α, PMX, OX, CX)
│   ├── mutation.py                  # Operadores de mutación (Uniforme, No uniforme, Intercambio)
│   ├── replacement.py               # Estrategias de sustitución (Elitismo, Steady-state, Crowding)
│   └── ga_engine.py                 # Ciclo evolutivo asíncrono con control de parada
│
├── benchmarks/                      # Catálogo de funciones de prueba
│   ├── __init__.py
│   └── test_functions.py            # Esfera, Rastrigin, Ackley, Rosenbrock, Michalewicz, etc.
│
├── almacenamiento/                  # Persistencia y registro de ejecuciones
│   ├── __init__.py
│   ├── experiment_logger.py         # Guardado automático en JSON, reportes TXT y exportación CSV
│   └── registros/                   # Directorio donde se almacenan las ejecuciones
│
├── ui/                              # Interfaz gráfica moderna y modular (Tkinter + Matplotlib)
│   ├── __init__.py
│   ├── styles.py                    # Paleta de colores sobria, moderna y estilos ttk
│   ├── main_window.py               # Ventana principal multihilo
│   └── components/                  # Paneles desacoplados
│       ├── __init__.py
│       ├── function_panel.py        # Configuración de función y límites [a, b]
│       ├── hyperparameters_panel.py # Menús dinámicos adaptativos según método
│       ├── plot_panel.py            # Gráficas integradas de paisaje y convergencia
│       ├── metrics_panel.py         # Tarjeta de métricas en tiempo real
│       └── history_dialog.py        # Modal de historial y recuperación de parámetros
│
└── tests/                           # Suite de pruebas automatizadas
    ├── __init__.py
    ├── test_operators.py            # Pruebas unitarias de todos los operadores evolutivos
    └── test_ga.py                   # Pruebas de integración y convergencia
```

---

## 🧬 Métodos Evolutivos Implementados (`05_hiperparametros`)

### 1. Selección y Sustitución
* **Ruleta Proporcional**: Probabilidad proporcional a la aptitud ($p_i = f_i / \sum f_j$).
* **Ranking Lineal**: Ordena del mejor al peor asignando probabilidades decrecientes lineales basadas en $a_{max} \in [1.0, 2.0]$.
* **Ranking No Lineal**: Decrecimiento geométrico basado en el factor $q \in (0, 1)$ ($w_r = q(1-q)^{rank-1}$).
* **Torneo**: Competencia entre $k$ candidatos al azar; el de mayor aptitud gana.
* **Muestreo Estocástico Universal (SUS)**: $m$ punteros equidistantes sobre la distribución acumulada con sorteo aleatorio único en $[0, 1/m)$.
* **Sustitución Steady-State**: Reemplaza en cada generación únicamente a los $n$ peores individuos por los nuevos descendientes.
* **Factor de Crowding**: Para cada nuevo descendiente, toma una muestra aleatoria de tamaño $CF$ y sustituye al individuo más similar en el espacio fenotípico.
* **Reemplazo Generacional con Elitismo**: Preserva intactos los $e$ mejores individuos históricos.

### 2. Cruce / Combinación
* **Cruce Uniforme**: Máscara binaria que decide de cuál de los dos padres hereda cada gen.
* **Cruce Aritmético**: Combinación convexa mediante media ponderada ($H_1 = aP_1 + (1-a)P_2$).
* **Cruce Plano**: Sorteo uniforme entre los valores de los padres ($h \sim U(\min(p_1, p_2), \max(p_1, p_2))$).
* **Cruce BLX-$\alpha$**: Expande el intervalo de los padres en una proporción $\alpha$ de su distancia ($I = |p_1 - p_2|$).
* **PMX (Partially Mapped Crossover)**: Preserva asignaciones y mapea correspondencias.
* **OX (Order Crossover)**: Preserva el orden relativo de secuencias.
* **CX (Cycle Crossover)**: Identifica y conserva ciclos posicionales alternados.

### 3. Mutación
* **Mutación Uniforme**: Sustituye el gen por un sorteo uniforme en el dominio permitido $[LB, UB]$.
* **Mutación No Uniforme**: Perturbación decreciente con el avance de las generaciones ($\Delta = y [1 - r^{(1 - t/T)^b}]$), permitiendo exploración global al inicio y afinamiento fino al final.
* **Mutación por Intercambio (Swap)**: Intercambio de posiciones o reflexión respecto al centro del intervalo.

---

## 🚀 Cómo Ejecutar

1. Abre una terminal en la carpeta del proyecto:
   ```powershell
   cd "C:\Users\Admin\Desktop\alogoritmo genetico simple"
   ```
2. Ejecuta la aplicación:
   ```powershell
   python main.py
   ```
3. Ejecutar las pruebas unitarias:
   ```powershell
   python tests/test_operators.py
   python tests/test_ga.py
   ```
