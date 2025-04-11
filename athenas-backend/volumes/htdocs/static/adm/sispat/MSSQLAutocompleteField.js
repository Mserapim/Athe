
Ext.ns('adm.sispat.fields');

adm.sispat.fields.MSSQLAutocompleteField = Ext.extend(
    Ext.form.ComboBox,
    {
        constructor: function(cfg) {
            cfg = cfg ? cfg : {};

            Ext.apply(
                cfg,
                {
                    store: new Ext.data.Store({
                        proxy: new Ext.data.HttpProxy({
                            url: cfg.dataUrl,
                            method: 'GET',
                            disableCaching: false,
                        }),
                        reader: new Ext.data.JsonReader({
                            totalProperty: 'count',
                            root: 'collection',
                            fields: ['pk', 'description']
                        })
                    }),
                    mode: 'remote',
                    hideTrigger: true,
                    triggerAction: 'all',
                    resizable: true
                }
            );

            adm.sispat.fields.MSSQLAutocompleteField.superclass.constructor.call(this, cfg);
        }
    }
);

Ext.reg('mssql-autocompletefield', adm.sispat.fields.MSSQLAutocompleteField);
