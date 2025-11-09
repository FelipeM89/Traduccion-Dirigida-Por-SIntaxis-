#!/usr/bin/env python3
# calcular_conjuntos.py
"""
Cálculo de conjuntos PRIMEROS, SIGUIENTES y PREDICCIÓN
para una gramática independiente del contexto
"""

import sys
from collections import defaultdict

def leer_gramatica(archivo):
    """Lee la gramática desde un archivo"""
    gramatica = defaultdict(list)
    simbolo_inicial = None
    
    with open(archivo, 'r', encoding='utf-8') as f:
        for linea in f:
            linea = linea.strip()
            
            # Ignorar líneas vacías y comentarios
            if not linea or linea.startswith('#'):
                continue
            
            # Parsear regla: A -> alpha | beta
            if '->' not in linea:
                continue
            
            izquierda, derecha = linea.split('->', 1)
            izquierda = izquierda.strip()
            
            # El primer no terminal es el símbolo inicial
            if simbolo_inicial is None:
                simbolo_inicial = izquierda
            
            # Procesar alternativas separadas por |
            alternativas = derecha.split('|')
            for alt in alternativas:
                produccion = alt.strip().split()
                # Manejar epsilon (ε o e)
                if not produccion or produccion == ['ε'] or produccion == ['e']:
                    produccion = ['ε']
                gramatica[izquierda].append(produccion)
    
    return gramatica, simbolo_inicial


def obtener_terminales_no_terminales(gramatica):
    """Identifica terminales y no terminales de la gramática"""
    no_terminales = set(gramatica.keys())
    terminales = set()
    
    for producciones in gramatica.values():
        for produccion in producciones:
            for simbolo in produccion:
                if simbolo != 'ε' and simbolo not in no_terminales:
                    terminales.add(simbolo)
    
    return terminales, no_terminales


def calcular_primeros(gramatica):
    """Calcula el conjunto PRIMEROS para cada símbolo"""
    primeros = defaultdict(set)
    terminales, no_terminales = obtener_terminales_no_terminales(gramatica)
    
    # Inicialización: terminales producen a sí mismos
    for terminal in terminales:
        primeros[terminal].add(terminal)
    
    # Algoritmo iterativo de punto fijo
    cambio = True
    while cambio:
        cambio = False
        
        for nt in gramatica:
            for produccion in gramatica[nt]:
                # Para cada símbolo en la producción
                puede_ser_vacio = True
                
                for simbolo in produccion:
                    # Terminal: agregar y terminar
                    if simbolo not in no_terminales:
                        antes = len(primeros[nt])
                        primeros[nt].add(simbolo)
                        if len(primeros[nt]) > antes:
                            cambio = True
                        puede_ser_vacio = False
                        break
                    
                    # No terminal: agregar PRIMEROS(símbolo) - {ε}
                    antes = len(primeros[nt])
                    primeros[nt] |= (primeros[simbolo] - {'ε'})
                    if len(primeros[nt]) > antes:
                        cambio = True
                    
                    # Si no puede derivar ε, terminar
                    if 'ε' not in primeros[simbolo]:
                        puede_ser_vacio = False
                        break
                
                # Si todos pueden derivar ε, agregar ε a PRIMEROS(nt)
                if puede_ser_vacio:
                    if 'ε' not in primeros[nt]:
                        primeros[nt].add('ε')
                        cambio = True
    
    return primeros


def calcular_siguientes(gramatica, inicial, primeros):
    """Calcula el conjunto SIGUIENTES para cada no terminal"""
    siguientes = defaultdict(set)
    
    # Regla 1: $ en SIGUIENTES(S)
    siguientes[inicial].add('$')
    
    # Algoritmo iterativo de punto fijo
    cambio = True
    while cambio:
        cambio = False
        
        for nt in gramatica:
            for produccion in gramatica[nt]:
                for i, simbolo in enumerate(produccion):
                    # Solo nos interesan los no terminales
                    if simbolo not in gramatica:
                        continue
                    
                    # β = símbolos después de este
                    beta = produccion[i+1:]
                    
                    if beta:
                        # Calcular PRIMEROS(β)
                        primeros_beta = set()
                        todo_puede_ser_vacio = True
                        
                        for b in beta:
                            if b in primeros:
                                primeros_beta |= primeros[b]
                            else:
                                primeros_beta.add(b)
                            
                            if 'ε' not in primeros.get(b, {b}):
                                todo_puede_ser_vacio = False
                                break
                        
                        # Agregar PRIMEROS(β) - {ε}
                        antes = len(siguientes[simbolo])
                        siguientes[simbolo] |= (primeros_beta - {'ε'})
                        if len(siguientes[simbolo]) > antes:
                            cambio = True
                        
                        # Si todo β puede ser ε, agregar SIGUIENTES(nt)
                        if todo_puede_ser_vacio:
                            antes = len(siguientes[simbolo])
                            siguientes[simbolo] |= siguientes[nt]
                            if len(siguientes[simbolo]) > antes:
                                cambio = True
                    else:
                        # No hay β, agregar SIGUIENTES(nt)
                        antes = len(siguientes[simbolo])
                        siguientes[simbolo] |= siguientes[nt]
                        if len(siguientes[simbolo]) > antes:
                            cambio = True
    
    return siguientes


def calcular_primeros_cadena(cadena, primeros):
    """Calcula PRIMEROS de una cadena de símbolos"""
    resultado = set()
    
    for simbolo in cadena:
        if simbolo in primeros:
            resultado |= (primeros[simbolo] - {'ε'})
        else:
            resultado.add(simbolo)
        
        # Si no puede derivar ε, terminar
        if 'ε' not in primeros.get(simbolo, {simbolo}):
            return resultado
    
    # Si todos pueden derivar ε, agregar ε
    resultado.add('ε')
    return resultado


def calcular_prediccion(gramatica, primeros, siguientes):
    """Calcula el conjunto PREDICCIÓN para cada producción"""
    prediccion = {}
    
    for nt in gramatica:
        for produccion in gramatica[nt]:
            conjunto = set()
            
            # Calcular PRIMEROS(producción)
            primeros_prod = calcular_primeros_cadena(produccion, primeros)
            
            # Agregar PRIMEROS(producción) - {ε}
            conjunto |= (primeros_prod - {'ε'})
            
            # Si ε ∈ PRIMEROS(producción), agregar SIGUIENTES(nt)
            if 'ε' in primeros_prod:
                conjunto |= siguientes[nt]
            
            prediccion[(nt, tuple(produccion))] = conjunto
    
    return prediccion


def verificar_factorizacion_izquierda(gramatica, primeros):
    """Verifica si la gramática necesita factorización izquierda"""
    problemas = []
    
    for nt in gramatica:
        producciones = gramatica[nt]
        
        # Comparar cada par de producciones
        for i in range(len(producciones)):
            for j in range(i+1, len(producciones)):
                prod1 = producciones[i]
                prod2 = producciones[j]
                
                # Verificar si tienen el mismo primer símbolo
                if prod1 and prod2 and prod1[0] == prod2[0]:
                    problemas.append(
                        f"  {nt} -> {' '.join(prod1)} | {' '.join(prod2)}"
                    )
    
    return problemas


def verificar_recursion_izquierda(gramatica):
    """Detecta recursión izquierda directa"""
    problemas = []
    
    for nt in gramatica:
        for produccion in gramatica[nt]:
            if produccion and produccion[0] == nt:
                problemas.append(
                    f"  {nt} -> {' '.join(produccion)}"
                )
    
    return problemas


def imprimir_conjunto(nombre, conjunto, width=80):
    """Imprime un conjunto de forma legible"""
    print(f"\n{nombre}")
    print("="*width)
    
    for clave in sorted(conjunto.keys(), key=str):
        valores = sorted(conjunto[clave], key=lambda x: (x == '$', x == 'ε', x))
        valores_str = "{" + ", ".join(valores) + "}"
        print(f"  {str(clave):20} = {valores_str}")


def imprimir_prediccion(prediccion, width=80):
    """Imprime el conjunto PREDICCIÓN"""
    print(f"\nCONJUNTO PREDICCIÓN")
    print("="*width)
    
    for (nt, prod), conjunto in sorted(prediccion.items()):
        prod_str = ' '.join(prod)
        valores = sorted(conjunto, key=lambda x: (x == '$', x == 'ε', x))
        valores_str = "{" + ", ".join(valores) + "}"
        print(f"  PRED({nt:3} -> {prod_str:30}) = {valores_str}")


def main():
    """Función principal"""
    print("="*80)
    print(" CÁLCULO DE CONJUNTOS: PRIMEROS, SIGUIENTES Y PREDICCIÓN ".center(80, "="))
    print("="*80)
    
    if len(sys.argv) < 2:
        print("\n❌ Error: Debe proporcionar un archivo de gramática")
        print("Uso: python calcular_conjuntos.py gramatica.txt")
        return 1
    
    archivo = sys.argv[1]
    
    try:
        # Leer gramática
        gramatica, inicial = leer_gramatica(archivo)
        
        print(f"\n📄 Archivo: {archivo}")
        print(f"🔤 Símbolo inicial: {inicial}")
        
        # Mostrar gramática
        print(f"\n📐 GRAMÁTICA CARGADA")
        print("-"*80)
        for nt in sorted(gramatica.keys()):
            producciones = [' '.join(p) for p in gramatica[nt]]
            print(f"  {nt:5} -> {' | '.join(producciones)}")
        print("-"*80)
        
        # Identificar símbolos
        terminales, no_terminales = obtener_terminales_no_terminales(gramatica)
        print(f"\n📊 Terminales: {sorted(terminales)}")
        print(f"📊 No terminales: {sorted(no_terminales)}")
        
        # Verificar problemas
        print(f"\n🔍 VERIFICACIÓN DE LA GRAMÁTICA")
        print("-"*80)
        
        rec_izq = verificar_recursion_izquierda(gramatica)
        if rec_izq:
            print("⚠️  Recursión izquierda detectada:")
            for prob in rec_izq:
                print(prob)
        else:
            print("✅ Sin recursión izquierda directa")
        
        primeros = calcular_primeros(gramatica)
        fact_izq = verificar_factorizacion_izquierda(gramatica, primeros)
        if fact_izq:
            print("\n⚠️  Necesita factorización izquierda:")
            for prob in fact_izq:
                print(prob)
        else:
            print("✅ No necesita factorización izquierda")
        
        print("-"*80)
        
        # Calcular conjuntos
        siguientes = calcular_siguientes(gramatica, inicial, primeros)
        prediccion = calcular_prediccion(gramatica, primeros, siguientes)
        
        # Mostrar resultados
        imprimir_conjunto("CONJUNTO PRIMEROS", primeros)
        imprimir_conjunto("CONJUNTO SIGUIENTES", siguientes)
        imprimir_prediccion(prediccion)
        
        # Verificar si es LL(1)
        print(f"\n🎯 VERIFICACIÓN LL(1)")
        print("="*80)
        
        es_ll1 = True
        for nt in gramatica:
            producciones = gramatica[nt]
            conjuntos_pred = [prediccion[(nt, tuple(p))] for p in producciones]
            
            # Verificar intersección vacía entre producciones
            for i in range(len(conjuntos_pred)):
                for j in range(i+1, len(conjuntos_pred)):
                    interseccion = conjuntos_pred[i] & conjuntos_pred[j]
                    if interseccion:
                        es_ll1 = False
                        prod1 = ' '.join(producciones[i])
                        prod2 = ' '.join(producciones[j])
                        print(f"❌ Conflicto en {nt}:")
                        print(f"   {nt} -> {prod1}")
                        print(f"   {nt} -> {prod2}")
                        print(f"   Intersección: {interseccion}")
        
        if es_ll1:
            print("✅ La gramática es LL(1)")
        else:
            print("\n❌ La gramática NO es LL(1)")
        
        print("="*80)
        
    except FileNotFoundError:
        print(f"\n❌ Error: Archivo '{archivo}' no encontrado")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())