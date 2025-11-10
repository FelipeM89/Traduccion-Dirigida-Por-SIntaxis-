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
# 1. **Diseño de la gramatica**
´´´ 
S  → D S | E
D  → int id ; | float id ;
E  → E + T | E - T | T
T  → T * F | T / F | F
F  → ( E ) | num | id
´´´
