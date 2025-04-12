
/**
 *
 **/
Ext._define('judicial.params.judicialchoice.Grid', {
    extend: 'standard.ChoiceGrid',

    restWindow: 'judicial.params.judicialchoice.Window'
});

core.RestfulGrid.register(
    'judicial.params.judicialchoice.Restful',
    'judicial.params.judicialchoice.Grid'
);
