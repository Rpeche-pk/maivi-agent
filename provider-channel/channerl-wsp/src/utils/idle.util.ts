import {timeoutFlow} from "@/flow/exit_flow/exit.flow";
import {log_warning} from "./logger.util";
import {BotContext as Context} from "@builderbot/bot/dist/types";

const timers : any = {};
const activeTimers = new Set();

export function idleStart(ctx: Context, gotoFlow:any, time:number) {
    const userId = ctx.from;

    if (activeTimers.has(userId)) {
        return;
    }

    log_warning(`[STARTED - IDLESTART] cuenta atrás para el usuario ${userId}!`);

    activeTimers.add(userId);
    timers[userId] = setTimeout(() => {
        if (activeTimers.has(userId)) {
            log_warning(`¡Tiempo agotado para el usuario ${userId}!`);
            activeTimers.delete(userId);
            delete timers[userId];
            return gotoFlow(timeoutFlow);
        }
    }, time);
}

export function idleReset(ctx:Context, gotoFlow :any, time :number) {
    const userId = ctx.from;
    idleStop(ctx);
    if (timers[userId]) {
        log_warning(`[RESTART - IDLERESET] cuenta atrás para el usuario ${userId}!`);
        clearTimeout(timers[userId]);
        delete timers[userId];
    }

    idleStart(ctx, gotoFlow, time);
}

export function idleStop(ctx:Context) {
    const userId = ctx.from;
    log_warning(`[STOP - IDLESTOP] cuenta atrás para el usuario ${userId}!`);

    if (timers[userId]) {
        clearTimeout(timers[userId]);
        delete timers[userId];
    }
    activeTimers.delete(userId);
}

// Función para limpiar timers huérfanos (opcional, puede llamarse periódicamente)
export function cleanupTimers() {
    for (const userId in timers) {
        clearTimeout(timers[userId]);
        delete timers[userId];
    }
    activeTimers.clear();
}
