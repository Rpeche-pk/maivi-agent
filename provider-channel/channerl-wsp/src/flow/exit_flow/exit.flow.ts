import { addKeyword, EVENTS } from '@builderbot/bot'
import { JsonFileDB as Database } from '@builderbot/database-json'
import { BaileysProvider as Provider } from '@builderbot/provider-baileys'
import {idleStop} from "@/utils/idle.util";
import { log_error } from '@/utils/logger.util';


export const timeoutFlow = addKeyword<Provider,Database>(EVENTS.ACTION, {})
    .addAction(async (ctx, { extensions, flowDynamic, endFlow }) => {
        try {
            const jid = ctx?.key?.remoteJid;

            
            await flowDynamic("❌ Se ha agotado el tiempo de respuesta ❌");

            idleStop(ctx);
            return endFlow();
        } catch (e) {
            const err = e instanceof Error ? e : new Error(String(e));
            log_error("Error en el flujo timeoutFlow", err)
        }
    });