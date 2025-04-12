/**
 *
 **/
Ext._define('core.fields.DisplayDateField', {
    'extend': 'core.fields.DisplayDatetimeField',

    'xtype': 'displaydatefield',

    'constructor': function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                'format': 'd/m/Y'
            }
        );

        // this.callParent([cfg]);
        core.fields.DisplayDateField.superclass.constructor.call(this, cfg);
    }
});