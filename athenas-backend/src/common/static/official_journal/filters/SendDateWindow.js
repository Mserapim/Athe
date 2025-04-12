
Ext._define('common.official_journal.filters.SendDateWindow', {
    extend: 'common.official_journal.filters.FilterWindow',

    width: 245,

    properties: [
        {stage: 105, property: 'send_date__gte'},
        {stage: 106, property: 'send_date__lte'}
    ],


    getFormPanel: function(cfg) {
        if(!this._formPanel)
        this._formPanel = Ext._create('Ext.form.FormPanel', {
            frame: true,
            border: false,
            items: [
                {
                    xtype: 'datefield',
                    name: 'send_date__gte',
                    fieldLabel: 'Data início',
                    allowBlank: false,
                    format: 'd/m/Y'
                },
                {
                    xtype: 'datefield',
                    name: 'send_date__lte',
                    fieldLabel: 'Data fim',
                    allowBlank: false,
                    format: 'd/m/Y'
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
                title: 'Filtrar por data de encaminhamento'
            }
        );

        common.official_journal.filters.SendDateWindow.superclass.constructor.call(this, cfg);
        this.readFilters();

    }

});
