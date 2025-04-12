
Ext._define('judicial.reminder.partlawsuit.Grid', {
    extend: 'judicial.reminder.Grid',

    restWindow: 'judicial.reminder.partlawsuit.Window'
});

core.RestfulGrid.register(
    'judicial.reminder.partlawsuit.Restful',
    'judicial.reminder.partlawsuit.Grid'
);
