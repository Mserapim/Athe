
Ext._define('judicial.reminder.lawsuit.Grid', {
    extend: 'judicial.reminder.Grid',

    restWindow: 'judicial.reminder.lawsuit.Window'
});

core.RestfulGrid.register(
    'judicial.reminder.lawsuit.Restful',
    'judicial.reminder.lawsuit.Grid'
);
