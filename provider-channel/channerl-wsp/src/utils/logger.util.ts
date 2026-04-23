import chalk from 'chalk';

/**
 * Registra un mensaje de éxito.
 * @param {string} message - El mensaje principal.
 * @param {Object} [details] - Detalles adicionales opcionales.
 */
export function log_success(message:any, details = {}) {
    const log_date = formatLogDate();
    console.log(`[${log_date}]`,chalk.green('✔ ÉXITO:'), chalk.green.bold(message));
    if (Object.keys(details).length > 0) {
        console.log(`[${log_date}]`,chalk.green('  Detalles:'), chalk.white(JSON.stringify(details)));
    }
}

/**
 * Registra un mensaje de error.
 * @param {string} message - El mensaje principal de error.
 * @param {Error|Object} [error] - El objeto de error o detalles adicionales.
 */
export function log_error(message:any, error = {}) {
    const logDate = formatLogDate();
    console.log(`[${logDate} ]`,chalk.red('✖ ERROR:'), chalk.red.bold(message));
    if (error instanceof Error) {
        console.log(`[${logDate}]`,chalk.red('  Detalles del error:'));
        console.log(`[${logDate}]`,chalk.red(`    Nombre: ${error.name}`));
        console.log(`[${logDate}]`,chalk.red(`    Mensaje: ${error.message}`));
        if (error.stack) {
            console.log(`[${logDate}]`,chalk.red('  Stack:'));
            console.log(`[${logDate}]`,chalk.red(error.stack.split('\n').map(line => `    ${line}`).join('\n')));
        }
    } else if (Object.keys(error).length > 0) {
        console.log(`[${logDate}]`,chalk.red('  Detalles adicionales:'), chalk.white(JSON.stringify(error)));
    }
}

/**
 * Registra un mensaje de advertencia.
 * @param {string} message - El mensaje principal de advertencia.
 * @param {Object} [details] - Detalles adicionales opcionales.
 */
export function log_warning(message:any, details = {}) {
    const logDate = formatLogDate();
    console.log(`[${logDate} ]`,chalk.yellow('⚠ ADVERTENCIA:'), chalk.yellow.bold(message));
    if (Object.keys(details).length > 0) {
        console.log(chalk.yellow('  Detalles:'), chalk.white(JSON.stringify(details)));
    }
}

function formatLogDate () {
    const now = new Date();
    return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}:${String(now.getMilliseconds()).padStart(3, '0')}`
}
