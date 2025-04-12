
Ext._define('edocs.protocolo.filters.SendDateWindow', {
    extend: 'edocs.protocolo.filters.FilterWindow',

    width: 245,

    prepareFilterValue: function(property, value) {
        if(property.indexOf('__gte') >= 0)
            value += ' 00:00';
        else if(property.indexOf('__lte') >= 0)
            value += ' 23:59';

        return value;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    {
                        xtype: 'datefield',
                        name: 'data_encaminhamento__gte',
                        fieldLabel: 'Data início',
                        allowBlank: false
                    },
                    {
                        xtype: 'datefield',
                        name: 'data_encaminhamento__lte',
                        fieldLabel: 'Data fim',
                        allowBlank: false
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Selecionar origem do documento'
            }
        );

        edocs.protocolo.filters.SendDateWindow.superclass.constructor.call(this, cfg);
    }
});
