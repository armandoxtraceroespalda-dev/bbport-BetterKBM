# bbport-ds3Controls
Controles de dark souls 3 para el port de pc de bloodborne "bbport" https://github.com/DarkIzuku/bloodborne_pc

Preparado para el port de Supermedo incluido en Bloodborne-Windows (1).zip.
Es un perfil con un pequeño complemento externo de controles. No es una
modificación del ejecutable del juego ni un mod para la carpeta mods.

INSTALACIÓN

1. Cierra el juego y cualquier launcher de Bloodborne que tengas abierto.
2. Extrae TODOS los archivos de este ZIP dentro de la carpeta donde está
   Bloodborne.exe. Allí deben quedar:

   Iniciar-Bloodborne-DS3.bat
   ds3_controls (carpeta con bridge.py, control_logic.py y profile.ini)
   LEEME.txt

3. Ejecuta Iniciar-Bloodborne-DS3.bat.
4. En la ventana del complemento, elige la RTX 4090 en la lista de GPU.
   La lista se rellena después de unos segundos y busca seleccionar la 4090
   automáticamente si no has heredado una selección BB_GPU_ID previa.
5. Pulsa "Abrir launcher con este perfil", configura tu juego normalmente y
   pulsa PLAY. Si ya tienes todo configurado, puedes usar "Jugar directamente".
6. Mantén abierto el complemento mientras juegas. Puedes minimizarlo.

No requiere instalar Python ni AutoHotkey: usa el Python incluido en el port.
La selección de GPU y el perfil se pasan al launcher y a sus procesos hijos.
Abre el launcher desde el complemento cada vez que quieras este mapeo.

CONTROLES

W / A / S / D               Moverse.
Ratón                       Cámara.
Clic izquierdo              Ataque ligero (R1).
Shift + clic izquierdo      Ataque fuerte (R2).
Mantener Shift + clic izq.   Ataque cargado: mantén el clic hasta soltarlo.
Clic derecho                Disparar / parry con arma de fuego (L2).
Ctrl izquierdo              Disparar / parry (alternativa).
Shift + clic derecho        Disparar / parry (alternativa).
F                           Transformar el arma (L1).
Espacio                     Esquivar / retroceder; mantener para correr.
Alt izquierdo               Caminar despacio mientras se mantiene.
E / Enter                   Interactuar / confirmar.
Q / clic central            Fijar objetivo / centrar cámara.
R                           Usar el objeto rápido seleccionado (Square).
C                           Usar vial de sangre (Triangle).
Rueda abajo                 Cambiar objeto rápido.
Rueda arriba                Crear balas de sangre (D-pad arriba; CONSUME VIDA).
Shift + rueda arriba        Cambiar arma derecha.
Shift + rueda abajo         Cambiar arma izquierda.
Flechas                     D-pad: arriba balas, abajo objetos, izq./der. armas.
Esc                         Menú del juego.
G                           Gestos.
Tab                         Efectos personales / lado derecho del touchpad.
Z                           Pulsación del stick izquierdo (L3).
Insert                      Menú de ajustes del port.
F7                          Activar/desactivar captura del ratón.
F8                          Recargar el perfil de controles.

La acción del clic se decide al presionarlo. Si empiezas un ataque cargado
con Shift + clic, soltar Shift antes que el clic no inicia un ataque ligero.
Al cambiar a otra ventana se liberan las teclas simuladas del ratón.
El mando, si lo conectas, conserva su mapeo habitual.

CORRECCIÓN DEL SPRINT (1.1)

El perfil mantiene la intensidad completa del movimiento en diagonal y hace
el giro de WASD en pasos breves, en vez de cambiar de dirección al instante.
Esto evita las condiciones que cortan el sprint al pasar de W a W+A, A+S,
etc. Usa stick_circular=off y stick_turn_rate=900.

stick_release_delay_ms=60 cubre pequeños huecos al soltar una dirección justo
antes de presionar la siguiente. Al soltar todas las teclas de movimiento,
puede mantener la última dirección hasta 60 ms adicionales. Espacio sigue
siendo el botón de carrera/esquiva; no se generan pulsaciones adicionales.

Si instalaste la versión 1.0, cierra juego y complemento y sobrescribe los
archivos al extraer esta versión. La corrección está en profile.ini.

DIFERENCIAS RESPECTO A DARK SOULS 3

Se reproduce su esquema de movimiento, ataque fuerte, interacción, objetos,
lock-on y cambio de armas, con adaptaciones para las acciones de Bloodborne:
- F transforma el arma, en vez de empuñarla a dos manos.
- C usa un vial de sangre; R sigue reservado al objeto rápido.
- El clic derecho dispara para hacer parry, en vez de bloquear.
- Bloodborne no tiene selección de hechizos: rueda arriba activa su acción
  de D-pad arriba, que crea balas de sangre y consume vida.

No se cambia la lógica de combate, de salto o de menús del juego. Por ejemplo,
el salto conserva el gesto de Bloodborne con el botón de carrera. En menús,
usa E/Enter para confirmar y Espacio/Retroceso para volver: Q sigue siendo R3
y no equivale a cancelar. No se añaden iconos de teclado a la interfaz.

La cámara usa el modo directo del port, disponible para el juego 1.09; otras
versiones usan la emulación de stick si el port no encuentra el código de cámara.
La sensibilidad se puede cambiar en ds3_controls/profile.ini, mediante
mouse_camera_sensitivity. Para el modo de stick, cambia mouse_camera a stick
y ajusta el segundo número de mouse_movement_params.

PERFIL Y DESINSTALACIÓN

El complemento usa ds3_controls/profile.ini mediante BB_INPUT_CONFIG.
Tu input.ini habitual no se sustituye. Evita reasignar controles desde la
pestaña Controls del launcher mientras usas este perfil: el launcher puede
guardar tus cambios en el propio profile.ini.

Para volver a tus controles anteriores, cierra juego y complemento y abre
Bloodborne.exe normalmente. Para quitar el complemento, elimina el BAT,
la carpeta ds3_controls y este LEEME. No cambia partidas guardadas.

SI ALGO NO FUNCIONA

- Debes iniciar el juego desde este complemento. Un launcher ya abierto o
  abierto desde otro acceso directo no hereda el perfil.
- Si no gira la cámara, pulsa F7 una vez para capturar el ratón.
- Los ataques del ratón solo se traducen cuando bb-probe.exe tiene el foco
  y Windows informa que el cursor está oculto. Esto evita ataques al clicar
  en otras aplicaciones, al recuperar el foco o usar el overlay del port.
- Abre complemento y juego con el mismo nivel de permisos. Normalmente no
  necesitas ejecutar ninguno como administrador.
- No uses a la vez otro programa que traduzca los mismos botones del ratón.
- No pulses F10, F11 o F12 manualmente: son las teclas internas de ataques.
- Si el complemento no abre, adjunta ds3_controls/error.log, si se creó.
- Si el port se actualiza y elimina o cambia --script o BB_INPUT_CONFIG,
  habrá que adaptar el complemento a esa versión.

VERIFICACIÓN Y ALCANCE

Se ha comprobado la lógica de combinaciones, ataques cargados, liberación de
teclas, cambio de arma con Shift + rueda y la estructura de datos de Windows.
El perfil se ha revisado con el formato y el lector de controles del proyecto.
No se ha ejecutado Bloodborne ni se han probado los hooks en un PC con Windows
durante la preparación. Esta versión necesita una primera prueba dentro del
juego para confirmar captura de ratón, inyección de teclas y comportamiento.

FUENTES

Mapeo de Dark Souls 3 (manual oficial de FromSoftware):
https://www.fromsoftware.jp/manual/darksouls3/win/operation_appendix.html

Formato de controles y funciones del port:
https://github.com/Supermedo/bloodborne_pc/blob/windows/docs/INPUT.md
https://github.com/Supermedo/bloodborne_pc/blob/windows/launcher/bbport_launcher_win.py

Los archivos Python incluidos son el código fuente del complemento.


