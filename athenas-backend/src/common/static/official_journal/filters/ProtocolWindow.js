
Ext._define('common.official_journal.filters.ProtocolWindow', {
    extend: 'common.official_journal.filters.FilterWindow',

    width: 550,

    properties: [
        {stage: 107, property: 'protocol'}
    ],


    getFormPanel: function(cfg) {
        if(!this._formPanel)
        this._formPanel = Ext._create('Ext.form.FormPanel', {
            frame: true,
            border: false,
            items: [
                {
                    xtype: 'rest-autocompletefield',
                    name: 'protocol',
                    rest: 'edocs.protocolo.ProtocoloRestful',
                    fieldLabel: 'Protocolo',
                    width: 400,
                    allowBlank: false,
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
                title: 'Filtrar por protocolo'
            }
        );

        common.official_journal.filters.ProtocolWindow.superclass.constructor.call(this, cfg);
        // this.readFilters();

    }

});
