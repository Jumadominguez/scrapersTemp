# Carpeta Sandbox para Scripts Temporales

Esta carpeta funciona como un **sandbox** para todos los scripts temporales, de testing, debugging y modificaciones situacionales que no son parte permanente de la plataforma.

## Propósito

- **Scripts de testing**: Archivos para probar funcionalidades específicas
- **Scripts de debugging**: Herramientas temporales para diagnosticar problemas
- **Scripts de modificación**: Scripts para hacer cambios puntuales en la base de datos o configuración
- **Scripts situacionales**: Cualquier script que no sea necesario mantener en el repositorio principal

## Reglas de uso

1. **Archivos temporales**: Todos los scripts aquí son temporales y pueden ser eliminados
2. **No commitear**: Esta carpeta está en `.gitignore`, así que los archivos no se suben al repositorio
3. **Documentación**: Si creas un script complejo, agrega comentarios explicando su propósito
4. **Limpieza**: Elimina los scripts cuando ya no sean necesarios

## Estructura actual

```
temp/
├── db-scripts/          # Scripts para modificar la base de datos
├── test-scripts/        # Scripts de testing
├── debug-scripts/       # Scripts de debugging
├── migration-scripts/   # Scripts de migración
├── utils/              # Utilidades temporales
└── README.md           # Esta documentación
```
Nota: Si se necesita crear un script temporal que no se encuentra dentro de estas categorias, crear la carpeta.

## Algunos ejemplos de uso

- Scripts para poblar datos de prueba
- Scripts para limpiar colecciones específicas
- Scripts para verificar integridad de datos
- Scripts para testing de APIs
- Scripts para debugging de errores específicos

## Importante

Los scripts en esta carpeta **NO** son parte de la plataforma principal y pueden ser eliminados en cualquier momento. Si un script se vuelve necesario permanentemente, debe ser movido a la ubicación apropiada en el proyecto.
