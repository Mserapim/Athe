Ext._define('raf.subitem.CalculateWindow', {
    extend: 'core.RestfulWindow',

    rest: 'raf.subitem.CalculateRestful',

    width: 500,

    getFromSumField: function(cfg) {
        if(!this._fromSumField)
            this._fromSumField = Ext._create('core.fields.AutocompleteField', {
                    xtype: "rest-autocompletefield",
                    fieldLabel: "Para cálculo",
                    allowBlank: false,
                    rest: "raf.subitem.Restful",
                    name: "from_the_sum",
                    gridConfig: {
                        columnAction: false
                    },
                    preFilter: [
                        {property: 'quiz__subitem', value: cfg.params.subitem !== undefined ? cfg.params.subitem : null, stage: 100},
                        {property: 'pk', value: cfg.params.subitem !== undefined ? cfg.params.subitem : null, stage: -100},
                        {property: 'for_calculation__subitem', value: cfg.params.subitem !== undefined ? cfg.params.subitem : null, stage: -101},
                    ]
                });

        return this._fromSumField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getFromSumField(cfg),
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Afetar',
                        hiddenName: 'affectation',
                        width: 200,
                        choiceId: 'raf.AFFECTATION',
                    },
                    {
                        xtype: 'checkbox',
                        name: 'previous_month',
                        fieldLabel: 'Mês Anteior',
                        checked: false
                    },
                ]
            });

        return this._formPanel;
    }
});
