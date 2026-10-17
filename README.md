# bbport-BetterKBM
Controles de dark souls 3 de teclado y mouse (kbm) para el port de pc de bloodborne creado por [deadinside28](https://github.com/deadinside28) PERO preparado para el fork de Supermedo https://github.com/Supermedo/bloodborne_pc  (USAR ESTE ULTIMO)

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
4. En la ventana del complemento, elige tu gpu en la lista de GPU.
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

Para volver a tus controles anteriores, cierra juego y complemento y abre
Bloodborne.exe normalmente. Para quitar el complemento, elimina el BAT,
la carpeta ds3_controls y este LEEME. No cambia partidas guardadas.


Formato de controles y funciones del port:
https://github.com/Supermedo/bloodborne_pc/blob/windows/docs/INPUT.md
https://github.com/Supermedo/bloodborne_pc/blob/windows/launcher/bbport_launcher_win.py

Los archivos Python incluidos son el código fuente del complemento.


