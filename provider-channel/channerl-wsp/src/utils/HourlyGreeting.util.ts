import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc.js';
import timezone from 'dayjs/plugin/timezone.js';
import isBetween from 'dayjs/plugin/isBetween.js';
import customParseFormat from 'dayjs/plugin/customParseFormat.js';
import {log_error} from "@/utils/logger.util";
dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.extend(isBetween);
dayjs.extend(customParseFormat);

const TIME_ZONE = 'America/Lima';

const TIME_RANGES = {
    EARLY_MORNING: {
        start: '00:00',
        end: '06:00',
        greetings: [
            "*El que madruga Dios lo ayuda* ✨",
            "*Buena Amanecida* ☕",
            "*¡Buen amanecer!* 🌅"
        ]
    },
    MORNING: {
        start: '06:00',
        end: '12:00',
        greetings: [
            "*Buenos Días* 🌤",
            "*¡Hola, buen día!* 🌞",
            "*Saludos matutinos* ☀️",
            "*¡Que tengas un excelente día!* 🌅"
        ]
    },
    AFTERNOON: {
        start: '12:00',
        end: '18:00',
        greetings: [
            "*Saludos vespertinos* 🌅",
            "*Buenas Tardes* ⛅",
            "*¡Hola, buenas tardes!* 🌤"
        ]
    },
    EVENING: {
        start: '18:00',
        end: '23:59',
        greetings: [
            "*¡Buenas Noches!* 🌌",
            "*Buenas Noches* 🌚",
            "*¡Buenas noches!* 🌙",
            "*Que tengas una excelente noche* ✨"
        ]
    }
};

export const randomGreeting = () => {
    try {
        const currentTime = dayjs().tz(TIME_ZONE);

        const currentRange = Object.values(TIME_RANGES).find(range => {
            const start = dayjs(`${currentTime.format('YYYY-MM-DD')} ${range.start}`);
            const end = dayjs(`${currentTime.format('YYYY-MM-DD')} ${range.end}`);
            return currentTime.isBetween(start, end, null, '[]');
        });

        if (!currentRange) {
            return "*¡Hola!* 👋";
        }

        return currentRange.greetings

    } catch (error) {
        log_error('Error al generar saludo:', {error: error instanceof Error ? {name: error.name, message: error.message, stack: error.stack} : error});
        return "*¡Hola!* 👋";
    }
};
