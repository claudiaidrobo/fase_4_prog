# Software FJ — Sistema Integral de Gestión

Aplicación de escritorio desarrollada en Python con Tkinter.  
Gestiona clientes, servicios y reservas para la empresa Software FJ,
aplicando POO completa y manejo robusto de excepciones.

# Integrantes

Claudia Alejandra Idrobo Montañez

## Requisitos

- Python 3.10 o superior  
- Tkinter (incluido en la instalación estándar de Python)  
- Sin dependencias externas

## Ejecución

```bash
python main.py
```

## Estructura del proyecto

```
software_fj/
├── core/               # Clases abstractas y de dominio
│   ├── entidad_base.py
│   ├── cliente.py
│   ├── servicio.py
│   ├── reserva.py
│   └── excepciones.py
├── servicios/          # Implementaciones concretas de Servicio
│   ├── reserva_sala.py
│   ├── alquiler_equipo.py
│   └── asesoria.py
├── ui/                 # Vistas Tkinter
│   ├── ventana_principal.py
│   ├── tab_clientes.py
│   ├── tab_servicios.py
│   ├── tab_reservas.py
│   ├── tab_simulacion.py
│   └── tab_logs.py
├── utils/              # Servicios transversales
│   ├── logger.py
│   ├── gestor.py
│   └── gestor_reservas.py
├── simulacion/         # Operaciones de prueba automáticas
│   └── simulacion.py
├── data/               # Archivos generados en ejecución
│   └── eventos.log
└── main.py
```

## Conceptos de POO aplicados

| Concepto | Dónde |
|---|---|
| Abstracción | `EntidadBase`, `Servicio` |
| Herencia | `Cliente`, `Reserva`, `ReservaSala`, `AlquilerEquipo`, `AsesoriaEspecializada` |
| Polimorfismo | `calcular_costo()` y `describir()` en cada servicio |
| Encapsulación | Name mangling `__atributo` + propiedades con setters validados |
| Excepciones personalizadas | `core/excepciones.py` — jerarquía propia |
| `try/except/else/finally` | `TabClientes`, `TabReservas`, `GestorReservas` |
| Encadenamiento (`raise X from Y`) | `GestorReservas.crear_reserva()`, `Reserva.confirmar()` |
| Registro en archivo de logs | `utils/logger.py` → `data/eventos.log` |
| Singleton | `Logger`, `Gestor` |