# Traduccion-Dirigida-Por-SIntaxis-
# ETDS - Esquema de Traducción Dirigida por la Sintaxis
---
## **Descripcion**
Este proyecto implementa un Esquema de Traducción Dirigida por la Sintaxis (ETDS) completo para una gramática independiente del contexto que maneja expresiones aritméticas con las cuatro operaciones básicas (suma, resta, multiplicación y división).
El sistema realiza:

- Análisis léxico - Tokenización de la entrada
- Análisis sintáctico - Construcción del árbol de derivación
- Análisis semántico - Validación de tipos y declaraciones
- Generación de AST decorado - Árbol con atributos sintetizados
- Tabla de símbolos - Gestión de variables con alcances
- Codigo intermedio - Generación de código de 3 direcciones
- Cálculo de conjuntos - PRIMEROS, SIGUIENTES y PREDICCIÓN

---
## **Objetivos**

1. Diseño de la gramática
2. Definir atributos
3. Calcular los conjuntos: F,S,P,
4. Generar el AST decorado(imprimirlo)
5. Generar la tabla de símbolos (definir las estructuras)
6. Generar la gramática de atributos
7. Generar la ETDS.

---
## 1. **Diseño de la gramatica**

- Gramática Libre de Contexto
```
S  → D S | E
D  → int id ; | float id ;
E  → E + T | E - T | T
T  → T * F | T / F | F
F  → ( E ) | num | id
```
**Características:**

- Símbolos no terminales: S (Programa), D (Declaración), E (Expresión), T (Término), F (Factor)
- Símbolos terminales: int, float, id, num, +, -, *, /, (, ), ;
- Precedencia de operadores: Paréntesis > Multiplicación/División > Suma/Resta
- Asociatividad: Izquierda para todos los operadores

---

## 2. **Definición de Atributos**
**Atributos Sintetizados**

Los atributos sintetizados se calculan de abajo hacia arriba en el árbol:  s

| Símbolo | Atributo | Tipo     | Descripción |
|----------|-----------|----------|--------------|
| E, T, F  | `val`     | numérico | Valor calculado de la expresión |
| E, T, F  | `tipo`    | string   | Tipo de dato (por ejemplo `int` o `float`) |
| E, T, F  | `lugar`   | string   | Variable temporal que contiene el resultado |
| E, T, F  | `codigo`  | string   | Código intermedio generado |
| D        | `nombre`  | string   | Nombre de la variable declarada |
| D        | `tipo_var`| string   | Tipo de la variable |

### Atributo hederados 
Los atributos heredados se propagan de arriba hacia abajo:

| Símbolo | Atributo        | Descripción                                 |
|--------:|-----------------|---------------------------------------------|
| `tabla` | `E, T, F`       | Referencia a la tabla de símbolos activa.   |
| `linea` | `Número`        | Número de línea en el código fuente.        |

### Ejemplo de Decoración
Para la expresión x = 5 + 3 * 2:

```
Asignacion [tipo: int, val: 11]
├── x [tipo: int]
└── + [tipo: int, val: 11, lugar: t2]
    ├── 5 [tipo: int, val: 5]
    └── * [tipo: int, val: 6, lugar: t1]
        ├── 3 [tipo: int, val: 3]
        └── 2 [tipo: int, val: 2]
```

### Atributos decorados:

- tipo: Resultado de la coerción de tipos
- val: Valor calculado si es constante (5 + 6 = 11)
- lugar: Variable temporal asignada (t1, t2)

---

## **3. Cálculo de Conjuntos**

### PRIMEROS (FIRST)
El conjunto PRIMEROS indica qué terminales pueden aparecer al inicio de una derivación:

```
PRIMEROS(S)  = {int, float, (, num, id}
PRIMEROS(D)  = {int, float}
PRIMEROS(E)  = {(, num, id}
PRIMEROS(T)  = {(, num, id}
PRIMEROS(F)  = {(, num, id}

```
¿Cómo se calculan?

1. Si X es terminal: PRIMEROS(X) = {X}
2. Si X → ε: agregar ε a PRIMEROS(X)
3. Si X → Y₁Y₂...Yₖ: agregar PRIMEROS(Y₁) - {ε}, y si Y₁ deriva ε, continuar con Y₂, etc.

### SIGUIENTES (FOLLOW)

El conjunto SIGUIENTES indica qué terminales pueden aparecer después de un símbolo:
```
SIGUIENTES(S)  = {$}
SIGUIENTES(D)  = {int, float, (, num, id}
SIGUIENTES(E)  = {$, ), +, -, ;}
SIGUIENTES(T)  = {$, ), +, -, *, /, ;}
SIGUIENTES(F)  = {$, ), +, -, *, /, ;}
```
¿Cómo se calculan?

1. SIGUIENTES(S) = {$} (símbolo inicial)
2. Si A → αBβ: agregar PRIMEROS(β) - {ε} a SIGUIENTES(B)
3.Si A → αB o β deriva ε: agregar SIGUIENTES(A) a SIGUIENTES(B)

### PREDICCIÓN
El conjunto PREDICCIÓN determina qué producción usar según el token actual:
```
PRED(S → D S)         = {int, float}
PRED(S → E)           = {(, num, id}
PRED(D → int id ;)    = {int}
PRED(D → float id ;)  = {float}
PRED(E → E + T)       = {(, num, id}
PRED(E → T)           = {(, num, id}
PRED(T → T * F)       = {(, num, id}
PRED(T → F)           = {(, num, id}
PRED(F → ( E ))       = {(}
PRED(F → num)         = {num}
PRED(F → id)          = {id}
```
Fórmula:
```
PRED(A → α) = PRIMEROS(α) si ε ∉ PRIMEROS(α)
PRED(A → α) = (PRIMEROS(α) - {ε}) ∪ SIGUIENTES(A) si ε ∈ PRIMEROS(α)
```
Verificación LL(1): La gramática es LL(1) si para cada par de producciones A → α | β:

PRED(A → α) ∩ PRED(A → β) = ∅
---
## **4. AST Decorado**
Estructura del Árbol
El AST (Abstract Syntax Tree) decorado contiene en cada nodo:

```py
class NodoAST:
    etiqueta    # Operador, identificador o valor
    hijos       # Lista de sub-nodos
    tipo        # Tipo de dato (int, float, void)
    val         # Valor calculado
    lugar       # Variable temporal
    codigo      # Código intermedio
    linea       # Número de línea
```
### **Ejemplo Completo**

Entrada:
```
int x;
float y;
x = 5 + 3 * 2;
y = x / 2.0;
```
AST Decorado Generado:

<img width="643" height="392" alt="image" src="https://github.com/user-attachments/assets/a6b61112-2d74-42d1-91c9-ff3f53effd83" />


Interpretación del AST
Cada nodo muestra:

Etiqueta: El operador o valor (ej: +, 5, x)
[tipo: ...]: El tipo de dato resultante después de la operación
[val: ...]: El valor calculado (solo si es evaluable en tiempo de compilación)

Jerarquía visual:

└── indica el último hijo de un nodo
├── indica un hijo intermedio
│ marca la continuación de una rama

**Ejemplo de lectura:**
```
+ [tipo: int, val: 11]
├── 5 [tipo: int, val: 5]
└── * [tipo: int, val: 6]
    ├── 3 [tipo: int, val: 3]
    └── 2 [tipo: int, val: 2]

```
---

## **5. Tabla de Símbolos**

Estructura de datos
```
class Simbolo:
    nombre     # Identificador de la variable
    tipo       # Tipo de dato (int, float)
    alcance    # Nivel de anidamiento
    linea      # Línea de declaración
    valor      # Valor asignado (opcional)
    usado      # Si ha sido referenciado
```
**Ejemplo de Tabla**

Para el código anterior:

<img width="644" height="155" alt="image" src="https://github.com/user-attachments/assets/fb7089a5-f11a-4d46-83be-399f15cd1258" />

**Interpretación de Columnas**

| Columna  | Descripción                           | Ejemplo               |
|-----------|---------------------------------------|------------------------|
| **Nombre** | Identificador de la variable          | `x`, `y`, `resultado`  |
| **Tipo**   | Tipo de dato declarado                | `int`, `float`         |
| **Alcance** | Nivel de anidamiento (`0 = global`)  | `0`, `1`, `2`          |
| **Línea**  | Línea donde se declaró                | `1`, `2`, `3`          |
| **Valor**  | Último valor asignado                 | `11`, `5.5`, `None`    |
| **Usado**  | Si la variable fue utilizada          | `Sí`, `No`             |

Funcionalidades
1. Detección de redeclaraciones:
```
int x;
   int x;  // ❌ Error: Variable 'x' ya declarada en línea 1
```
2. Validación de uso antes de declaración:
```
y = 5;  // ❌ Error: Variable 'y' no declarada
   int y;
```
3. Variables no usadas (warning):
```
   int z;  // ⚠️ Warning: Variable 'z' declarada pero no usada
```
---

## **6. Gramática de Atributos**
**Reglas Semánticas**
Expresión con Suma
```
E → E₁ + T
{
    E.tipo = coercion(E₁.tipo, T.tipo)
    E.val = E₁.val + T.val
    temp = nuevo_temporal()
    E.lugar = temp
    E.codigo = E₁.codigo || T.codigo || 
               temp || " = " || E₁.lugar || " + " || T.lugar
}
```
**Explicación:**

1. Calcula el tipo resultante aplicando coerción (int + float = float)
2. Si ambos son constantes, evalúa el valor en tiempo de compilación
3. Genera una variable temporal para almacenar el resultado
4. Concatena el código de los operandos más la instrucción de suma

Expresión con Multiplicación

```py
T → T₁ * F
{
    T.tipo = coercion(T₁.tipo, F.tipo)
    T.val = T₁.val * F.val
    temp = nuevo_temporal()
    T.lugar = temp
    T.codigo = T₁.codigo || F.codigo || 
               temp || " = " || T₁.lugar || " * " || F.lugar
}

```
**Factor: Número**
```py
F → num
{
    F.tipo = tipo_de(num.lexema)    // "3.14" → float, "5" → int
    F.val = convertir(num.lexema)
    F.lugar = num.lexema
    F.codigo = ""
}

```
**Factor: Identificador**
```py
F → id
{
    if not existe(id.lexema) then
        error("Variable no declarada")
    F.tipo = buscar_tipo(id.lexema)
    F.val = buscar_valor(id.lexema)
    F.lugar = id.lexema
    F.codigo = ""
    marcar_usado(id.lexema)
}
```
**Función de Coerción**
```py
def coercion(tipo1, tipo2):
    if tipo1 == 'float' or tipo2 == 'float':
        return 'float'
    return 'int'
```
**Ejemplos:**

- int + int → int
- int + float → float
- float + float → float

---

## **7. ETDS Completo**
Esquema de Traducción
```
S → D { insertar_en_tabla(D.nombre, D.tipo_var) } S

S → E { evaluar_y_mostrar(E) }

D → tipo id ; 
    { 
        D.tipo_var = tipo.lexema
        D.nombre = id.lexema
        verificar_no_redeclarada(id.lexema)
        generar_codigo("declare " || id.lexema || " : " || tipo.lexema)
    }

E → E₁ + T 
    { 
        E.tipo = coercion(E₁.tipo, T.tipo)
        E.val = evaluar(E₁.val + T.val)
        temp = nuevo_temporal()
        E.lugar = temp
        generar_codigo(temp || " = " || E₁.lugar || " + " || T.lugar)
    }

F → id 
    { 
        verificar_declarada(id.lexema)
        F.tipo = obtener_tipo(id.lexema)
        F.val = obtener_valor(id.lexema)
        F.lugar = id.lexema
        marcar_usada(id.lexema)
    }
```
---
## **8. Codigo Intermedio**
Formato de 3 Direcciones
El código intermedio generado sigue el formato:
```
destino = operando1 op operando2

```
Ejemplo Completo
Entrada:
```
int x;
int y;
x = 5 + 3 * 2;
y = x - 1;
```
Código Intermedio Generado:


<img width="654" height="191" alt="image" src="https://github.com/user-attachments/assets/0a4edeef-00d9-49cc-994d-2dd1aacd7712" />


**Interpretación**


| Instrucción       | Significado                                         |
|--------------------|----------------------------------------------------|
| `declare x : int`  | Declarar variable `x` de tipo `int`.               |
| `t1 = 3 * 2`       | Calcular `3 * 2` y guardar en el temporal `t1`.    |
| `t2 = 5 + t1`      | Sumar `5 + t1` y guardar en el temporal `t2`.      |
| `x = t2`           | Asignar el valor de `t2` a la variable `x`.        |
| `t3 = x - 1`       | Restar `x - 1` y guardar en el temporal `t3`.      |
| `y = t3`           | Asignar el valor de `t3` a la variable `y`.        |

Características:

- Una operación por línea
- Variables temporales: t1, t2, t3, ...
- Respeta el orden de evaluación
- Facilita la optimización posterior

# USO
1. . Calcular conjuntos FIRST, FOLLOW, PREDICT
```
python calcular_conjuntos.py gramatica.txt
```
2. Analizar código (modo interactivo)
```
python analizador_completo.py gramatica.txt

```
Luego escribe tu código y presiona Enter dos veces:
```
int x;
x = 5 + 3 * 2;
```

# EJEMPLO
entrada 
```
int x;
int y;
x = 5 + 3 * 2;
y = x - 1;
```
SALIDA COMPLETA
---

<img width="665" height="419" alt="image" src="https://github.com/user-attachments/assets/4c850018-2274-456b-b7f9-cec3b4ce114a" />

---

<img width="656" height="548" alt="image" src="https://github.com/user-attachments/assets/d5aee183-8e4f-4dc2-803b-9ba0b12c761c" />

---

<img width="681" height="307" alt="image" src="https://github.com/user-attachments/assets/ce4e7c77-2e8d-4f44-ab44-9beb16676033" />

---


