/**
 * Módulo común con funciones JavaScript compartidas entre vistas
 * 
 * Este archivo contiene utilidades reutilizables para todas las plantillas
 * del sistema de gestión de tareas.
 */

/**
 * Alterna la visibilidad de un campo de contraseña entre texto plano y oculto.
 * 
 * Cambia el tipo del input entre 'password' y 'text', y actualiza el icono
 * del ojo para indicar el estado actual (👁️ = oculto, 🙈 = visible).
 * 
 * @param {string} inputId - ID del elemento input de contraseña a modificar
 * @param {HTMLElement} icon - Elemento DOM del icono que se actualizará
 * 
 * @example
 * // HTML: <input id="password" type="password">
 * // <span onclick="togglePasswordVisibility('password', this)">👁️</span>
 * togglePasswordVisibility('password', iconElement);
 */
function togglePasswordVisibility(inputId, icon) {
  var input = document.getElementById(inputId);
  if (input.type === 'password') {
    input.type = 'text';
    icon.textContent = '🙈';
  } else {
    input.type = 'password';
    icon.textContent = '👁️';
  }
}
