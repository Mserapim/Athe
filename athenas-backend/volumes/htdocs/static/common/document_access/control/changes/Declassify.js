Ext._define('common.document_access.control.changes.Declassify', {
    extend: 'common.document_access.control.changes.BaseJustification',

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.apply(cfg, {
            action: 'declassify',
        });
        Ext.applyIf(cfg, {});

        common.document_access.control.changes.Declassify.superclass.constructor.call(this, cfg);
    }
});
