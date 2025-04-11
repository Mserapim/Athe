Ext._define('rh.raw.AutocompleteField', {
    extend: 'core.fields.AutocompleteField',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                fieldLabel: 'Não informado',
                allowBlank: true,
                rest: "core.Restful",
                name: 'nome',
                disabled: false
            }
        );
        rh.raw.AutocompleteField.superclass.constructor.call(this, cfg);
    },
});