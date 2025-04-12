Ext._define('judicial.parts.SuspendDeadlineWindow', {
    extend: 'judicial.PartLawsuitHandLess',

    rest: 'judicial.parts.SuspendDeadlineRestful',

    width: 900,

    actionTitle: 'Registro de Suspensão de Prazo',

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: []
            });

        return this._formPanel;
    },

});

judicial.PartLawsuitGrid.register('judicial.suspenddeadline', 'judicial.parts.SuspendDeadlineWindow');
