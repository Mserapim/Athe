
Ext._define('common.official_journal.filters.OriginDepartament', {
    extend: 'common.official_journal.filters.FilterWindow',

    width: 550,

    properties: [
        {stage: 104, property: 'department_origin'}
    ],


    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                labelWidth: 120,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        name: 'department_origin',
                        rest: 'rh.generalorgan.Restful',
                        fieldLabel: 'Local de envio'
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
                title: 'Filtrar por local de origem'
            }
        );

        common.official_journal.filters.OriginDepartament.superclass.constructor.call(this, cfg);
        this.readFilters();
    }

});
