/**
 *
 **/

Ext._define('judicial.outcourtlawsuit.FilterLawsuitTypeWindow', {
    extend: 'judicial.outcourtlawsuit.FilterBaseWindow',

    width: 650,

    properties: [
        {stage: 1001, property: 'type_lawsuit'}
    ],

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 140,
                items: [
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Tipo',
                        name: 'type_lawsuit',
                        hiddenName: 'type_lawsuit',
                        choiceId: 'judicial.TYPE_LAWSUIT',
                        width: 475
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = (cfg || {});

        Ext.applyIf(
            cfg,
            {
                title: 'Filtrar por tipo de procedimento'
            }
        );

        judicial.outcourtlawsuit.FilterLawsuitTypeWindow.superclass.constructor.call(this, cfg);
        this.readFilters();
    }
});
