Ext._define('judicial.parts.ResumeDeadlineWindow', {
    extend: 'judicial.PartLawsuitHandLess',

    rest: 'judicial.parts.ResumeDeadlineRestful',

    width: 900,

    actionTitle: 'Reestabelecer o Prazo',

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: []
            });

        return this._formPanel;
    },

});

judicial.PartLawsuitGrid.register('judicial.resumedeadline', 'judicial.parts.ResumeDeadlineWindow');
