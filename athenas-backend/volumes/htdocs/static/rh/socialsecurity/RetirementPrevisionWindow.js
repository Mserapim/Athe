Ext._define('rh.socialsecurity.RetirementPrevisionWindow', {
    extend: 'core.RestfulWindow',

    rest: 'rh.socialsecurity.RetirementPrevisionRestful',
    width: 500,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                {
                    xtype: 'displayfield',
                    fieldLabel: 'Contribuinte',
                    name: 'natural_person_unicode',
                },
                {
                    xtype: 'checkbox',
                    fieldLabel: '&nbsp;',
                    labelSeparator: '&nbsp;',
                    boxLabel: 'Negativa de vínculo anterior',
                    allowBlank: true,
                    name: 'negative_previous_bond'
                },
            ]
            });

        return this._formPanel;
    }
});
