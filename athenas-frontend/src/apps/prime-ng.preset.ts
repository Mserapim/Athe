import { definePreset } from '@primeng/themes';
import Aura from '@primeng/themes/aura';
import { palette } from '@primeng/themes';

const royalBlue = palette('#276ca9');

export const PRIME_NG_THEME = definePreset(Aura, {
    primitive: {
        royalBlue
    },
    semantic: {
        primary: {
            50: '{royalBlue.50}',
            100: '{royalBlue.100}',
            200: '{royalBlue.200}',
            300: '{royalBlue.300}',
            400: '{royalBlue.400}',
            500: '{royalBlue.500}',
            600: '{royalBlue.600}',
            700: '{royalBlue.700}',
            800: '{royalBlue.800}',
            900: '{royalBlue.900}',
            950: '{royalBlue.950}'
        }
    }
}); 