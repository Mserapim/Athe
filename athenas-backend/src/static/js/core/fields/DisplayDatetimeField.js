/**
 *
 **/
Ext._define('core.fields.DisplayDatetimeField', {
    'extend': 'Ext.form.TextField',

    'xtype': 'displaydatetimefield',

    'setValue': function(value) {
        if(value instanceof Date)
            value = Ext.util.Format.date(value, this.format);

        core.fields.DisplayDatetimeField.superclass.setValue.call(this, value);
    },

    'constructor': function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                'format': 'd/m/Y H:i:s'
            }
        );

        Ext.apply(
            cfg,
            {
                'readonly': true,
                disabled: true
            }
        );

        // this.callParent([cfg]);
        core.fields.DisplayDatetimeField.superclass.constructor.call(this, cfg);
    }
});
