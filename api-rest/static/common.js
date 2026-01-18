/** -Módulo común con funciones JavaScript compartidas entre vistas
 * 
 * Este archivo contiene utilidades reutilizables para todas las plantillas
 * del sistema de gestión de tareas.
 */

/** Alterna la visibilidad de un campo de contraseña entre texto plano y oculto.
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

/** Valida que las contraseñas coincidan antes de enviar el formulario.
 * 
 * 
 * Compara los valores de los campos password/new_password y confirm_password.
 * Muestra un mensaje de error si no coinciden.
 * Busca automáticamente el campo principal por ID 'password' o 'new_password'.
 * 
 * @returns {boolean} true si coinciden, false si no
 * 
 * @example
 * // HTML: <form onsubmit="return validatePassword()">
 * // <input id="password" type="password">
 * // <input id="confirm_password" type="password">
 * // <div id="password-error"></div>
 * validatePassword();
 */
function validatePassword() {
  // Buscar el campo principal (puede ser 'password' o 'new_password')
  var passwordField = document.getElementById('password') || document.getElementById('new_password');
  var confirmField = document.getElementById('confirm_password');
  var errorMsg = document.getElementById('password-error');
  
  if (!passwordField || !confirmField || !errorMsg) {
    return true; // Si no existen los elementos, dejar que el form se envíe
  }
  
  var password = passwordField.value;
  var confirm = confirmField.value;
  
  if (password !== confirm) {
    errorMsg.style.display = 'block';
    return false;
  }
  
  errorMsg.style.display = 'none';
  return true;
}
