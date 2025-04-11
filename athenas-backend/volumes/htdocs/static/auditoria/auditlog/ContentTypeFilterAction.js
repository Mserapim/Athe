Ext._define('auditoria.auditlog.ContentTypeFilterAction', {
    extend: 'core.fields.ComboField',

    constructor: function (cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                propertyName: 'content_type',
                rest: 'auditoria.auditlog.ContentTypeRestful',
                fieldLabel: 'Modelos',
                hiddenName: 'content',
                valueField: 'pk',
                emptyText: 'Informe o Modelo para filtrar',
                triggerAction: 'all',
                lazyRender: true,
                lazyInit: true,
                displayField: 'unicode',
                width: 200,
            }
        );

        auditoria.auditlog.ContentTypeFilterAction.superclass.constructor.call(this, cfg);

        var store = this.getStore();
        var all_groups = new Ext.data.Record({
            pk: 0,
            unicode: 'TODOS OS MODELOS',
        });

        store.on('load', function () {
            store.insert(0, all_groups);
            store.commitChanges();
        });

        var objToFilter = this.objToFilter;

        this.on({
            scope: this,
            select: {
                buffer: 1,
                fn: function (combo, record, index) {
                    if (record.data.pk === 0)
                        objToFilter.removeFilterProperty(cfg.propertyName, 800);
                    else
                        objToFilter.setFilterProperty(cfg.propertyName, record.data.pk, 800);
                }
            }
        });
    }
});
