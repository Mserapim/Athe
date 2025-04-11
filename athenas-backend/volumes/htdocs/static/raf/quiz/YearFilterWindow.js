
Ext._define('raf.quiz.YearFilterWindow', {
    extend: 'raf.quiz.FilterBaseWindow',

    width: 650,

    properties: [
        {stage: 1000, property: 'yearbase'}
    ],

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 120,
                items: [
                    {
                        name: 'yearbase',
                        fieldLabel: 'Ano Base',
                        xtype: 'rest-autocompletefield',
                        rest: 'raf.yearbase.Restful'
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
                title: 'Filtrar por Ano Base'
            }
        );

        raf.quiz.YearFilterWindow.superclass.constructor.call(this, cfg);
        this.readFilters();
    }
});
